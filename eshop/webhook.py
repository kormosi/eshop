import stripe

from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Order


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

    if event.type == "checkout.session.completed":
        session = event.data.object
        order_id = session["metadata"]["order_id"]
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponse(status=400)
        
        if order.status != Order.Status.PAID:  # idempotency measure, Stripe can deliver one event more than once
            order.status = Order.Status.PAID
            order.paid_at = timezone.now()
            order.save()

    return HttpResponse(status=200)