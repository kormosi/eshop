import json
from pathlib import Path

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Order, OrderItem
from .stripe import create_checkout_session
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import redirect

def home(request):
    product = Product.objects.filter(active=True, is_shipping=False).first()

    return render(
        request,
        "eshop/home.html",
        {"product": product},
    )

def cart(request):
    shipping = Product.objects.get(is_shipping=True)
    return render(request, "eshop/cart.html", {"delivery_fee": shipping.price})

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
        is_shipping=False,
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

    # Reject empty cart
    quantity = cart.get(PRODUCT_ID)
    if quantity is None:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # Reject invalid product counts
    quantity = int(quantity)
    if not 1 <= quantity <= 99:
        messages.error(request, "Quantity must be between 1 and 99.")
        return redirect("cart")

    # Reject invalid pickup point
    pickup_point_id = request.POST.get("pickup_point_id")
    if not pickup_point_id:
        messages.error(request, "Please select a pick-up point.")
        return redirect("cart")

    # Reject missing VOP consent
    if not request.POST.get("vop_consent"):
        messages.error(request, "Please confirm that you have read the terms and conditions.")
        return redirect("cart")

    product = Product.objects.get(
        id=PRODUCT_ID,
        active=True,
    )
    shipping = Product.objects.get(is_shipping=True)

    order = Order.objects.create(
        email=request.POST["email"],
        # first_name=request.POST["first_name"],
        # last_name=request.POST["last_name"],
        # phone=request.POST["phone"],
        # address=request.POST["address"],
        # city=request.POST["city"],
        # postal_code=request.POST["postal_code"],
        # country=request.POST["country"],
        pickup_point_id=request.POST["pickup_point_id"],
        pickup_point_address=request.POST["pickup_point_address"],
        total=product.price * quantity + shipping.price,
        currency=product.currency,
        delivery_fee=shipping.price,
        delivery_vat_rate=shipping.vat_rate,
    )
    
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=int(cart[PRODUCT_ID]),
        unit_price=product.price,
        vat_rate=product.vat_rate,
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
    session_id = request.GET.get("session_id")

    if session_id:
        order = Order.objects.filter(stripe_checkout_session_id=session_id).first()
        if order and order.status == Order.Status.PENDING:
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status"])

    return render(request, "eshop/checkout_cancel.html")

def vop(request):
    vop_text = (Path(settings.BASE_DIR) / "VOP.txt").read_text(encoding="utf-8")
    return render(request, "eshop/vop.html", {"vop_text": vop_text})
