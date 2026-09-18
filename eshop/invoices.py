import os
import sys
from decimal import Decimal

if sys.platform == "darwin":
    # Homebrew's Pango/GObject libs (needed by WeasyPrint) aren't on the
    # default dlopen search path on macOS.
    os.environ.setdefault(
        "DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib:/usr/local/lib"
    )

from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from .models import Invoice

VAT_RATE = Decimal("0.05")  # Slovak standard VAT rate for books
CENTS = Decimal("0.01")


def _next_invoice_number():
    year = timezone.now().year
    count = Invoice.objects.filter(number__startswith=str(year)).count()
    return f"{year}{count + 1:04d}"


def create_invoice(order):
    issued_at = timezone.now().date()

    items = []
    base_total = Decimal("0")
    vat_total = Decimal("0")

    for item in order.items.all():
        line_total = item.unit_price * item.quantity
        line_base = (line_total / (1 + VAT_RATE)).quantize(CENTS)
        line_vat = line_total - line_base

        base_total += line_base
        vat_total += line_vat

        items.append({
            "product": item.product,
            "quantity": item.quantity,
            "unit_base": (item.unit_price / (1 + VAT_RATE)).quantize(CENTS),
            "line_vat": line_vat,
            "line_total": line_total,
        })

    with transaction.atomic():
        number = _next_invoice_number()

        html = render_to_string("eshop/invoice.html", {
            "order": order,
            "number": number,
            "issued_at": issued_at,
            "items": items,
            "vat_rate_percent": int(VAT_RATE * 100),
            "base_total": base_total,
            "vat_total": vat_total,
            "total": base_total + vat_total,
        })

        pdf_bytes = HTML(string=html).write_pdf()

        invoice = Invoice(order=order, number=number)
        invoice.pdf.save(f"{number}.pdf", ContentFile(pdf_bytes), save=False)
        invoice.save()

    return invoice
