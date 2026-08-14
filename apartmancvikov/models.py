# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from django.db import models


class Booking(models.Model):
    start = models.DateField()
    end = models.DateField()
    uid = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.start} - {self.end}: {self.uid}"


class WeatherForecastSnapshot(models.Model):
    source = models.CharField(max_length=50, unique=True)
    payload = models.JSONField()
    fetched_at = models.DateTimeField()

    def __str__(self):
        return f"{self.source}: {self.fetched_at}"
