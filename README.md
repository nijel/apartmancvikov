# apartmancvikov

Website for Apartman Cvikov

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
