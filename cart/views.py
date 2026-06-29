# cart/views.py

from decimal import Decimal

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .cart import Cart
from customers.models import Product


def money_to_json(value):
    """
    Converts Decimal money values to a clean float for JavaScript.
    """
    if isinstance(value, Decimal):
        return float(value)
    return float(value or 0)


def cart_summary(request):
    cart = Cart(request)
    cart_items = cart.get_items()
    totals = cart.cart_total()

    return render(request, 'cart_summary.html', {
        'cart_items': cart_items,
        'totals': totals,
        'cart_count': cart.distinct_count(),
    })


def cart_add(request):
    cart = Cart(request)

    if request.method != 'POST' or request.POST.get('action') != 'post':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    product_id = request.POST.get('product_id')
    product_qty = request.POST.get('product_qty', 1)

    if not product_id or not str(product_id).isdigit():
        return JsonResponse({'error': 'Invalid product id'}, status=400)

    try:
        product_qty = int(product_qty)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid quantity'}, status=400)

    if product_qty < 1:
        return JsonResponse({'error': 'Invalid quantity'}, status=400)

    product = get_object_or_404(Product, product_id=product_id)

    added = cart.add(product=product, quantity=product_qty)

    if not added:
        return JsonResponse({'error': 'Could not add product to cart'}, status=400)

    messages.success(request, "Product added to cart")

    return JsonResponse({
        'success': True,
        'product_id': str(product_id),
        'quantity': cart.get_quantity(product_id),
        'cart_count': cart.distinct_count(),
        'cart_total': money_to_json(cart.cart_total()),
    })


def cart_update(request):
    """
    Handles increment and decrement buttons.

    increment:
        current quantity + 1

    decrement:
        current quantity - 1

    If quantity becomes 0, product is removed from cart.
    """
    cart = Cart(request)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    action = request.POST.get('action')
    product_id = request.POST.get('product_id')

    if action not in ('increment', 'decrement'):
        return JsonResponse({'error': 'Invalid action'}, status=400)

    if not product_id or not str(product_id).isdigit():
        return JsonResponse({'error': 'Invalid product id'}, status=400)

    current_qty = cart.get_quantity(product_id)

    if current_qty < 1:
        return JsonResponse({'error': 'Product not in cart'}, status=404)

    product = get_object_or_404(Product, product_id=product_id)
    unit_price = product.sale_price if product.is_sale else product.price

    if action == 'increment':
        new_qty = current_qty + 1
    else:
        new_qty = current_qty - 1

    updated = cart.update(product_id=product_id, quantity=new_qty)

    if not updated:
        return JsonResponse({'error': 'Could not update cart'}, status=400)

    removed = new_qty < 1
    item_subtotal = Decimal('0.00') if removed else unit_price * new_qty

    return JsonResponse({
        'success': True,
        'removed': removed,
        'product_id': str(product_id),
        'quantity': max(new_qty, 0),
        'item_subtotal': money_to_json(item_subtotal),
        'cart_total': money_to_json(cart.cart_total()),
        'cart_count': cart.distinct_count(),
    })


def cart_delete(request):
    cart = Cart(request)

    if request.method != 'POST' or request.POST.get('action') != 'post':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    product_id = request.POST.get('product_id')

    if not product_id or not str(product_id).isdigit():
        return JsonResponse({'error': 'Invalid product id'}, status=400)

    deleted = cart.delete(product_id=product_id)

    if not deleted:
        return JsonResponse({'error': 'Product not in cart'}, status=404)

    return JsonResponse({
        'success': True,
        'removed': True,
        'product_id': str(product_id),
        'cart_total': money_to_json(cart.cart_total()),
        'cart_count': cart.distinct_count(),
    })