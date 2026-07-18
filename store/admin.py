from django.contrib import admin
from .models import Category, Product, Order, OrderItem,Cart

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Cart)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "customer", "pick_up_date", "total", "payment_status", "order_status", "date")
    list_filter = ("payment_status", "order_status", "pick_up_date", "date")
    search_fields = ("order_id", "customer__username", "customer__email")
