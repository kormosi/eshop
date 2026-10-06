import logging

import stripe

from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .emails import send_order_confirmation_email
from .invoices import create_invoice
from .models import Order

logger = logging.getLogger(__name__)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    STATUS_BY_EVENT_TYPE = {
        "checkout.session.completed": Order.Status.PAID,
        "checkout.session.async_payment_succeeded": Order.Status.PAID,
        "checkout.session.expired": Order.Status.CANCELLED,
        "checkout.session.async_payment_failed": Order.Status.FAILED,
    }

    new_status = STATUS_BY_EVENT_TYPE.get(event.type)
    if new_status is not None:
        session = event.data.object.to_dict()
        order_id = (session.get("metadata") or {}).get("order_id")
        if not order_id or not order_id.isdecimal():
            return HttpResponse(status=200)  # not one of our orders, retrying won't help

        is_paid = new_status == Order.Status.PAID
        if is_paid and session.get("payment_status") != "paid":
            return HttpResponse(status=200)  # wait for async_payment_succeeded, stripe will send a different event later

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponse(status=400)

        if is_paid and (
            session.get("amount_total") != int(order.total * 100)
            or (session.get("currency") or "").upper() != order.currency.upper()
        ):
            logger.error("Order %s: Stripe amount/currency mismatch, not marking paid", order.id)
            return HttpResponse(status=200)

        # Atomic compare-and-set: of concurrent/duplicate deliveries only one
        # updates a row (replaces the old read-then-write idempotency check).
        changed = Order.objects.filter(id=order.id, status=Order.Status.PENDING).update(
            status=new_status,
            **({"paid_at": timezone.now()} if is_paid else {}),
        )

        if changed:
            pass  # invoicing disabled for now, re-enable below
            # if is_paid:
            #     try:
            #         invoice = create_invoice(order)
            #         send_order_confirmation_email(order, invoice)
            #     except Exception:
            #         # Don't let a PDF/Resend hiccup turn into a 500 and a
            #         # pointless Stripe retry of an already-paid order.
            #         logger.exception(
            #             "Failed to create/send invoice for order %s", order.id
            #         )

    return HttpResponse(status=200)