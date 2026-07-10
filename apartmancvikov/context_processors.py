from django.conf import settings
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext as _
from django.utils.translation import override


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


def _lodging_schema():
    images = [
        "foto/dum.jpg",
        "foto/tyrkys.jpg",
        "foto/levandule.jpg",
        "foto/fuchsie.jpg",
        "foto/obyvak.jpg",
        "foto/kuchyn.jpg",
        "foto/koupelna-nahore.jpg",
        "foto/terasa.jpg",
    ]
    return {
        "@context": "https://schema.org",
        "@type": "VacationRental",
        "@id": f"{settings.SITE_URL}/#accommodation",
        "identifier": "apartman-cvikov-nabrezni-694",
        "name": str(_("Apartmán Cvikov")),
        "description": str(
            _(
                "Rodinné ubytování ve Cvikově se třemi ložnicemi, zahradou, "
                "dětským vybavením a venkovním bazénem."
            )
        ),
        "url": f"{settings.SITE_URL}/cs/",
        "image": [_absolute(static(image)) for image in images],
        "telephone": "+420775408751",
        "email": "ubytovani@apartmancvikov.cz",
        "latitude": 50.77409,
        "longitude": 14.64013,
        "checkinTime": "15:00",
        "checkoutTime": "10:00",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Nábřežní 694",
            "addressLocality": "Cvikov",
            "addressRegion": "Liberecký kraj",
            "postalCode": "471 54",
            "addressCountry": "CZ",
        },
        "containsPlace": {
            "@type": "Accommodation",
            "additionalType": "EntirePlace",
            "occupancy": {"@type": "QuantitativeValue", "value": 9},
            "numberOfBedrooms": 3,
            "numberOfBathroomsTotal": 2,
            "petsAllowed": False,
            "amenityFeature": [
                {
                    "@type": "LocationFeatureSpecification",
                    "name": "childFriendly",
                    "value": True,
                },
                {
                    "@type": "LocationFeatureSpecification",
                    "name": "parkingType",
                    "value": "Free",
                },
                {
                    "@type": "LocationFeatureSpecification",
                    "name": "poolType",
                    "value": "Outdoor",
                },
                {
                    "@type": "LocationFeatureSpecification",
                    "name": "wifi",
                    "value": True,
                },
                {
                    "@type": "LocationFeatureSpecification",
                    "name": "washerDryer",
                    "value": True,
                },
            ],
        },
    }


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
        "lodging_schema": _lodging_schema(),
    }
