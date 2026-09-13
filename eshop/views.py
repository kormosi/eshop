import json
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Order, OrderItem
from .stripe import create_checkout_session
from django.http import JsonResponse

def home(request):
    product = Product.objects.filter(active=True).first()

    return render(
        request,
        "eshop/home.html",
        {"product": product},
    )

def cart(request):
    return render(request, "eshop/cart.html")


def cart_data(request):
    ids = request.GET.get("ids", "")

    product_ids = [
        int(product_id)
        for product_id in ids.split(",")
        if product_id.isdigit()
    ]

    products = Product.objects.filter(
        id__in=product_ids,
        active=True,
    )

    return JsonResponse([
        {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "currency": product.currency,
        }
        for product in products
    ], safe=False)

def checkout(request):
    PRODUCT_ID = "1"
    cart = json.loads(request.POST["cart"])
    product = Product.objects.get(
        id=PRODUCT_ID,
        active=True,
    )
    order = Order.objects.create(
        email=request.POST["email"],
        total=product.price,
        currency=product.currency,
        pickup_point_id=request.POST["pickup_point_id"],
    )
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=int(cart[PRODUCT_ID]),
        unit_price=product.price,
    )
    session = create_checkout_session(order)
    
    order.stripe_checkout_session_id = session.id
    order.save(update_fields=["stripe_checkout_session_id"])
    return redirect(session.url)


def checkout_success(request):
    session_id = request.GET.get("session_id")

    # So that when someone manually visits /checkout/success before the
    # order has been paid, they will get 404
    order = get_object_or_404(
        Order,
        stripe_checkout_session_id=session_id,
        status=Order.Status.PAID,
    )

    return render(
        request,
        "eshop/checkout_success.html",
        {"order": order},
    )


def checkout_cancel(request):
    return render(request, "eshop/checkout_cancel.html")

