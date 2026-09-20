from django.contrib import admin
from .models import Product, Order, OrderItem


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "currency", "vat_rate", "active", "is_shipping")
    list_filter = ("active", "is_shipping")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status", "delivery_fee", "total", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]


admin.site.register(OrderItem)