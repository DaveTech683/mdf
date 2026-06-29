from django.db import models
from django.contrib.auth.models import User


class Subscriber(models.Model):
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.email


class Customer(models.Model):
    customer_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='', blank=True)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=65)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=350, default='', blank=True, null=True)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=9)
    image = models.ImageField(upload_to='uploads/product/')
    sizes = models.ManyToManyField(Size, blank=True, related_name='products')
    colors = models.ManyToManyField(Color, blank=True, related_name='products')
    feature = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=9)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PushSubscription(models.Model):
    """Stores a browser Web Push subscription for an admin/staff user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.TextField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Push sub for {self.user.username} ({self.endpoint[:60]})'