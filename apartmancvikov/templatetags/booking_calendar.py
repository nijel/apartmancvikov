from calendar import HTMLCalendar
from datetime import date, timedelta

from django import template
from django.utils.dates import MONTHS, WEEKDAYS_ABBR
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from apartmancvikov.models import Booking

register = template.Library()


class BookingCalendar(HTMLCalendar):
    def __init__(self, firstweekday=0):
        """Initialize the calendar and load data."""
        super().__init__(firstweekday=firstweekday)
        self.start_dates = set()
        self.end_dates = set()
        self.booked_dates = set()
        self.fill_in_dates()
        self.cleanup_dates()

    def fill_in_dates(self):
        """Load booking dates from the database."""
        for booking in Booking.objects.all():
            self.start_dates.add(booking.start)
            self.end_dates.add(booking.end)
            days_range = (booking.end - booking.start).days - 1
            if days_range > 0:
                self.booked_dates.update(
                    booking.start + timedelta(days=day + 1) for day in range(days_range)
                )

    def cleanup_dates(self):
        """Cleanup booking dates to avoid spaces."""
        starts = list(self.start_dates)
        for start in starts:
            # Merge when start overlaps with end or there is just one day space
            previous = start - timedelta(days=1)
            if start in self.end_dates or previous in self.end_dates:
                self.end_dates.discard(start)
                self.end_dates.discard(previous)
                self.start_dates.remove(start)
                self.booked_dates.add(start)
                self.booked_dates.add(previous)

    def get_calendar_data(self) -> list[tuple[int, int, list[list[date]]]]:
        """Generate calendar data."""
        today = date.today()  # noqa: DTZ011
        year = today.year
        month = today.month
        months = []
        while len(months) < 18:  # noqa: PLR2004
            months.append(
                (year, month, self.monthdatescalendar(year, month)),
            )
            month += 1
            if month > 12:  # noqa: PLR2004
                month = 1
                year += 1
        return months

    def format_day(self, year: int, month: int, day: date):
        """Return a formatted day entry."""
        css_class = ""
        if day.year != year or day.month != month:
            value = mark_safe("&nbsp;")
        else:
            value = format_html("{}", day.day)
            # Booking CSS
            if day in self.booked_dates:
                css_class = "booking_middle"
            elif day in self.end_dates:
                css_class = "booking_end"
            elif day in self.start_dates:
                css_class = "booking_start"
        return format_html('<td class="{}">{}</td>', css_class, value)

    def formatmonthname(self, theyear, themonth, withyear=True):  # noqa: ARG002, FBT002
        """Return a month name as a table row."""
        return format_html(
            '<tr><th colspan="7" class="{}">{} {}</th></tr>',
            self.cssclass_month_head,
            MONTHS[themonth],
            theyear,
        )

    def formatweekheader(self):
        """Return a header for a week as a table row."""
        return mark_safe(super().formatweekheader())  # noqa: S308

    def formatweekday(self, day):
        """Return a weekday name as a table header."""
        return format_html(
            '<th class="{}">{}</th>',
            self.cssclasses_weekday_head[day],
            WEEKDAYS_ABBR[day],
        )

    def format_month(self, year: int, month: int, dates: list[list[date]]):
        """Generate HTML with a month calendar."""
        calendar = format_html_join(
            "\n",
            "<tr>{}</tr>",
            (
                (
                    format_html_join(
                        "\n",
                        "{}",
                        ((self.format_day(year, month, day),) for day in row),
                    ),
                )
                for row in dates
            ),
        )
        return format_html(
            '<table class="booking">{}{}{}</table>',
            self.formatmonthname(year, month, withyear=True),
            self.formatweekheader(),
            calendar,
        )

    def render_booking(self):
        """Generate HTML with a booking calendar."""
        data = self.get_calendar_data()
        months = [self.format_month(year, month, dates) for year, month, dates in data]
        return format_html_join(
            "\n",
            '<div class="p-2">{}</div>',
            ((month,) for month in months),
        )


@register.simple_tag
def render_calendar():
    """Generate HTML with a booking calendar."""
    calendar = BookingCalendar()

    return calendar.render_booking()
