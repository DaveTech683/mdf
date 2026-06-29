# customer/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Product, Customer, Category, Subscriber, Color, Size  # removed Order
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from payment.forms import ShippingForm
from payment.models import Shippingaddr
from .forms import SignUpForm, LetterForm
from django.core.mail import send_mail
from django.conf import settings
from random import sample
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_GET, require_POST
from .models import PushSubscription


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_admin(user):
    """Test function used by @user_passes_test to restrict admin views."""
    return user.is_superuser


def _handle_newsletter(request, form):
    """
    Newsletter subscription logic extracted into a single helper to keep
    things DRY. Call it with the bound LetterForm and it saves the subscriber
    or shows the right message.
    """
    if form.is_valid():
        instance = form.save(commit=False)
        if Subscriber.objects.filter(email=instance.email).exists():
            messages.success(request, "You Already Subscribed")
        else:
            instance.save()
            messages.success(request, "You have Successfully Subscribed")


# ---------------------------------------------------------------------------
# Public views
# ---------------------------------------------------------------------------

def contact(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        sender_mail = request.POST.get('mail')

        if subject and message and sender_mail:
            try:
                # Sends to EMAIL_HOST_USER as the support inbox.
                # SUPPORT_EMAIL can be added to settings.py to override this.
                support_email = getattr(settings, 'SUPPORT_EMAIL', settings.EMAIL_HOST_USER)
                send_mail(
                    subject,
                    f"Message from {sender_mail}:\n\n{message}",
                    settings.EMAIL_HOST_USER,
                    [support_email],
                    fail_silently=False,
                )
                messages.success(request, 'Email sent successfully!')
            except Exception as e:
                messages.error(request, 'Error sending email: {}'.format(e))
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, 'contact.html', {})


def newsletter(request):
    """Standalone newsletter subscription endpoint (POST only)."""
    newsform = LetterForm(request.POST or None)
    _handle_newsletter(request, newsform)
    return redirect('home')


def home(request):
    products = Product.objects.order_by('?')
    newsform = LetterForm(request.POST or None)
    _handle_newsletter(request, newsform)
    return render(request, 'index.html', {'products': products, 'newsform': newsform})


def about(request):
    newsform = LetterForm(request.POST or None)
    _handle_newsletter(request, newsform)
    return render(request, 'about.html', {'newsform': newsform})


def product(request, pk):
    product = get_object_or_404(Product, product_id=pk)
    category = product.category
    products_from_same_category = Product.objects.filter(category=category).exclude(product_id=pk)
    random_products = sample(list(products_from_same_category), min(4, len(products_from_same_category)))

    newsform = LetterForm(request.POST or None)
    _handle_newsletter(request, newsform)

    return render(request, 'product.html', {
        'product': product,
        'newsform': newsform,
        'random_products': random_products,
    })


def categories(request, items):
    all_categories = Category.objects.all()
    items = items.replace('-', ' ')

    try:
        category = Category.objects.get(name=items)
        products = Product.objects.filter(category=category).order_by('name')

        paginator = Paginator(products, 8)
        page_number = request.GET.get('page')
        product_pagin = paginator.get_page(page_number)

        newsform = LetterForm(request.POST or None)
        _handle_newsletter(request, newsform)

        return render(request, 'categories.html', {
            'products': products,
            'product_pagin': product_pagin,
            'newsform': newsform,
            'category': category,
            'categories': all_categories,
        })
    except Category.DoesNotExist:
        messages.error(request, "Products Not Available At The Moment...")
        return render(request, 'categories.html', {'categories': all_categories})
    except Exception as e:
        messages.error(request, "An error occurred: {}".format(e))
        return redirect('home')


def search(request):
    categories = Category.objects.all()

    try:
        if request.method == "POST":
            searched_term = request.POST.get('search', '')
            searched = Product.objects.filter(
                Q(name__icontains=searched_term) | Q(description__icontains=searched_term)
            )

            if searched.exists():
                return render(request, "categories.html", {'searched': searched, 'categories': categories})
            else:
                messages.error(request, "Product You Searched For Is Not Available...")
                return render(request, "categories.html", {'categories': categories})

        return render(request, "categories.html", {'categories': categories})

    except Exception as e:
        messages.error(request, "Product You Searched For Is Not Available...")
        return redirect('categories', 'Earrings')


def filtering(request, items):
    items = items.replace('-', ' ')
    categories = Category.objects.all()
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    try:
        category = Category.objects.get(name=items)
    except Category.DoesNotExist:
        messages.error(request, "Category not found.")
        return redirect('home')

    product_filter = Product.objects.none()
    message = None

    if not min_price or not max_price:
        message = "Please enter both minimum and maximum price."
    else:
        try:
            min_price = float(min_price)
            max_price = float(max_price)
            product_filter = Product.objects.filter(
                category=category,
                price__gte=min_price,
                price__lte=max_price,
            )
        except ValueError:
            message = "Invalid price format. Please enter valid numerical values."

    return render(request, 'categories.html', {
        'product_filter': product_filter,
        'category': category,
        'categories': categories,
        'message': message,
    })


def filter_all(request, items):
    categories = Category.objects.all()
    category = get_object_or_404(Category, name=items)
    product_filts = Product.objects.filter(category=category)

    sort_by = request.GET.get('sort_by')
    sorting_options = {
        'latest': '-created_at',
        'cheapest': 'price',
        'all': 'category',
    }

    if sort_by in sorting_options:
        product_filt = product_filts.order_by(sorting_options[sort_by])
    else:
        product_filt = product_filts

    paginator = Paginator(product_filt, 9)
    page_number = request.GET.get('page')
    products_filt = paginator.get_page(page_number)

    return render(request, 'categories.html', {
        'sort_by': sort_by,
        'products_filt': products_filt,
        'category': category,
        'categories': categories,
    })


