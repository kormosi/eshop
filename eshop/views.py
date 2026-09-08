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


def checkout(request):
    product = get_object_or_404(Product, active=True)
    order = Order.objects.create(
        email=request.POST["email"],
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
    order.save(update_fields=["stripe_checkout_session_id"])
    return redirect(session.url)


def checkout_success(request):
    return render(request, "eshop/checkout_success.html")

def checkout_cancel(request):
    return render(request, "eshop/checkout_cancel.html")

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