from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import BookDetails, MerchDetails, Product, Order, OrderItem

# Caddy rejects request bodies over 1 MB, so stay under it.
MAX_IMAGE_BYTES = 900_000


def sniff_image_type(data):
    # Decided from the bytes, not the filename or the browser's claim: the
    # result becomes the Content-Type we serve from our own origin.
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


class ProductForm(forms.ModelForm):
    image_upload = forms.FileField(
        required=False,
        label="Image",
        help_text="JPEG, PNG or WebP, max 900 kB.",
    )

    class Meta:
        model = Product
        fields = "__all__"

    def clean_image_upload(self):
        upload = self.cleaned_data["image_upload"]
        if not upload:
            return None
        if upload.size > MAX_IMAGE_BYTES:
            raise forms.ValidationError("Image is larger than 900 kB.")
        data = upload.read()
        image_type = sniff_image_type(data)
        if image_type is None:
            raise forms.ValidationError("Not a JPEG, PNG or WebP image.")
        return data, image_type

    def save(self, commit=True):
        if self.cleaned_data.get("image_upload"):
            self.instance.image, self.instance.image_type = self.cleaned_data["image_upload"]
        return super().save(commit)


class BookDetailsInline(admin.StackedInline):
    model = BookDetails
    can_delete = False


class MerchDetailsInline(admin.StackedInline):
    model = MerchDetails
    can_delete = False


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ("name", "price", "currency", "vat_rate", "category", "active")
    list_filter = ("active", "category")
    readonly_fields = ("image_preview",)

    @admin.display(description="Current image")
    def image_preview(self, obj):
        if not obj.image:
            return "—"
        return format_html('<img src="{}" style="max-height: 200px">', reverse("product-image", args=[obj.id]))

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