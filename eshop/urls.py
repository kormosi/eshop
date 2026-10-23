from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views
from .webhook import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("coming-soon/", views.coming_soon, name="coming_soon"),

    path("product/<int:product_id>/image/", views.product_image, name="product-image"),

    path("cart/", views.cart, name="cart"),
    path("cart/data/", views.cart_data, name="cart-data"),
    
    path("vop/", views.vop, name="vop"),
    path("rp/", views.rp, name="rp"),
    path("odstupenie-od-zmluvy/", views.odstupenie_od_zmluvy, name="odstupenie_od_zmluvy"),
    path("ochrana-osobnych-udajov/", views.osobne_udaje, name="osobne_udaje"),
    path("reklamacny-formular/", views.reklamacny_formular, name="reklamacny_formular"),

    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout-success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout-cancel"),

    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
]

# So that we can download the invoice PDFs at localhost:8000/media/invoices/20260001.pdf 
# Not sure I need this, though.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)