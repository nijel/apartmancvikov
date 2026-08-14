# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apartmancvikov", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WeatherForecastSnapshot",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("source", models.CharField(max_length=50, unique=True)),
                ("payload", models.JSONField()),
                ("fetched_at", models.DateTimeField()),
            ],
        ),
    ]
