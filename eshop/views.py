import json
from pathlib import Path

from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CheckoutForm
from .models import Product, Order, OrderItem
from .stripe import create_checkout_session
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect

def home(request):
    product = Product.objects.filter(active=True).exclude(category=Product.Category.SHIPPING).first()

    return render(
        request,
        "eshop/home.html",
        {"product": product},
    )

def about(request):
    return render(request, "eshop/about.html")

def coming_soon(request):
    return render(request, "eshop/coming_soon.html")


def cart(request):
    shipping = Product.objects.get(category=Product.Category.SHIPPING)
    return render(request, "eshop/cart.html", {"delivery_fee": shipping.price})

def cart_data(request):
    ids = request.GET.get("ids", "")

    product_ids = [
        int(product_id)
        for product_id in ids.split(",")[:20]
        if product_id.isdecimal() and len(product_id) <= 9
    ]

    products = Product.objects.filter(
        id__in=product_ids,
        active=True,
    ).exclude(category=Product.Category.SHIPPING)

    return JsonResponse([
        {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "currency": product.currency,
        }
        for product in products
    ], safe=False)

def rate_limited(request, limit=10, window=600):
    # Caddy overwrites X-Forwarded-For and is the only way in, so its last
    # entry is the real client; REMOTE_ADDR would be Caddy for everyone.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[-1].strip()
    key = f"checkout-rl:{forwarded or request.META.get('REMOTE_ADDR')}"
    cache.add(key, 0, window)
    return cache.incr(key) > limit


@require_POST
def checkout(request):
    PRODUCT_ID = "1"

    if request.POST.get("website") or rate_limited(request):  # honeypot / abuse
        messages.error(request, "Too many attempts, try again later.")
        return redirect("cart")

    try:
        cart = json.loads(request.POST.get("cart", ""))
        quantity = cart.get(PRODUCT_ID)
    except (ValueError, AttributeError):
        quantity = None

    # Reject empty or malformed cart
    if quantity is None:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # Reject invalid product counts
    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        quantity = 0
    if not 1 <= quantity <= 99:
        messages.error(request, "Quantity must be between 1 and 99.")
        return redirect("cart")

    # Reject invalid pickup point
    pickup_point_id = request.POST.get("pickup_point_id", "")
    pickup_point_address = request.POST.get("pickup_point_address", "")
    if not pickup_point_id or not pickup_point_address or len(pickup_point_id) > 16 or len(pickup_point_address) > 255:
        messages.error(request, "Please select a pick-up point.")
        return redirect("cart")

    # Reject missing VOP consent
    if not request.POST.get("vop_consent"):
        messages.error(request, "Please confirm that you have read the terms and conditions.")
        return redirect("cart")

    # Reject invalid or missing billing details
    form = CheckoutForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please check the highlighted fields.")
        return redirect("cart")

    product = get_object_or_404(Product, id=PRODUCT_ID, active=True)
    shipping = get_object_or_404(Product, category=Product.Category.SHIPPING)

    order = Order.objects.create(
        **form.cleaned_data,
        pickup_point_id=pickup_point_id,
        pickup_point_address=pickup_point_address,
        total=product.price * quantity + shipping.price,
        currency=product.currency,
        delivery_fee=shipping.price,
        delivery_vat_rate=shipping.vat_rate,
    )
    
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=quantity,
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
    # No state change on GET: a user can go back and still pay. Abandoned
    # orders are cancelled by the checkout.session.expired webhook.
    return render(request, "eshop/checkout_cancel.html")

def vop(request):
    vop_text = (Path(settings.BASE_DIR) / "VOP.txt").read_text(encoding="utf-8")
    return render(request, "eshop/vop.html", {"vop_text": vop_text})

def odstupenie(request):
    return render(request, "eshop/odstupenie.html")

def osobne_udaje(request):
    return render(request, "eshop/osobne_udaje.html")
