# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, timedelta

from .models import Booking

MAXIMUM_INQUIRY_YEARS = 2


@dataclass(frozen=True)
class BookingPeriod:
    """A period displayed as one continuous booking."""

    start: date
    end: date


def aggregate_booking_periods(
    bookings: Iterable[tuple[date, date]],
) -> tuple[BookingPeriod, ...]:
    """Merge bookings as they are presented in the availability calendar."""
    one_day = timedelta(days=1)
    merge_distance = timedelta(days=2)
    periods = sorted(
        (
            BookingPeriod(start, end + one_day if start == end else end)
            for start, end in bookings
        ),
        key=lambda period: (period.start, period.end),
    )
    aggregated: list[BookingPeriod] = []
    for period in periods:
        if not aggregated or period.start > aggregated[-1].end + merge_distance:
            aggregated.append(period)
            continue

        previous = aggregated[-1]
        aggregated[-1] = BookingPeriod(
            start=previous.start,
            end=max(previous.end, period.end),
        )
    return tuple(aggregated)


def get_aggregated_booking_periods() -> tuple[BookingPeriod, ...]:
    """Load bookings and return the periods shared by HTML and iCalendar."""
    bookings = Booking.objects.order_by("start", "end").values_list("start", "end")
    return aggregate_booking_periods(bookings)


def maximum_inquiry_date(today: date) -> date:
    """Return the same calendar date at the end of the inquiry horizon."""
    try:
        return today.replace(year=today.year + MAXIMUM_INQUIRY_YEARS)
    except ValueError:
        # February 29 has no direct equivalent in a non-leap year.
        return today.replace(
            year=today.year + MAXIMUM_INQUIRY_YEARS,
            month=2,
            day=28,
        )


def get_inquiry_date_bounds(today: date) -> tuple[date, date]:
    """Return the first available arrival and the final accepted date."""
    earliest_arrival = today + timedelta(days=1)
    maximum_date = maximum_inquiry_date(today)
    bookings = (
        Booking.objects.filter(
            end__gte=earliest_arrival,
            start__lte=maximum_date,
        )
        .order_by("start", "end")
        .values_list("start", "end")
    )

    for booking_start, booking_end in bookings:
        if booking_start > earliest_arrival:
            break
        if booking_end >= earliest_arrival:
            earliest_arrival = booking_end + timedelta(days=1)

    return earliest_arrival, maximum_date


def has_booking_conflict(arrival: date, departure: date) -> bool:
    """Return whether a requested stay overlaps an occupied calendar date."""
    return Booking.objects.filter(
        start__lt=departure,
        end__gte=arrival,
    ).exists()
