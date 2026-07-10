from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.utils.translation import override

from .site_config import (
    ADDRESS_LOCALITY,
    ADDRESS_POSTAL_CODE,
    ADDRESS_STREET,
    CONTACT_EMAIL,
    CONTACT_PHONE,
    CONTACT_PHONE_DISPLAY,
    OPERATOR_ID_NUMBER,
    OPERATOR_NAME,
    PRICE_CURRENCY,
    STANDARD_ADULT_PRICE_CZK,
    STANDARD_CHILD_PRICE_CZK,
    STANDARD_INFANT_PRICE_CZK,
)
from .structured_data import build_structured_data


def _absolute(path):
    return f"{settings.SITE_URL}{path}"


def _localized_urls(request):
    match = request.resolver_match
    if match is None or not match.view_name:
        return []

    result = []
    for code, name in settings.LANGUAGES:
        try:
            with override(code):
                path = reverse(match.view_name, kwargs=match.kwargs)
        except NoReverseMatch:
            return []
        result.append({"code": code, "name": name, "url": _absolute(path)})
    return result


def seo(request):
    """Provide canonical URLs, language alternatives, and lodging metadata."""
    language_urls = _localized_urls(request)
    canonical_url = ""
    for item in language_urls:
        if item["code"] == request.LANGUAGE_CODE:
            canonical_url = item["url"]
            break

    return {
        "canonical_url": canonical_url,
        "language_urls": language_urls,
        "x_default_url": next(
            (item["url"] for item in language_urls if item["code"] == "cs"),
            "",
        ),
        "og_locale": {"cs": "cs_CZ", "en": "en_GB", "de": "de_DE"}.get(
            request.LANGUAGE_CODE, "cs_CZ"
        ),
        "site_url": settings.SITE_URL,
        "privacy_url": reverse("privacy"),
        "prices": {
            "adult": STANDARD_ADULT_PRICE_CZK,
            "child": STANDARD_CHILD_PRICE_CZK,
            "infant": STANDARD_INFANT_PRICE_CZK,
            "currency": PRICE_CURRENCY,
        },
        "contact": {
            "email": CONTACT_EMAIL,
            "phone": CONTACT_PHONE,
            "phone_display": CONTACT_PHONE_DISPLAY,
            "street": ADDRESS_STREET,
            "postal_code": ADDRESS_POSTAL_CODE,
            "locality": ADDRESS_LOCALITY,
            "operator_name": OPERATOR_NAME,
            "operator_id_number": OPERATOR_ID_NUMBER,
        },
        "structured_data": build_structured_data(request),
    }
