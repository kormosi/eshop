import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY


def send_order_confirmation_email(order):
    items_html = "".join(
        f"<li>{item.quantity} × {item.product.name} "
        f"({item.unit_price} {order.currency})</li>"
        for item in order.items.all()
    )

    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": order.email,
        "subject": f"Order #{order.id} confirmed",
        "html": (
            "<p>Thank you for your order!</p>"
            f"<ul>{items_html}</ul>"
            f"<p>Total: {order.total} {order.currency}</p>"
        ),
    })
