# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from __future__ import annotations

from datetime import datetime, timedelta
from numbers import Real
from typing import Any

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import WeatherForecastSnapshot
from .site_config import PROPERTY_LATITUDE, PROPERTY_LONGITUDE

WEATHER_SOURCE = "chmi-aladin"
WEATHER_DATA_URL = (
    "https://data-provider.chmi.cz/api/graphs/graf.meteogram/"
    f"?x={PROPERTY_LONGITUDE}&y={PROPERTY_LATITUDE}"
)
CHMI_FORECAST_URL = "https://www.chmi.cz/meteogram/63-cvikov"
METEOBLUE_FORECAST_URL = (
    "https://www.meteoblue.com/en/weather/week/cvikov_czechia_3077318"
)
YR_FORECAST_URL = (
    "https://www.yr.no/en/forecast/daily-table/2-3077318/Czechia/"
    "Libereck%C3%BD%20kraj/%C4%8Cesk%C3%A1%20L%C3%ADpa%20District/Cvikov"
)
WEATHER_STALE_AFTER = timedelta(hours=2)

# Numeric icon meanings published by ČHMÚ and used by Aladin Online.
ICON_CONDITION_MAP = {
    10: "sunny",
    20: "sunny",
    40: "partly-cloudy",
    41: "rainy",
    43: "sleet",
    45: "snowy",
    46: "thunderstorm",
    60: "partly-cloudy",
    61: "rainy",
    62: "sleet",
    63: "sleet",
    64: "snowy",
    65: "snowy",
    66: "thunderstorm",
    69: "hail",
    70: "cloudy",
    71: "rainy",
    72: "sleet",
    73: "sleet",
    74: "snowy",
    75: "snowy",
    76: "thunderstorm",
    79: "hail",
    80: "cloudy",
    81: "rainy",
    82: "sleet",
    83: "sleet",
    84: "snowy",
    85: "snowy",
    86: "thunderstorm",
    89: "hail",
    90: "fog",
    91: "fog",
    92: "fog",
    93: "fog",
    94: "fog",
    110: "clear-night",
    120: "clear-night",
    140: "partly-cloudy",
    141: "rainy",
    143: "sleet",
    145: "snowy",
    146: "thunderstorm",
    160: "partly-cloudy",
    161: "rainy",
    162: "sleet",
    163: "sleet",
    164: "snowy",
    165: "snowy",
    166: "thunderstorm",
    169: "hail",
    170: "cloudy",
    171: "rainy",
    172: "sleet",
    173: "sleet",
    174: "snowy",
    175: "snowy",
    176: "thunderstorm",
    179: "hail",
}

CONDITION_PRESENTATION = {
    "sunny": (_("Jasno"), "☀️"),
    "clear-night": (_("Jasná noc"), "🌙"),
    "partly-cloudy": (_("Polojasno až oblačno"), "⛅"),
    "cloudy": (_("Zataženo"), "☁️"),
    "rainy": (_("Déšť nebo přeháňky"), "🌧️"),
    "sleet": (_("Déšť se sněhem nebo mrznoucí déšť"), "🌨️"),
    "snowy": (_("Sněžení"), "❄️"),
    "thunderstorm": (_("Bouřka"), "⛈️"),
    "hail": (_("Kroupy"), "🧊"),
    "fog": (_("Mlha"), "🌫️"),
    "unknown": (_("Neurčené počasí"), "?"),
}

DAY_PERIODS = (
    {
        "key": "morning",
        "label": _("Ráno"),
        "time_label": "00:00–10:00",
        "start": 0,
        "end": 10,
    },
    {
        "key": "noon",
        "label": _("Poledne"),
        "time_label": "10:00–13:00",
        "start": 10,
        "end": 13,
    },
    {
        "key": "afternoon",
        "label": _("Odpoledne"),
        "time_label": "13:00–18:00",
        "start": 13,
        "end": 18,
    },
    {
        "key": "evening",
        "label": _("Večer"),
        "time_label": "18:00–24:00",
        "start": 18,
        "end": 24,
    },
)

REQUIRED_NUMERIC_FIELDS = ("t2m", "rh2m", "mslp", "cloudsTot", "windSpeed")
OPTIONAL_NUMERIC_FIELDS = ("prec", "windDirection", "windGustSpeed", "snow")


