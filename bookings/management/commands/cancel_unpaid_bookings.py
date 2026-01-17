from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from bookings.models import Booking


class Command(BaseCommand):
    help = "Cancel bookings that have no payment/deposit after a grace period."

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes",
            type=int,
            default=15,
            help="Grace period (minutes) before auto-cancel.",
        )

    def handle(self, *args, **options):
        minutes = options["minutes"]
        cutoff = timezone.now() - timedelta(minutes=minutes)

        qs = (
            Booking.objects.filter(created_at__lt=cutoff)
            .filter(status__in=["pending", "confirmed"])
            .filter(payment_status__in=["pending", "refunded"])
            .filter(deposit_paid=False)
        )

        updated = qs.update(
            status="cancelled",
            deposit_required=False,
            deposit_paid=False,
            deposit_percentage=Decimal("0"),
            deposit_amount=Decimal("0"),
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Auto-cancelled {updated} booking(s) older than {minutes} minute(s) without payment/deposit."
            )
        )
