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
        ] + [
            {
                "price_data": {
                    "currency": order.currency.lower(),
                    "product_data": {
                        "name": "Doprava",
                    },
                    "unit_amount": int(order.delivery_fee * 100),
                },
                "quantity": 1,
            }
        ],
        customer_email=order.email,
        # payment_method_types=["card"],
        success_url=(
            "http://127.0.0.1:8000/checkout/success/"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),
        cancel_url=(
            "http://127.0.0.1:8000/checkout/cancel/"
            "?session_id={CHECKOUT_SESSION_ID}"
        ),
    )