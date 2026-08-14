# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

import json
from datetime import UTC, datetime, timedelta
from io import BytesIO, StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from .models import WeatherForecastSnapshot
from .weather import (
    CHMI_FORECAST_URL,
    METEOBLUE_FORECAST_URL,
    WEATHER_DATA_URL,
    WEATHER_SOURCE,
    YR_FORECAST_URL,
    build_weather_forecast,
    validate_weather_payload,
)


def forecast_entry(forecast_time, **overrides):
    """Build one valid upstream forecast entry for a test."""
    entry = {
        "validityTime": forecast_time.isoformat(),
        "t2m": 12.5,
        "rh2m": 72.0,
        "mslp": 1014.2,
        "cloudsTot": 45.0,
        "windSpeed": 2.4,
        "icon": 40,
        "prec": 0.2,
        "windDirection": 225.0,
        "windGustSpeed": 5.1,
        "snow": 0.0,
    }
    entry.update(overrides)
    return entry


def forecast_payload(*entries):
    """Build a minimal valid upstream forecast payload."""
    return {
        "parameters": {"t2m": {"unit": "°C", "name": "Teplota"}},
        "data": list(entries),
        "z": 348,
    }


class FakeResponse(BytesIO):
    def __init__(self, content, *, status=200):
        """Create a file-like HTTP response with a status code."""
        super().__init__(content)
        self.status = status


class WeatherSyncTest(TestCase):
    def setUp(self):
        """Prepare a small valid ALADIN response."""
        self.now = datetime(2026, 8, 14, 12, tzinfo=UTC)
        self.payload = forecast_payload(
            forecast_entry(self.now),
            forecast_entry(self.now + timedelta(hours=1)),
        )

    @patch("apartmancvikov.management.commands.weather_sync.urlopen")
    def test_sync_stores_valid_forecast(self, mocked_urlopen):
        """A valid response is saved without default success output."""
        mocked_urlopen.return_value = FakeResponse(json.dumps(self.payload).encode())
        output = StringIO()

        call_command("weather_sync", stdout=output)

        snapshot = WeatherForecastSnapshot.objects.get(source=WEATHER_SOURCE)
        self.assertEqual(snapshot.payload, self.payload)
        self.assertEqual(output.getvalue(), "")
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, WEATHER_DATA_URL)
        self.assertIn("ApartmanCvikov", request.get_header("User-agent"))
        self.assertEqual(mocked_urlopen.call_args.kwargs["timeout"], 10)

    @patch("apartmancvikov.management.commands.weather_sync.urlopen")
    def test_sync_reports_success_at_higher_verbosity(self, mocked_urlopen):
        """Verbosity level two reports a successful synchronization."""
        mocked_urlopen.return_value = FakeResponse(json.dumps(self.payload).encode())
        output = StringIO()

        call_command("weather_sync", verbosity=2, stdout=output)

        self.assertIn("ČHMÚ forecast updated", output.getvalue())

    def test_sync_failures_preserve_last_valid_forecast(self):
        """Download and validation failures keep the last valid snapshot."""
        snapshot = WeatherForecastSnapshot.objects.create(
            source=WEATHER_SOURCE,
            payload=self.payload,
            fetched_at=self.now,
        )
        failures = (
            FakeResponse(b"not json"),
            FakeResponse(json.dumps({"data": []}).encode()),
            FakeResponse(json.dumps(self.payload).encode(), status=503),
            TimeoutError("timed out"),
        )

        for failure in failures:
            with self.subTest(failure=failure):
                if isinstance(failure, BaseException):
                    mocked_result = patch(
                        "apartmancvikov.management.commands.weather_sync.urlopen",
                        side_effect=failure,
                    )
                else:
                    mocked_result = patch(
                        "apartmancvikov.management.commands.weather_sync.urlopen",
                        return_value=failure,
                    )
                with mocked_result, self.assertRaises(CommandError):
                    call_command("weather_sync", verbosity=0)
                snapshot.refresh_from_db()
                self.assertEqual(snapshot.payload, self.payload)
                self.assertEqual(snapshot.fetched_at, self.now)


