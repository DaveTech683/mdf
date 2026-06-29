from payment.models import Order  # fixed: was from .models import Order


def unshipped_orders(request):
    # This is now a no-op — nav_notifications in payment/context_processors.py
    # handles both unshipped_count and has_arrived. Kept here to avoid a
    # missing-function error until the settings.py entry is removed.
    return {}