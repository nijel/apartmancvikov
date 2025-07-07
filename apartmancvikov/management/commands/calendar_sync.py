from __future__ import annotations

from datetime import date, datetime, timedelta

from caldav.davclient import get_davclient
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apartmancvikov.models import Booking


def fixup_date(value: date | datetime) -> date:
    """Convert iCal date into date object."""
    if isinstance(value, datetime):
        value = value.date()
    return value


class Command(BaseCommand):
    help = "refreshes calendar data"

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        """Fetch CalDav calendar and sync to Booking model."""
        verbosity = int(options["verbosity"])
        existing = {booking.uid: booking for booking in Booking.objects.all()}

        with get_davclient(
            username=settings.CALDAV_USER,
            password=settings.CALDAV_PASSWORD,
            url=settings.CALDAV_URL,
        ) as client:
            calendar_url = settings.CALDAV_URL.split("/", 3)[-1]
            calendar = client.calendar(url=f"/{calendar_url}")

            start_date = timezone.now().date().replace(day=1)

            events = calendar.search(
                event=True,
                start=start_date,
                end=start_date + timedelta(days=600),
                expand=True,
            )

            for event in events:
                start = fixup_date(event.component.start)
                end = fixup_date(event.component.end)
                uid = event.component.uid
                if uid not in existing:
                    booking = Booking.objects.create(start=start, end=end, uid=uid)
                    if verbosity > 1:
                        self.stdout.write(f"created: {booking}")
                else:
                    booking = existing[event.component.uid]
                    if booking.start != start or booking.end != end:
                        booking.start = start
                        booking.end = end
                        booking.save()
                        self.stdout.write(f"updated: {booking}")
                    del existing[event.component.uid]

            for booking in existing.values():
                booking.delete()
                self.stdout.write(f"removed: {booking}")
