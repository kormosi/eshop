from django.contrib import admin
from .models import BookDetails, MerchDetails, Product, Order, OrderItem


class BookDetailsInline(admin.StackedInline):
    model = BookDetails
    can_delete = False


class MerchDetailsInline(admin.StackedInline):
    model = MerchDetails
    can_delete = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "currency", "vat_rate", "category", "active", "is_shipping")
    list_filter = ("active", "is_shipping", "category")

    def get_inlines(self, request, obj):
        if obj is None:
            # Category isn't chosen yet on the add form, so offer both.
            return [BookDetailsInline, MerchDetailsInline]
        if obj.category == Product.Category.BOOK:
            return [BookDetailsInline]
        if obj.category == Product.Category.MERCH:
            return [MerchDetailsInline]
        return []


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status", "delivery_fee", "total", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]


admin.site.register(OrderItem)