from django.contrib import admin
from .models import Customer, Category, Product, Subscriber
from django.apps import AppConfig


admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
# admin.site.register(Order)
admin.site.register(Subscriber)
# admin.site.register(EmailTemplate)



class CustomersConfig(AppConfig):
    """
    Replace 'store' below with whatever your app is actually called
    (the folder name containing models.py / views.py).
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'   # ← change this to match your app name if different

    def ready(self):
        # Importing signals here is what wires them up.
        # Django calls ready() once at startup — this is the correct pattern.
        import customers.signals  # noqa: F401  ← change 'store' to match your app name
