import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(order):
    return stripe.checkout.Session.create(
        mode="payment",
        metadata={
            "order_id": str(order.id),
        },
        line_items = [
            {
                "price_data": {
                    "currency": item.order.currency.lower(),
                    "product_data": {
                        "name": item.product.name,
                    },
                    "unit_amount": int(item.unit_price * 100),
                },
                "quantity": item.quantity,
            }
            for item in order.items.all()
        ],
        success_url="http://127.0.0.1:8000/checkout/success/",
        cancel_url="http://127.0.0.1:8000/checkout/cancel/",
    )