def _parse_time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise TypeError("validityTime must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timezone.is_naive(parsed):
        raise ValueError("validityTime must include a timezone")
    return parsed


def _is_number(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def validate_weather_payload(payload: Any) -> dict[str, Any]:
    """Validate the upstream response before replacing the saved snapshot."""
    if not isinstance(payload, dict):
        raise TypeError("response must be an object")
    entries = payload.get("data")
    if not isinstance(entries, list) or not entries:
        raise ValueError("response must contain forecast data")

    previous_time = None
    for entry in entries:
        if not isinstance(entry, dict):
            raise TypeError("forecast entries must be objects")
        entry_time = _parse_time(entry.get("validityTime"))
        if previous_time is not None and entry_time <= previous_time:
            raise ValueError("forecast timestamps must be strictly increasing")
        previous_time = entry_time
        for field in REQUIRED_NUMERIC_FIELDS:
            if not _is_number(entry.get(field)):
                message = f"{field} must be numeric"
                raise ValueError(message)
        for field in OPTIONAL_NUMERIC_FIELDS:
            if field in entry and not _is_number(entry[field]):
                message = f"{field} must be numeric"
                raise ValueError(message)
        if "icon" in entry and (
            not isinstance(entry["icon"], int) or isinstance(entry["icon"], bool)
        ):
            raise ValueError("icon must be an integer")
    return payload


def _number(entry: dict[str, Any], key: str) -> Real | None:
    value = entry.get(key)
    return value if _is_number(value) else None


def _present_entry(entry: dict[str, Any], entry_time: datetime) -> dict[str, Any]:
    icon = entry.get("icon")
    condition_key = ICON_CONDITION_MAP.get(icon, "unknown")
    condition, symbol = CONDITION_PRESENTATION[condition_key]
    return {
        "time": timezone.localtime(entry_time),
        "condition": condition,
        "condition_key": condition_key,
        "symbol": symbol,
        "temperature": _number(entry, "t2m"),
        "humidity": _number(entry, "rh2m"),
        "precipitation": _number(entry, "prec"),
        "snow": _number(entry, "snow"),
        "wind_speed": _number(entry, "windSpeed"),
        "wind_gust": _number(entry, "windGustSpeed"),
        "wind_direction": _number(entry, "windDirection"),
        "pressure": _number(entry, "mslp"),
        "clouds": _number(entry, "cloudsTot"),
    }


def _period_summary(
    points: list[dict[str, Any]], period: dict[str, Any]
) -> dict[str, Any] | None:
    period_points = [
        point
        for point in points
        if period["start"] <= point["time"].hour < period["end"]
    ]
    if not period_points:
        return None

    temperatures = [
        point["temperature"]
        for point in period_points
        if point["temperature"] is not None
    ]
    precipitation = [
        point["precipitation"]
        for point in period_points
        if point["precipitation"] is not None
    ]
    winds = [
        point["wind_speed"]
        for point in period_points
        if point["wind_speed"] is not None
    ]
    clouds = [point["clouds"] for point in period_points if point["clouds"] is not None]
    representative = max(
        period_points,
        key=lambda point: (
            point["precipitation"] or 0,
            point["clouds"] or 0,
        ),
    )
    return {
        "key": period["key"],
        "label": period["label"],
        "time_label": period["time_label"],
        "minimum": min(temperatures) if temperatures else None,
        "maximum": max(temperatures) if temperatures else None,
        "precipitation": sum(precipitation) if precipitation else None,
        "wind_speed": max(winds) if winds else None,
        "clouds": sum(clouds) / len(clouds) if clouds else None,
        "condition": representative["condition"],
        "condition_key": representative["condition_key"],
        "symbol": representative["symbol"],
    }


def empty_weather(*, updated_at: datetime | None = None) -> dict[str, Any]:
    """Return the template context used when no current forecast is available."""
    return {
        "available": False,
        "stale": False,
        "updated_at": timezone.localtime(updated_at) if updated_at else None,
        "current": None,
        "days": (),
        "today_min": None,
        "today_max": None,
    }


def build_weather_forecast(
    snapshot: WeatherForecastSnapshot | None,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Convert a saved ALADIN response into localized display data."""
    if snapshot is None:
        return empty_weather()
    current_time = now or timezone.now()
    if timezone.is_naive(current_time):
        current_time = timezone.make_aware(current_time)

    if not isinstance(snapshot.payload, dict):
        return empty_weather(updated_at=snapshot.fetched_at)
    raw_entries = snapshot.payload.get("data")
    if not isinstance(raw_entries, list):
        return empty_weather(updated_at=snapshot.fetched_at)
    parsed_entries = []
    for entry in raw_entries:
        if not isinstance(entry, dict):
            continue
        try:
            entry_time = _parse_time(entry.get("validityTime"))
        except (TypeError, ValueError):
            continue
        parsed_entries.append((entry_time, entry))
    parsed_entries.sort(key=lambda item: item[0])

    future_indexes = [
        index
        for index, (entry_time, _entry) in enumerate(parsed_entries)
        if entry_time >= current_time
    ]
    if not future_indexes:
        return empty_weather(updated_at=snapshot.fetched_at)

    current_indexes = [
        index
        for index, (entry_time, _entry) in enumerate(parsed_entries)
        if entry_time <= current_time
    ]
    start_index = current_indexes[-1] if current_indexes else future_indexes[0]
    displayed = [
        _present_entry(entry, entry_time)
        for entry_time, entry in parsed_entries[start_index:]
    ]
    current = displayed[0]

    local_today = timezone.localtime(current_time).date()
    day_groups: list[dict[str, Any]] = []
    for point in displayed:
        point_date = point["time"].date()
        if not day_groups or day_groups[-1]["date"] != point_date:
            day_groups.append(
                {
                    "date": point_date,
                    "is_today": point_date == local_today,
                    "is_tomorrow": point_date == local_today + timedelta(days=1),
                    "hours": [],
                }
            )
        day_groups[-1]["hours"].append(point)

    for day in day_groups:
        temperatures = [
            point["temperature"]
            for point in day["hours"]
            if point["temperature"] is not None
        ]
        day["minimum"] = min(temperatures) if temperatures else None
        day["maximum"] = max(temperatures) if temperatures else None
        day["periods"] = tuple(
            summary
            for period in DAY_PERIODS
            if (summary := _period_summary(day["hours"], period)) is not None
        )

    today_temperatures = [
        point["temperature"]
        for point in displayed
        if point["time"].date() == local_today and point["temperature"] is not None
    ]
    return {
        "available": True,
        "stale": current_time - snapshot.fetched_at > WEATHER_STALE_AFTER,
        "updated_at": timezone.localtime(snapshot.fetched_at),
        "current": current,
        "days": day_groups,
        "today_min": min(today_temperatures) if today_temperatures else None,
        "today_max": max(today_temperatures) if today_temperatures else None,
    }


def get_weather_forecast(*, now: datetime | None = None) -> dict[str, Any]:
    """Load the saved forecast and convert it into template context."""
    snapshot = WeatherForecastSnapshot.objects.filter(source=WEATHER_SOURCE).first()
    return build_weather_forecast(snapshot, now=now)
