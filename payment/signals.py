import json
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail

from .models import Orderitem
from customers.models import PushSubscription

logger = logging.getLogger(__name__)


def notify_admin_new_order(order):
    """
    Sends email/push alert after order items have been created.
    This should be called manually from process_order after Orderitem records are saved.
    """
    if order.shipped:
        return

    _send_order_email(order)
    _send_order_push(order)


def _send_order_email(order):
    """Email all superusers about the new order."""
    admin_emails = list(
        User.objects.filter(is_superuser=True)
        .exclude(email='')
        .values_list('email', flat=True)
    )

    if not admin_emails:
        logger.warning('MDF notifications: no superuser email addresses found.')
        return

    try:
        customer_name = (
            order.order_name
            or order.customer.get_full_name()
            or order.customer.username
            or order.order_email
            or 'Unknown'
        )

        total_quantity = 0
        order_items = Orderitem.objects.filter(order=order)

        for item in order_items:
            try:
                total_quantity += int(item.quantity)
            except (TypeError, ValueError):
                continue

        subject = f'[MDF] New Order #{order.id} — Action Required'

        body = (
            f'A new order has been placed on Modest Daily Fashion.\n\n'
            f'Order ID       : #{order.id}\n'
            f'Customer       : {customer_name}\n'
            f'Customer Email : {order.order_email}\n'
            f'Amount Paid    : ₦{order.amount_paid}\n'
            f'Total Quantity : {total_quantity}\n'
            f'Date Ordered   : {order.order_date.strftime("%d %b %Y, %H:%M") if order.order_date else "N/A"}\n'
            f'Status         : Unshipped\n\n'
            f'Log in to your admin panel to process this order.\n\n'
            f'— Modest Daily Fashion Notification System'
        )

        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
            recipient_list=admin_emails,
            fail_silently=False,
        )

        logger.info('MDF notifications: order email sent for Order #%s', order.id)

    except Exception as exc:
        logger.error('MDF notifications: email failed for Order #%s — %s', order.id, exc)


def _send_order_push(order):
    """Send Web Push notification to stored admin browser subscriptions."""
    try:
        from pywebpush import webpush, WebPushException
    except ImportError:
        logger.warning(
            'MDF notifications: pywebpush not installed — skipping push. Run: pip install pywebpush'
        )
        return

    vapid_private = getattr(settings, 'VAPID_PRIVATE_KEY', None)
    vapid_claims = getattr(settings, 'VAPID_CLAIMS', None)

    if not vapid_private or not vapid_claims:
        logger.warning(
            'MDF notifications: VAPID_PRIVATE_KEY / VAPID_CLAIMS not set — skipping push.'
        )
        return

    admin_user_ids = list(
        User.objects.filter(is_superuser=True).values_list('id', flat=True)
    )

    subscriptions = PushSubscription.objects.filter(user_id__in=admin_user_ids)

    if not subscriptions.exists():
        logger.info('MDF notifications: no push subscriptions found for admins.')
        return

    payload = json.dumps({
        'title': f'New Order #{order.id}',
        'body': 'A new unshipped order has been placed. Tap to review.',
        'url': '/not_shipped_dash/',
    })

    stale_ids = []

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {
                        'p256dh': sub.p256dh,
                        'auth': sub.auth,
                    },
                },
                data=payload,
                vapid_private_key=vapid_private,
                vapid_claims=vapid_claims,
            )

            logger.info('MDF notifications: push sent to sub #%s', sub.pk)

        except WebPushException as exc:
            status = getattr(exc.response, 'status_code', None)

            if status in (404, 410):
                stale_ids.append(sub.pk)
                logger.info(
                    'MDF notifications: stale push sub #%s removed HTTP %s',
                    sub.pk,
                    status
                )
            else:
                logger.error(
                    'MDF notifications: push failed for sub #%s — %s',
                    sub.pk,
                    exc
                )

    if stale_ids:
        PushSubscription.objects.filter(pk__in=stale_ids).delete()