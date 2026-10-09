import hmac, json, time
from hashlib import sha256

from django.conf import settings
from django.test import Client, TestCase

from .models import Order


def post_event(client, type_, order_id, **session):
    payload = json.dumps({
        "id": "evt_1", "object": "event", "type": type_,
        "data": {"object": {"id": "cs_1", "object": "checkout.session",
                            "metadata": {"order_id": str(order_id)} if order_id else {}, **session}},
    })
    ts = int(time.time())
    sig = hmac.new(settings.STRIPE_WEBHOOK_SECRET.encode(), f"{ts}.{payload}".encode(), sha256).hexdigest()
    return client.post("/stripe/webhook/", payload, content_type="application/json",
                       HTTP_STRIPE_SIGNATURE=f"t={ts},v1={sig}")


class WebhookTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            first_name="a", last_name="b", address="c", city="d", postal_code="81101",
            country="SK", email="a@b.sk", phone="123456", total="10.00",
            pickup_point_id="1", pickup_point_address="x")

    def status(self):
        return Order.objects.get(id=self.order.id).status

    def paid(self, **kw):
        s = {"payment_status": "paid", "amount_total": 1000, "currency": "eur", **kw}
        return post_event(self.client, "checkout.session.completed", self.order.id, **s)

    def test_paid(self):
        self.assertEqual(self.paid().status_code, 200)
        self.assertEqual(self.status(), "paid")
        self.assertIsNotNone(Order.objects.get(id=self.order.id).paid_at)

    def test_unpaid_waits_for_async_success(self):
        self.paid(payment_status="unpaid")
        self.assertEqual(self.status(), "pending")
        post_event(self.client, "checkout.session.async_payment_succeeded", self.order.id,
                   payment_status="paid", amount_total=1000, currency="eur")
        self.assertEqual(self.status(), "paid")

    def test_amount_mismatch_not_paid(self):
        self.paid(amount_total=1)
        self.assertEqual(self.status(), "pending")

    def test_expired_cannot_override_paid(self):
        self.paid()
        post_event(self.client, "checkout.session.expired", self.order.id)
        self.assertEqual(self.status(), "paid")

    def test_foreign_session_without_metadata_is_200(self):
        self.assertEqual(post_event(self.client, "checkout.session.completed", None).status_code, 200)

    def test_bad_signature_400(self):
        self.assertEqual(self.client.post("/stripe/webhook/", "{}", content_type="application/json",
                                          HTTP_STRIPE_SIGNATURE="t=1,v1=bad").status_code, 400)


class InputTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_no_500_on_garbage(self):
        c = self.client
        self.assertEqual(c.get("/checkout/").status_code, 405)
        for cart in ["", "nope", "[]", "null", '{"1": "abc"}', '{"1": {"a":1}}', '{"1": 0}', '{"1": 100}', '{"1": 1}']:
            r = c.post("/checkout/", {"cart": cart})
            self.assertEqual(r.status_code, 302, cart)
        for ids in ["²,٣", "9" * 40, ",".join(["1"] * 500), "", "-1"]:
            self.assertEqual(c.get("/cart/data/", {"ids": ids}).status_code, 200, ids)


class NotFoundTests(TestCase):
    def test_custom_404(self):
        for url in ["/nope/", "/checkout/success/?session_id=cs_x"]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 404, url)
            self.assertContains(r, "Page not found", status_code=404)


class AbuseTests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    def test_honeypot(self):
        r = self.client.post("/checkout/", {"website": "x", "cart": '{"1": 1}'}, follow=True)
        self.assertContains(r, "Too many attempts")
        self.assertEqual(Order.objects.count(), 0)

    def test_rate_limit(self):
        for _ in range(10):
            r = self.client.post("/checkout/", {"cart": ""}, follow=True)
            self.assertNotContains(r, "Too many attempts")
        self.assertContains(self.client.post("/checkout/", {"cart": ""}, follow=True), "Too many attempts")

    def test_rate_limit_is_per_forwarded_ip(self):
        for _ in range(11):
            self.client.post("/checkout/", {"cart": ""}, HTTP_X_FORWARDED_FOR="1.1.1.1")
        # fresh client: the first one's session still holds its queued error messages
        r = Client().post("/checkout/", {"cart": ""}, follow=True, HTTP_X_FORWARDED_FOR="2.2.2.2")
        self.assertNotContains(r, "Too many attempts")

    def test_csp_header(self):
        r = self.client.get("/about")
        self.assertIn("script-src", r["Content-Security-Policy"])
