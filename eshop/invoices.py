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

CENTS = Decimal("0.01")


def _next_invoice_number():
    year = timezone.now().year
    count = Invoice.objects.filter(number__startswith=str(year)).count()
    return f"{year}{count + 1:04d}"


def create_invoice(order):
    issued_at = timezone.now().date()

    items = []
    totals_by_rate = {}  # vat_rate (percent) -> {"base": Decimal, "vat": Decimal}

    for item in order.items.all():
        rate = item.vat_rate / 100
        line_total = item.unit_price * item.quantity
        line_base = (line_total / (1 + rate)).quantize(CENTS)
        line_vat = line_total - line_base

        bucket = totals_by_rate.setdefault(
            item.vat_rate, {"base": Decimal("0"), "vat": Decimal("0")}
        )
        bucket["base"] += line_base
        bucket["vat"] += line_vat

        items.append({
            "product": item.product,
            "quantity": item.quantity,
            "vat_rate": item.vat_rate,
            "unit_base": (item.unit_price / (1 + rate)).quantize(CENTS),
            "line_vat": line_vat,
            "line_total": line_total,
        })

    # A separate base/VAT subtotal per rate, as Slovak VAT law requires
    # when an invoice mixes items taxed at different rates.
    vat_breakdown = [
        {"rate": rate, "base": totals["base"], "vat": totals["vat"]}
        for rate, totals in sorted(totals_by_rate.items())
    ]
    base_total = sum((row["base"] for row in vat_breakdown), Decimal("0"))
    vat_total = sum((row["vat"] for row in vat_breakdown), Decimal("0"))

    with transaction.atomic():
        number = _next_invoice_number()

        html = render_to_string("eshop/invoice.html", {
            "order": order,
            "number": number,
            "issued_at": issued_at,
            "items": items,
            "vat_breakdown": vat_breakdown,
            "base_total": base_total,
            "vat_total": vat_total,
            "total": base_total + vat_total,
        })

        pdf_bytes = HTML(string=html).write_pdf()

        invoice = Invoice(order=order, number=number)
        invoice.pdf.save(f"{number}.pdf", ContentFile(pdf_bytes), save=False)
        invoice.save()

    return invoice
