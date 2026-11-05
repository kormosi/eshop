import resend
from django.conf import settings
from django.utils.html import escape
from django.utils.timezone import localtime

resend.api_key = settings.RESEND_API_KEY


def notify_owner(subject):
    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": settings.NOTIFY_EMAIL,
        "subject": subject,
        "text": subject,
    })


def send_order_confirmation_email(order):
    items_html = "".join(
        f"<li>{item.quantity} × {escape(item.product.name)} "
        f"({item.unit_price} {order.currency})</li>"
        for item in order.items.all()
    )
    items_html += f"<li>Doprava ({order.delivery_fee} {order.currency})</li>"

    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": order.email,
        "subject": f"Potvrdenie objednávky {order.id}",
        "html": (
            "<p>Ďakujeme za Vašu objednávku!</p>"
            f"<ul>{items_html}</ul>"
            f"<p>Spolu: {order.total} {order.currency}</p>"
            "<p>Faktúru Vám zašleme samostatne.</p>"
            "<p>Na tento email neodpovedajte.</p>"
            '<p><a href="https://silviakormosi.com">www.silviakormosi.com</a></p>'
        ),
    })

    notify_owner(f"Nová objednávka {order.id}")


def send_withdrawal_confirmation_email(withdrawal):
    submitted_at = localtime(withdrawal.created_at).strftime("%d.%m.%Y %H:%M")
    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": withdrawal.email,
        "subject": f"Potvrdenie odstúpenia od zmluvy (objednávka {withdrawal.order_number})",
        "html": (
            "<p>Potvrdzujeme prijatie Vášho odstúpenia od zmluvy.</p>"
            "<ul>"
            f"<li>Meno a priezvisko: {escape(withdrawal.name)}</li>"
            f"<li>Číslo objednávky: {escape(withdrawal.order_number)}</li>"
            f"<li>Dátum a čas odstúpenia: {submitted_at}</li>"
            "</ul>"
            "<p>Na tento email neodpovedajte.</p>"
            '<p><a href="https://silviakormosi.com">www.silviakormosi.com</a></p>'
        ),
    })

    notify_owner(f"Nové odstúpenie od zmluvy (objednávka {withdrawal.order_number})")
