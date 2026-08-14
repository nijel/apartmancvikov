# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

import json
from http import HTTPStatus
from urllib.request import Request, urlopen

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apartmancvikov.models import WeatherForecastSnapshot
from apartmancvikov.weather import (
    WEATHER_DATA_URL,
    WEATHER_SOURCE,
    validate_weather_payload,
)

HTTP_TIMEOUT_SECONDS = 10
USER_AGENT = "ApartmanCvikov/1.0 (+https://apartmancvikov.cz/)"


class Command(BaseCommand):
    help = "refreshes the ČHMÚ ALADIN weather forecast"

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        """Download, validate, and save the latest ALADIN forecast."""
        request = Request(  # noqa: S310
            WEATHER_DATA_URL,
            headers={"User-Agent": USER_AGENT},
        )
        try:
            with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:  # noqa: S310
                status = response.status
                payload = json.load(response)
        except (OSError, json.JSONDecodeError) as error:
            message = f"Could not download ČHMÚ forecast: {error}"
            raise CommandError(message) from error

        if status != HTTPStatus.OK:
            message = f"ČHMÚ returned unexpected HTTP status {status}"
            raise CommandError(message)

        try:
            validate_weather_payload(payload)
        except (TypeError, ValueError) as error:
            message = f"ČHMÚ returned invalid forecast data: {error}"
            raise CommandError(message) from error

        with transaction.atomic():
            WeatherForecastSnapshot.objects.update_or_create(
                source=WEATHER_SOURCE,
                defaults={"payload": payload, "fetched_at": timezone.now()},
            )
        if int(options["verbosity"]) > 1:
            self.stdout.write(self.style.SUCCESS("ČHMÚ forecast updated"))
