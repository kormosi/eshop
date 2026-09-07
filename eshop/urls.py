from django.contrib import admin
from django.urls import path
from . import views
from .webhook import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("checkout/", views.checkout, name="checkout"),
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
]