def filters_all(request):
    categories = Category.objects.all()
    products_filt = Product.objects.all()

    sort_by = request.GET.get('sort_by')
    if sort_by == 'latest':
        products_filt = products_filt.order_by('-created_at')
    elif sort_by == 'cheapest':
        products_filt = products_filt.order_by('price')

    return render(request, 'categories.html', {'products_filt': products_filt, 'categories': categories})


# ---------------------------------------------------------------------------
# Auth views
# ---------------------------------------------------------------------------

def signup(request):
    form = SignUpForm()

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Welcome! Kindly continue to checkout")
            return redirect('cart_summary')

    return render(request, 'signup.html', {'form': form})


@csrf_protect
def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been Logged In, Fill Your Shipping Address")
            next_url = request.GET.get('next') or request.POST.get('next') or 'shipping'
            return redirect(next_url)
        else:
            messages.error(request, "Login not successful. Please try again.")
            return redirect('signin')

    return render(request, 'signin.html', {})


def signout(request):
    logout(request)
    messages.success(request, "You have logged out!")
    return redirect('home')


# ---------------------------------------------------------------------------
# Admin views
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def admin_cat_product_list(request, pk):
    category = get_object_or_404(Category, category_id=pk)

    if request.method == 'POST':
        num = request.POST.get('num')
        product = get_object_or_404(Product, product_id=num)
        product.delete()
        messages.success(request, "Product deleted successfully.")
        # Redirect after POST so a page refresh doesn't re-submit the delete
        return redirect('admin_cat_product_list', pk=pk)

    # Re-fetch products after any delete redirect lands here
    products = Product.objects.filter(category=category)
    return render(request, 'admin_cat_product_list.html', {'products': products})


@login_required
@user_passes_test(is_admin)
def admin_cat_list(request):
    categories = Category.objects.all()
    return render(request, 'admin_cat_list.html', {"categories": categories})


@login_required
@user_passes_test(is_admin)
def admin_uploads(request):
    categories = Category.objects.all()
    colors = Color.objects.all()
    sizes = Size.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('cats')
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        color_names = request.POST.getlist('product_colors')
        size_names = request.POST.getlist('product_sizes')
        product_des = request.POST.get('product_des')
        product_feats = request.POST.get('product_feats')
        product_img = request.FILES.get('product_img')

        try:
            product_price = float(product_price)
        except (TypeError, ValueError):
            messages.error(request, "Invalid price. Please enter a valid number.")
            return redirect('admin_uploads')

        try:
            category = get_object_or_404(Category, category_id=category_id)

            product = Product.objects.create(
                name=product_name,
                description=product_des,
                price=product_price,
                feature=product_feats,
                image=product_img,
                category=category,
            )

            for color_name in color_names:
                color, _ = Color.objects.get_or_create(name=color_name)
                product.colors.add(color)

            for size_name in size_names:
                size, _ = Size.objects.get_or_create(name=size_name)
                product.sizes.add(size)

            messages.success(request, "Product Added Successfully")
            return redirect('admin_uploads')

        except Exception as e:
            messages.error(request, str(e))
            return redirect('admin_uploads')

    return render(request, 'admin_uploads.html', {
        "categories": categories,
        "colors": colors,
        "sizes": sizes,
    })


# ---------------------------------------------------------------------------
# Shipping
# ---------------------------------------------------------------------------

@login_required   # fixed: was manual is_authenticated check, now uses decorator
def shipping(request):
    shipping_user = Shippingaddr.objects.filter(customer=request.user).first()
    shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

    if shipping_form.is_valid():
        instance = shipping_form.save(commit=False)
        instance.customer = request.user
        instance.save()
        messages.success(request, "Shipping Address Successfully Submitted")
        return redirect('checkout')

    return render(request, 'shipping.html', {'Shipping_form': shipping_form})


# ---------------------------------------------------------------------------
# Static / info pages
# ---------------------------------------------------------------------------

def logs(request):
    return render(request, 'logs.html', {})


def ship_info(request):
    return render(request, 'ship_info.html', {})


def pay_info(request):
    return render(request, 'pay_info.html', {})


def terms_info(request):
    return render(request, 'terms_info.html', {})


# ---------------------------------------------------------------------------
# Push notification views
# ---------------------------------------------------------------------------

@staff_member_required
@require_GET
def push_vapid_public_key(request):
    """Lets the admin-side JS fetch the public VAPID key at runtime."""
    return JsonResponse({'publicKey': settings.VAPID_PUBLIC_KEY})


@staff_member_required
@require_POST
def push_subscribe(request):
    """Called by mdf-push.js after the admin grants notification permission."""
    try:
        data = json.loads(request.body)
        endpoint = data['endpoint']
        keys = data['keys']
        p256dh = keys['p256dh']
        auth = keys['auth']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'error': 'Malformed subscription payload'}, status=400)

    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            'user': request.user,
            'p256dh': p256dh,
            'auth': auth,
        },
    )
    return JsonResponse({'status': 'subscribed'})


@staff_member_required
@require_POST
def push_unsubscribe(request):
    """Called when the admin clicks Disable notifications."""
    try:
        data = json.loads(request.body)
        endpoint = data['endpoint']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'error': 'Malformed payload'}, status=400)

    PushSubscription.objects.filter(endpoint=endpoint).delete()
    return JsonResponse({'status': 'unsubscribed'})