from django.contrib import admin
from .models import Shippingaddr, Order, Orderitem
from django.contrib.auth.models import User

admin.site.register(Shippingaddr)
admin.site.register(Order)
admin.site.register(Orderitem)

class OrderItemInline(admin.StackedInline):
    model = Orderitem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["order_date"]
    # fields = ["order_name", "order_phone_number", "order_email"]
    inlines = [OrderItemInline]

admin.site.unregister(Order)


admin.site.register(Order, OrderAdmin)
   
