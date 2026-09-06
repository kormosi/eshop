from django.shortcuts import render
from .models import Product


def home(request):
    product = Product.objects.filter(active=True).first()

    return render(
        request,
        "eshop/home.html",
        {"product": product},
    )