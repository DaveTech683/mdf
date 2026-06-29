from django.db import models
from django.contrib.auth.models import User
from customers.models import Product
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


class Shippingaddr(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    shipping_name = models.TextField(max_length=100, blank=True, null=True)
    shipping_address = models.CharField(max_length=500, default='', blank=True)
    shipping_city = models.CharField(max_length=255, blank=True)
    shipping_state = models.CharField(max_length=255, blank=True)
    shipping_country = models.CharField(max_length=255, blank=True)
    shipping_phone_number = models.CharField(max_length=20, blank=True)
    shipping_email = models.EmailField(max_length=50, blank=True, null=True)

    class Meta:                              # fixed: was lowercase 'meta'
        verbose_name_plural = "Shipping Addresses"

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_name = models.CharField(max_length=100, default='')
    order_phone_number = models.CharField(max_length=20, blank=True)
    order_email = models.EmailField(max_length=50, blank=True, null=True)
    order_address = models.TextField(max_length=500, default='')
    amount_paid = models.DecimalField(max_digits=16, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Order - {str(self.id)}'


# Auto-set shipping date when shipped flips to True
@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            obj = sender._default_manager.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        if instance.shipped and not obj.shipped:
            instance.date_shipped = timezone.now()   # fixed: was naive datetime.now()


class Orderitem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=16, decimal_places=2)

    def __str__(self):
        return f'Order Item - {str(self.id)}'


class OrderView(models.Model):
    """Tracks when a user last viewed their order tracking page."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='order_view')
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} last viewed orders at {self.last_seen}'


# class PushSubscription(models.Model):
#     """Stores a browser Web Push subscription for an admin/staff user."""
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
#     endpoint = models.TextField(unique=True)
#     p256dh = models.TextField()
#     auth = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'Push sub for {self.user.username} ({self.endpoint[:60]})'


class UserPayment(models.Model):
    app_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    payment_bool = models.BooleanField(default=False)
    stripe_checkout_id = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)