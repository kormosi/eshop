import logging

import stripe

from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .emails import send_order_confirmation_email
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

    # Checkout session events that resolve an order one way or another.
    # Session-related statuses only (not payment_intent.* events) since
    # order_id is only present in the checkout session's own metadata.
    STATUS_BY_EVENT_TYPE = {
        "checkout.session.completed": Order.Status.PAID,
        "checkout.session.expired": Order.Status.CANCELLED,
        "checkout.session.async_payment_failed": Order.Status.FAILED,
    }

    new_status = STATUS_BY_EVENT_TYPE.get(event.type)
    if new_status is not None:
        session = event.data.object
        order_id = session["metadata"]["order_id"]

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponse(status=400)

        if order.status == Order.Status.PENDING:  # idempotency measure, Stripe can deliver one event more than once
            is_paid = new_status == Order.Status.PAID

            order.status = new_status
            if is_paid:
                order.paid_at = timezone.now()
            order.save()

            if is_paid:
                try:
                    send_order_confirmation_email(order)
                except Exception:
                    # Don't let a Resend hiccup turn into a 500 and a
                    # pointless Stripe retry of an already-paid order.
                    logger.exception(
                        "Failed to send confirmation email for order %s", order.id
                    )

    return HttpResponse(status=200)