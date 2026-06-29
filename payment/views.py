from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from django.contrib import messages
from .forms import PaymentForm
from payment.forms import ShippingForm
from payment.models import Shippingaddr, Order, Orderitem, OrderView
from django.contrib.auth.models import User
from customers.models import Product
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
import datetime
import json
import requests
import uuid

# Import notification function
from payment.signals import notify_admin_new_order


def is_admin(user):
    return user.is_superuser


def verify_flutterwave_payment(tx_id):
    """Verify a transaction server-side with Flutterwave before creating an order."""
    try:
        url = f"https://api.flutterwave.com/v3/transactions/{tx_id}/verify"
        headers = {
            "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        return data

    except Exception:
        return None


@login_required
@user_passes_test(is_admin)
def not_shipped_dash(request):
    if request.POST:
        num = request.POST.get('num')

        if num:
            Order.objects.filter(id=num).update(
                shipped=True,
                date_shipped=timezone.now()
            )
            messages.success(request, "Shipping Status Changed")

    orders = Order.objects.filter(shipped=False).order_by('-order_date')

    return render(request, 'payment/not_shipped.html', {
        "orders": orders
    })


@login_required
@user_passes_test(is_admin)
def shipped_dash(request):
    if request.POST:
        num = request.POST.get('num')

        if num:
            Order.objects.filter(id=num).update(
                shipped=False,
                date_shipped=None
            )
            messages.success(request, "Shipping Status Changed")

    orders = Order.objects.filter(shipped=True).order_by('-date_shipped')

    return render(request, 'payment/shipped.html', {
        "orders": orders
    })


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = get_object_or_404(Order, id=pk)
        items = Orderitem.objects.filter(order=pk)

        if request.POST:
            status = request.POST.get('shipping_status')

            if status == "true":
                Order.objects.filter(id=pk).update(
                    shipped=True,
                    date_shipped=timezone.now()
                )
            else:
                Order.objects.filter(id=pk).update(
                    shipped=False,
                    date_shipped=None
                )

            messages.success(request, "Shipping Status Changed")
            order = get_object_or_404(Order, id=pk)

        return render(request, 'payment/ordered.html', {
            "order": order,
            "items": items
        })

    else:
        messages.error(request, "Access Denied")
        return redirect('home')


def track(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(customer=request.user).order_by('-order_date')

        order_items = []

        for order in orders:
            items = Orderitem.objects.filter(order=order)
            order_items.append({
                "order": order,
                "items": items
            })

        OrderView.objects.update_or_create(
            user=request.user,
            defaults={'last_seen': timezone.now()},
        )

        return render(request, 'payment/track.html', {
            "orders": order_items
        })

    else:
        messages.error(request, "Access Denied")
        return redirect('home')


def checkout(request):
    try:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        request.session['my_shipping'] = {
            'name': request.POST.get('name', ''),
            'shipping_address': request.POST.get('shipping_address', ''),
            'shipping_city': request.POST.get('shipping_city', ''),
            'shipping_state': request.POST.get('shipping_state', ''),
            'shipping_country': request.POST.get('shipping_country', ''),
            'shipping_phone_number': request.POST.get('shipping_phone_number', ''),
            'shipping_email': request.POST.get('shipping_email', ''),
        }

        request.session.modified = True

        my_shipping = request.session['my_shipping']
        order_name = my_shipping['name']
        order_email = my_shipping['shipping_email']

        return render(request, 'payment/checkout.html', {
            "order_name": order_name,
            "order_email": order_email,
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
        })

    except Exception:
        import traceback
        traceback.print_exc()
        return redirect('shipping')


def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        if request.user.is_authenticated:
            billing_form = PaymentForm()

            # Generate a unique transaction reference from the server
            tx_ref = f"MDF-{uuid.uuid4().hex[:12]}"

            # Save the transaction reference and amount in session
            # This helps us confirm the payment later
            request.session['flutterwave_tx_ref'] = tx_ref
            request.session['flutterwave_amount'] = str(totals)
            request.session.modified = True

            return render(request, 'payment/billing_info.html', {
                "cart_products": cart_products,
                "quantities": quantities,
                "totals": totals,
                "billing_form": billing_form,

                # Flutterwave values for the template
                "flutterwave_public_key": settings.FLUTTERWAVE_PUBLIC_KEY,
                "flutterwave_redirect_url": settings.FLUTTERWAVE_REDIRECT_URL,
                "tx_ref": tx_ref,
            })

        else:
            messages.error(request, "You have to be logged in to place orders.")
            return redirect('home')

    else:
        messages.error(request, "Something went wrong.")
        return redirect('home')


def process_order(request):
    cart = Cart(request)
    cart_products = list(cart.get_prods)
    quantities = cart.get_quants
    totals = cart.cart_total()

    # ── 1. Verify payment with Flutterwave before creating order ──────────

    tx_id = None
    flw_status = None
    tx_ref = None

    # Flutterwave usually redirects with these GET parameters:
    # ?status=successful&tx_ref=...&transaction_id=...
    if request.GET:
        tx_id = request.GET.get('transaction_id')
        flw_status = request.GET.get('status')
        tx_ref = request.GET.get('tx_ref')

    # Fallback for your old response format
    response_raw = request.GET.get('response')

    if response_raw:
        try:
            payment_data = json.loads(response_raw)
            tx_id = payment_data.get('id')
            flw_status = payment_data.get('status')
            tx_ref = payment_data.get('tx_ref')

        except (json.JSONDecodeError, KeyError, TypeError):
            messages.error(request, "Invalid payment response.")
            return redirect('checkout')

    if not tx_id:
        messages.error(request, "No payment transaction was found.")
        return redirect('checkout')

    if flw_status != 'successful':
        messages.error(request, "Payment was not successful. Please try again.")
        return redirect('checkout')

    saved_tx_ref = request.session.get('flutterwave_tx_ref')

    if saved_tx_ref and tx_ref and saved_tx_ref != tx_ref:
        messages.error(request, "Payment reference mismatch. Please contact support.")
        return redirect('checkout')

    verification_data = verify_flutterwave_payment(tx_id)

    if not verification_data:
        messages.error(request, "Payment could not be verified. Please contact support.")
        return redirect('checkout')

    payment_info = verification_data.get('data', {})

    verified_status = payment_info.get('status')
    verified_amount = payment_info.get('amount')
    verified_currency = payment_info.get('currency')
    verified_tx_ref = payment_info.get('tx_ref')

    if verified_status != 'successful':
        messages.error(request, "Payment verification failed.")
        return redirect('checkout')

    if verified_currency != 'NGN':
        messages.error(request, "Invalid payment currency.")
        return redirect('checkout')

    if str(verified_tx_ref) != str(saved_tx_ref):
        messages.error(request, "Payment reference could not be confirmed.")
        return redirect('checkout')

    try:
        if float(verified_amount) != float(totals):
            messages.error(request, "Payment amount does not match your order total.")
            return redirect('checkout')
    except (TypeError, ValueError):
        messages.error(request, "Payment amount could not be confirmed.")
        return redirect('checkout')

    # ── 2. Retrieve shipping from session ─────────────────────────────────

    my_shipping = request.session.get('my_shipping')

    if not my_shipping:
        messages.error(
            request,
            "Session expired. Please re-enter your shipping details."
        )
        return redirect('shipping')

    order_name = my_shipping['name']
    order_email = my_shipping['shipping_email']
    order_phone_number = my_shipping['shipping_phone_number']

    order_address = (
        f"{my_shipping['shipping_address']}\n"
        f"{my_shipping['shipping_city']}\n"
        f"{my_shipping['shipping_state']}\n"
        f"{my_shipping['shipping_country']}"
    )

    amount_paid = totals

    # ── 3. Create order ───────────────────────────────────────────────────

    if request.user.is_authenticated:
        user = request.user

        create_order = Order(
            customer=user,
            order_name=order_name,
            order_email=order_email,
            order_phone_number=order_phone_number,
            order_address=order_address,
            amount_paid=amount_paid,
        )

        create_order.save()
        order_id = create_order.pk

        # Create order items before sending notification
        for product in cart_products:
            product_id = product.product_id
            price = product.sale_price if product.is_sale else product.price

            for key, value in quantities.items():
                if int(key) == product.product_id:
                    Orderitem(
                        order_id=order_id,
                        customer=user,
                        product_id=product_id,
                        quantity=value,
                        price=price,
                    ).save()

        # Send email/push notification after order items have been created
        notify_admin_new_order(create_order)

        # Clear cart, shipping, and Flutterwave session data
        request.session.pop('session_key', None)
        request.session.pop('my_shipping', None)
        request.session.pop('flutterwave_tx_ref', None)
        request.session.pop('flutterwave_amount', None)
        request.session.modified = True

        messages.success(request, "Order Placed Successfully!")
        return redirect('home')

    else:
        messages.error(request, "You must be logged in to complete an order.")
        return redirect('signin')