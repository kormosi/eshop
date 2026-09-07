from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Order, OrderItem
from .stripe import create_checkout_session

def home(request):
    product = Product.objects.filter(active=True).first()

    return render(
        request,
        "eshop/home.html",
        {"product": product},
    )

def checkout(request):
    product = get_object_or_404(
        Product,
        active=True,
    )
    order = Order.objects.create(
        email="test@example.com",
        total=product.price,
        currency=product.currency,
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=1,
        unit_price=product.price,
    )
    session = create_checkout_session(order)
    order.stripe_checkout_session_id = session.id
    order.save()
    return redirect(session.url)

def checkout_success(request):
    return render(request, "eshop/checkout_success.html")