class WeatherForecastTest(TestCase):
    def test_validation_accepts_missing_optional_values(self):
        """Optional model values may be absent from upstream data."""
        entry = forecast_entry(datetime(2026, 8, 14, 12, tzinfo=UTC))
        for field in ("icon", "prec", "windDirection", "windGustSpeed", "snow"):
            entry.pop(field)
        payload = forecast_payload(entry)

        self.assertIs(validate_weather_payload(payload), payload)

    def test_validation_rejects_invalid_or_unsorted_data(self):
        """Invalid values and time order are rejected before persistence."""
        first = datetime(2026, 8, 14, 12, tzinfo=UTC)
        cases = (
            {"data": []},
            forecast_payload(forecast_entry(first, t2m="warm")),
            forecast_payload(
                forecast_entry(first),
                forecast_entry(first - timedelta(hours=1)),
            ),
            forecast_payload(forecast_entry(first, validityTime="invalid")),
        )
        for payload in cases:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                validate_weather_payload(payload)

    def test_forecast_selects_current_point_and_aggregates_day_periods(self):
        """Hourly points are summarized into localized parts of the day."""
        now = datetime(2026, 8, 14, 4, 30, tzinfo=UTC)
        snapshot = WeatherForecastSnapshot(
            source=WEATHER_SOURCE,
            fetched_at=now - timedelta(minutes=20),
            payload=forecast_payload(
                forecast_entry(
                    datetime(2026, 8, 14, 3, tzinfo=UTC),
                    t2m=8,
                    prec=0,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 4, tzinfo=UTC),
                    t2m=9,
                    prec=0.1,
                    windSpeed=2,
                    cloudsTot=20,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 5, tzinfo=UTC),
                    t2m=7,
                    prec=0.2,
                    windSpeed=3,
                    cloudsTot=40,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 7, tzinfo=UTC),
                    t2m=11,
                    prec=0.3,
                    windSpeed=4,
                    cloudsTot=60,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 8, tzinfo=UTC),
                    t2m=12,
                    prec=0.4,
                    windSpeed=2,
                    cloudsTot=20,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 10, tzinfo=UTC),
                    t2m=16,
                    prec=0.1,
                    windSpeed=5,
                    cloudsTot=40,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 11, tzinfo=UTC),
                    t2m=14,
                    prec=0,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 15, tzinfo=UTC),
                    t2m=18,
                    prec=0.7,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 16, tzinfo=UTC),
                    t2m=13,
                    prec=0.1,
                ),
                forecast_entry(
                    datetime(2026, 8, 14, 21, tzinfo=UTC),
                    t2m=10,
                    prec=0.2,
                ),
                forecast_entry(datetime(2026, 8, 14, 22, tzinfo=UTC), t2m=9),
            ),
        )

        weather = build_weather_forecast(snapshot, now=now)

        self.assertTrue(weather["available"])
        self.assertEqual(weather["current"]["temperature"], 9)
        self.assertEqual(len(weather["days"]), 2)
        periods = weather["days"][0]["periods"]
        self.assertEqual(
            [period["key"] for period in periods],
            [
                "morning",
                "noon",
                "afternoon",
                "evening",
            ],
        )
        self.assertEqual(periods[0]["minimum"], 7)
        self.assertEqual(periods[0]["maximum"], 11)
        self.assertAlmostEqual(periods[0]["precipitation"], 0.6)
        self.assertEqual(periods[0]["wind_speed"], 4)
        self.assertEqual(periods[0]["clouds"], 40)
        self.assertEqual(periods[1]["minimum"], 12)
        self.assertEqual(periods[1]["maximum"], 16)
        self.assertAlmostEqual(periods[1]["precipitation"], 0.5)
        self.assertEqual(periods[2]["minimum"], 14)
        self.assertEqual(periods[2]["maximum"], 18)
        self.assertEqual(periods[3]["minimum"], 10)
        self.assertEqual(periods[3]["maximum"], 13)
        self.assertAlmostEqual(periods[3]["precipitation"], 0.3)
        self.assertEqual(weather["today_min"], 7)
        self.assertEqual(weather["today_max"], 18)

    def test_forecast_handles_dst_and_unknown_icon(self):
        """Repeated DST hours and unknown condition codes remain usable."""
        now = datetime(2026, 10, 25, 0, 30, tzinfo=UTC)
        snapshot = WeatherForecastSnapshot(
            source=WEATHER_SOURCE,
            fetched_at=now,
            payload=forecast_payload(
                forecast_entry(datetime(2026, 10, 25, 0, tzinfo=UTC), icon=999),
                forecast_entry(datetime(2026, 10, 25, 1, tzinfo=UTC), icon=999),
                forecast_entry(datetime(2026, 10, 25, 2, tzinfo=UTC), icon=999),
            ),
        )

        weather = build_weather_forecast(snapshot, now=now)

        hours = weather["days"][0]["hours"]
        self.assertEqual(str(weather["current"]["condition"]), "Neurčené počasí")
        self.assertEqual(weather["current"]["symbol"], "?")
        self.assertNotEqual(hours[0]["time"].utcoffset(), hours[1]["time"].utcoffset())

    def test_stale_and_expired_forecasts(self):
        """Old downloads are flagged and forecasts without future data expire."""
        now = datetime(2026, 8, 14, 12, 30, tzinfo=UTC)
        stale = WeatherForecastSnapshot(
            source=WEATHER_SOURCE,
            fetched_at=now - timedelta(hours=3),
            payload=forecast_payload(
                forecast_entry(now - timedelta(minutes=30)),
                forecast_entry(now + timedelta(minutes=30)),
            ),
        )
        expired = WeatherForecastSnapshot(
            source=WEATHER_SOURCE,
            fetched_at=now - timedelta(minutes=10),
            payload=forecast_payload(forecast_entry(now - timedelta(minutes=1))),
        )

        self.assertTrue(build_weather_forecast(stale, now=now)["stale"])
        self.assertFalse(build_weather_forecast(expired, now=now)["available"])


