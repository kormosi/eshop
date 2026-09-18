import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY


def send_order_confirmation_email(order, invoice):
    items_html = "".join(
        f"<li>{item.quantity} × {item.product.name} "
        f"({item.unit_price} {order.currency})</li>"
        for item in order.items.all()
    )

    with invoice.pdf.open("rb") as pdf_file:
        pdf_content = list(pdf_file.read())

    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": order.email,
        "subject": f"Potvrdenie objednávky {order.id}",
        "html": (
            "<p>Ďakujeme za Vašu objednávku!</p>"
            f"<ul>{items_html}</ul>"
            f"<p>Total: {order.total} {order.currency}</p>"
            "<p>Faktúru nájdete v prílohe.</p>"
            "<p>Na tento email neodpovedajte.</p>"
        ),
        "attachments": [
            {
                "filename": f"faktura-{invoice.number}.pdf",
                "content": pdf_content,
                "content_type": "application/pdf",
            }
        ],
    })
