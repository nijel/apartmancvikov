# apartmancvikov

Website for Apartman Cvikov

## Development

Use Python 3.11 or newer and uv to install the locked dependencies, including
the development tools:

```sh
uv sync --locked
uv run --no-sync python manage.py compilemessages -v 0
uv run --no-sync python manage.py check
uv run --no-sync python manage.py test
uv run --no-sync python manage.py runserver
```

Compiling translations requires GNU gettext. Building mysqlclient requires a C
compiler, Python development headers, pkg-config, and MySQL client development
libraries.

Run the pre-commit hooks with:

```sh
uv run --locked --only-group pre-commit prek run --all-files
```

Declare runtime dependencies in `project.dependencies` and development tools in
`dependency-groups` in `pyproject.toml`. After changing dependencies, run `uv lock`
and include both `pyproject.toml` and `uv.lock` in the change. To update a locked
package within its declared constraints, use `uv lock --upgrade-package PACKAGE`.
CI checks Python 3.11, 3.12, 3.13, and 3.14 and rejects an outdated lock file.

For production, install only runtime dependencies:

```sh
uv sync --locked --no-dev
```

## Static files

Production uses Django's manifest static-files storage, which gives changed
CSS, JavaScript, images, and fonts content-hashed URLs. Run this after every
deployment so the templates and the collected files use the same manifest:

```sh
.venv/bin/python manage.py collectstatic --noinput
```

## E-mail delivery

Development uses Django's console e-mail backend and does not send real
messages. Configure authenticated SMTP in the untracked
`apartmancvikov/settings_local.py` on the production server:

```python
from apartmancvikov.site_config import CONTACT_EMAIL

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.example.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = CONTACT_EMAIL
EMAIL_HOST_PASSWORD = "replace-with-a-secret"
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = f"Apartmán Cvikov <{CONTACT_EMAIL}>"
```

The public recipient address and other business details are defined in
`apartmancvikov/site_config.py`. Never commit SMTP credentials.

## Availability calendar

The public iCalendar feed for synchronizing aggregated availability with
e-chalupy.cz and other booking services is available at
`https://apartmancvikov.cz/obsazenost.ics`. It contains no guest details.

## Weather forecast

The website reads the ČHMÚ ALADIN forecast from a database snapshot, so page
requests never wait for the upstream service. Apply migrations and refresh the
snapshot with:

```sh
.venv/bin/python manage.py weather_sync
```

Successful synchronization is silent by default. Use `-v 2` to print a success
confirmation.

Run this command every 30 minutes in production. For example, a cron entry can
use `*/30 * * * * cd /path/to/apartmancvikov && .venv/bin/python manage.py
weather_sync`. A failed download leaves the last valid snapshot untouched and
returns a non-zero status.
