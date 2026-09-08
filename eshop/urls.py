from django.contrib import admin
from django.urls import path
from . import views
from .webhook import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    
    path("cart/", views.cart, name="cart"),
    path("cart/data/", views.cart_data, name="cart-data"),
    
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/success/", views.checkout_success, name="checkout-success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout-cancel"),
    
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
]
