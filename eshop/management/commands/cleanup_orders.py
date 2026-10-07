from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from eshop.models import Order


class Command(BaseCommand):
    help = "Delete orders still pending after 2 days (Stripe sessions expire after 24h). Run daily from cron."

    def handle(self, *args, **options):
        deleted, _ = Order.objects.filter(
            status=Order.Status.PENDING,
            created_at__lt=timezone.now() - timedelta(days=2),
        ).delete()
        self.stdout.write(f"Deleted {deleted} rows")
