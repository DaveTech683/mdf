from payment.models import Order, OrderView
from django.utils import timezone


def nav_notifications(request):
    unshipped_count = 0
    has_arrived = False

    if request.user.is_authenticated:
        if request.user.is_superuser:
            unshipped_count = Order.objects.filter(shipped=False).count()
        else:
            try:
                last_seen = request.user.order_view.last_seen
            except OrderView.DoesNotExist:
                last_seen = None

            if last_seen:
                # Dot only shows for shipped orders newer than user's last visit
                has_arrived = Order.objects.filter(
                    customer=request.user,
                    shipped=True,
                    date_shipped__gt=last_seen,
                ).exists()
            else:
                # User has never visited track page — show dot if anything shipped
                has_arrived = Order.objects.filter(
                    customer=request.user,
                    shipped=True,
                ).exists()

    return {
        'unshipped_count': unshipped_count,
        'has_arrived': has_arrived,
    }