class WeatherPageTest(TestCase):
    def setUp(self):
        """Save enough hourly data to render several forecast periods."""
        self.now = timezone.now()
        first_hour = self.now.replace(minute=0, second=0, microsecond=0)
        WeatherForecastSnapshot.objects.create(
            source=WEATHER_SOURCE,
            fetched_at=self.now,
            payload=forecast_payload(
                *(
                    forecast_entry(
                        first_hour + timedelta(hours=offset),
                        icon=81 if offset == 0 else (999 if offset == 1 else 40),
                        t2m=11.6 + (offset % 8),
                        prec=0.2 if offset % 6 == 0 else 0,
                    )
                    for offset in range(-1, 37)
                ),
            ),
        )

    def test_detail_renders_full_forecast_and_provider_links(self):
        """The detail shows a compact table and all external providers."""
        response = self.client.get("/cs/pocasi/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Předpověď na příští tři dny")
        self.assertContains(response, "Déšť nebo přeháňky")
        for label in (
            "Teplota",
            "Ráno",
            "Poledne",
            "Odpoledne",
            "Večer",
            "min / max",
            "Celkové srážky",
            "Max. vítr",
            "Průměrná oblačnost",
        ):
            self.assertContains(response, label)
        for hidden_label in (
            "Sníh",
            "Nárazy větru",
            "Směr větru",
            "Vlhkost",
            "Tlak",
            "Nejnižší teplota",
            "Nejvyšší teplota",
            "Aktuálně",
            "Části dne",
            "Výhled po částech dne",
        ):
            self.assertNotContains(response, hidden_label)
        content = response.content.decode()
        self.assertContains(response, '<table class="weather-table">')
        self.assertGreaterEqual(content.count('class="weather-table__period"'), 4)
        self.assertNotContains(response, 'class="weather-day"')
        self.assertNotContains(response, 'class="weather-current"')
        self.assertNotContains(response, 'class="weather-hour"')
        self.assertRegex(content, r"\d+ / \d+ °C")
        self.assertNotContains(response, "11,6 °C")
        for url in (CHMI_FORECAST_URL, METEOBLUE_FORECAST_URL, YR_FORECAST_URL):
            self.assertContains(response, url)
        self.assertContains(response, 'rel="external noopener noreferrer"', count=3)
        self.assertNotContains(response, "<iframe")

    def test_home_renders_compact_model_summary(self):
        """The home page limits weather to condition and daily range."""
        response = self.client.get("/cs/")
        content = response.content.decode()

        self.assertContains(response, "Předpověď na dnešek")
        self.assertContains(response, "Déšť nebo přeháňky")
        self.assertRegex(content, r"\d+ až \d+ °C")
        self.assertEqual(content.count("°C"), 1)
        for detail in (
            "Modelová předpověď ALADIN",
            "Srážky",
            "Vítr",
            "Oblačnost",
            "12 °C",
        ):
            self.assertNotContains(response, detail)
        self.assertContains(response, 'href="/cs/pocasi/"')

    def test_weather_page_has_localized_seo_and_schema(self):
        """Every locale exposes canonical metadata and a WebPage schema."""
        for language, heading in (
            ("cs", "Počasí v\N{NO-BREAK SPACE}Cvikově"),
            ("en", "Weather in Cvikov"),
            ("de", "Wetter in Cvikov"),
        ):
            with self.subTest(language=language):
                response = self.client.get(f"/{language}/pocasi/")
                self.assertContains(response, heading)
                self.assertContains(
                    response,
                    f'<link rel="canonical" href="https://apartmancvikov.cz/{language}/pocasi/"',
                )
                graph = response.context["structured_data"]
                page = next(
                    node for node in graph["@graph"] if node["@type"] == "WebPage"
                )
                self.assertEqual(
                    page["url"], f"https://apartmancvikov.cz/{language}/pocasi/"
                )

    def test_missing_and_stale_snapshots_have_clear_statuses(self):
        """The detail explains stale and unavailable saved forecasts."""
        snapshot = WeatherForecastSnapshot.objects.get(source=WEATHER_SOURCE)
        snapshot.fetched_at = self.now - timedelta(hours=3)
        snapshot.save(update_fields=["fetched_at"])
        self.assertContains(
            self.client.get("/cs/pocasi/"),
            "Zobrazená data jsou starší než dvě hodiny",
        )

        snapshot.delete()
        unavailable = self.client.get("/cs/pocasi/")
        self.assertContains(unavailable, "Předpověď nyní není dostupná")
        self.assertContains(unavailable, CHMI_FORECAST_URL)
