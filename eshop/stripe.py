import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(order):
    return stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": order.currency.lower(),
                    "product_data": {
                        "name": order.items.first().product.name,
                    },
                    "unit_amount": int(
                        order.items.first().unit_price * 100
                    ),
                },
                "quantity": order.items.first().quantity,
            }
        ],
        success_url="http://127.0.0.1:8000/checkout/success/",
        cancel_url="http://127.0.0.1:8000/checkout/cancel/",
    )