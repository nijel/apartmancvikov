from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext as _

from .content import ATTRACTIONS, ATTRACTIONS_BY_SLUG
from .pricing import (
    PRICE_CURRENCY,
    STANDARD_ADULT_PRICE_CZK,
    STANDARD_CHILD_PRICE_CZK,
    STANDARD_INFANT_PRICE_CZK,
    STANDARD_PAID_PRICE_MAX_CZK,
    STANDARD_PAID_PRICE_MIN_CZK,
)

SITE_ID = f"{settings.SITE_URL}/#website"
OPERATOR_ID = f"{settings.SITE_URL}/#operator"
ACCOMMODATION_ID = f"{settings.SITE_URL}/#accommodation"
UNIT_ID = f"{settings.SITE_URL}/#accommodation-unit"

PROPERTY_IMAGES = (
    ("foto/dum.jpg", 1600, 1200),
    ("foto/tyrkys.jpg", 1600, 1064),
    ("foto/levandule.jpg", 1600, 1064),
    ("foto/fuchsie.jpg", 1600, 1064),
    ("foto/obyvak.jpg", 1600, 1064),
    ("foto/kuchyn.jpg", 1600, 1064),
    ("foto/koupelna-nahore.jpg", 1600, 1064),
    ("foto/terasa.jpg", 1600, 901),
)

EXTERNAL_PROFILES = (
    "https://maps.google.com/maps?cid=5382507699096848928",
    "https://www.firmy.cz/detail/13404124-apartman-cvikov-cvikov-ii.html",
    "https://www.facebook.com/apartman.cvikov/",
)

LANGUAGE_TAGS = {"cs": "cs-CZ", "en": "en", "de": "de"}


def _absolute(path):
    return f"{settings.SITE_URL}{path}"


def _page_url(request):
    return _absolute(request.path)


def _image_url(path):
    return _absolute(static(path))


def _operator_node():
    return {
        "@type": "Person",
        "@id": OPERATOR_ID,
        "name": "Petra Čihařová",
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "IČO",
            "value": "10843116",
        },
        "telephone": "+420775408751",
        "email": "ubytovani@apartmancvikov.cz",
    }


def _website_node():
    return {
        "@type": "WebSite",
        "@id": SITE_ID,
        "url": f"{settings.SITE_URL}/",
        "name": str(_("Apartmán Cvikov")),
        "inLanguage": ["cs-CZ", "en", "de"],
        "publisher": {"@id": OPERATOR_ID},
    }


def _lodging_node():
    return {
        "@type": "VacationRental",
        "@id": ACCOMMODATION_ID,
        "additionalType": "Apartment",
        "identifier": "apartman-cvikov-nabrezni-694",
        "name": str(_("Apartmán Cvikov")),
        "description": str(
            _(
                "Prostorný rodinný apartmán o ploše 180 m² ve Cvikově se "
                "třemi ložnicemi, zahradou, dětským vybavením a venkovním "
                "bazénem."
            )
        ),
        "url": _absolute(reverse("home")),
        "image": [_image_url(path) for path, _width, _height in PROPERTY_IMAGES],
        "telephone": "+420775408751",
        "email": "ubytovani@apartmancvikov.cz",
        "latitude": 50.77409,
        "longitude": 14.64013,
        "checkinTime": "15:00",
        "checkoutTime": "10:00",
        "knowsLanguage": ["cs-CZ", "en"],
        "owner": {"@id": OPERATOR_ID},
        "sameAs": list(EXTERNAL_PROFILES),
        "priceRange": (
            f"{STANDARD_PAID_PRICE_MIN_CZK}-{STANDARD_PAID_PRICE_MAX_CZK} "
            f"{PRICE_CURRENCY} per person per night"
        ),
        "makesOffer": [
            {"@id": f"{settings.SITE_URL}/#offer-adult"},
            {"@id": f"{settings.SITE_URL}/#offer-child"},
            {"@id": f"{settings.SITE_URL}/#offer-infant"},
        ],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Nábřežní 694",
            "addressLocality": "Cvikov",
            "addressRegion": "Liberecký kraj",
            "postalCode": "471 54",
            "addressCountry": "CZ",
        },
        "containsPlace": {
            "@type": ["Accommodation", "Product"],
            "@id": UNIT_ID,
            "additionalType": "EntirePlace",
            "occupancy": {"@type": "QuantitativeValue", "value": 9},
            "floorSize": {
                "@type": "QuantitativeValue",
                "value": 180,
                "unitCode": "MTK",
            },
            "numberOfRooms": 5,
            "numberOfBedrooms": 3,
            "numberOfBathroomsTotal": 2,
            "bed": [
                {"@type": "BedDetails", "numberOfBeds": 2, "typeOfBed": "Double"},
                {"@type": "BedDetails", "numberOfBeds": 3, "typeOfBed": "Single"},
                {
                    "@type": "BedDetails",
                    "numberOfBeds": 2,
                    "typeOfBed": "Floor mattress",
                },
            ],
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
                    "name": "internetType",
                    "value": "Free",
                },
                {
                    "@type": "LocationFeatureSpecification",
                    "name": "washerDryer",
                    "value": True,
                },
            ],
        },
    }


def _offer_node(identifier, name, description, price):
    return {
        "@type": "Offer",
        "@id": f"{settings.SITE_URL}/#{identifier}",
        "name": str(name),
        "description": str(description),
        "url": _absolute(reverse("cenik")),
        "businessFunction": "http://purl.org/goodrelations/v1#LeaseOut",
        "offeredBy": {"@id": ACCOMMODATION_ID},
        "itemOffered": {"@id": UNIT_ID},
        "priceSpecification": {
            "@type": "UnitPriceSpecification",
            "price": price,
            "priceCurrency": PRICE_CURRENCY,
            "priceType": "RegularPrice",
            "unitCode": "IE",
            "unitText": "person per night",
            "billingDuration": "P1D",
        },
    }


def _offer_nodes():
    exceptions = _(
        "U pobytů na jednu noc a v dalších nestandardních situacích se cena "
        "stanovuje individuálně."
    )
    return [
        _offer_node(
            "offer-adult",
            _("Standardní cena za dospělého"),
            _("%(price)s Kč za osobu a noc. %(exceptions)s")
            % {"price": STANDARD_ADULT_PRICE_CZK, "exceptions": exceptions},
            STANDARD_ADULT_PRICE_CZK,
        ),
        _offer_node(
            "offer-child",
            _("Standardní cena za dítě do 12 let"),
            _("%(price)s Kč za dítě a noc. %(exceptions)s")
            % {"price": STANDARD_CHILD_PRICE_CZK, "exceptions": exceptions},
            STANDARD_CHILD_PRICE_CZK,
        ),
        _offer_node(
            "offer-infant",
            _("Dítě do 3 let bez nároku na lůžko"),
            _("Dítě do 3 let bez nároku na lůžko má pobyt zdarma."),
            STANDARD_INFANT_PRICE_CZK,
        ),
    ]


def _image_node(path, width, height, caption, *, attraction=None):
    image_url = _image_url(path)
    node = {
        "@type": "ImageObject",
        "@id": f"{image_url}#image",
        "url": image_url,
        "contentUrl": image_url,
        "width": width,
        "height": height,
        "caption": str(caption),
    }
    if attraction and attraction.credit_name:
        node.update(
            {
                "creditText": attraction.credit_name,
                "creator": {
                    "@type": "Person",
                    "name": attraction.credit_name,
                },
                "license": attraction.license_url,
                "acquireLicensePage": attraction.credit_url,
            }
        )
    return node


def _page_metadata(view_name):
    metadata = {
        "home": (
            "WebPage",
            _("Apartmán Cvikov"),
            _(
                "Prostorný rodinný apartmán o ploše 180 m² ve Cvikově pro až "
                "devět hostů."
            ),
        ),
        "vylety": (
            "CollectionPage",
            _("Rodinné výlety z Apartmánu Cvikov"),
            _(
                "Deset ověřených tipů na rodinné výlety z Apartmánu Cvikov: "
                "pumptrack, vyhlídky, skály, hrady, sklárny, lyžování i "
                "program za deště."
            ),
        ),
        "cenik": (
            "WebPage",
            _("Ceník a podmínky Apartmánu Cvikov"),
            _(
                "Cena ubytování v Apartmánu Cvikov, zahrnuté vybavení, platební "
                "a storno podmínky a informace k příjezdu."
            ),
        ),
        "obsazenost": (
            "WebPage",
            _("Volné termíny v Apartmánu Cvikov"),
            _(
                "Kalendář volných a obsazených termínů Apartmánu Cvikov. "
                "Vyberte si termín rodinného pobytu v Lužických horách."
            ),
        ),
        "kontakt": (
            "ContactPage",
            _("Kontaktujte Apartmán Cvikov"),
            _(
                "Kontakt, telefon, e-mail, adresa a mapa Apartmánu Cvikov v "
                "Lužických horách."
            ),
        ),
    }
    return metadata[view_name]


def _webpage_node(request, metadata, image_node, main_entity):
    page_type, name, description = metadata
    page_url = _page_url(request)
    node = {
        "@type": page_type,
        "@id": f"{page_url}#webpage",
        "url": page_url,
        "name": str(name),
        "description": str(description),
        "inLanguage": LANGUAGE_TAGS.get(request.LANGUAGE_CODE, request.LANGUAGE_CODE),
        "isPartOf": {"@id": SITE_ID},
        "primaryImageOfPage": {"@id": image_node["@id"]},
    }
    if main_entity:
        node["mainEntity"] = {"@id": main_entity}
    else:
        node["about"] = {"@id": ACCOMMODATION_ID}
    return node


def _breadcrumb_node(request, items):
    return {
        "@type": "BreadcrumbList",
        "@id": f"{_page_url(request)}#breadcrumb",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "name": str(name),
                "item": url,
            }
            for position, (name, url) in enumerate(items, start=1)
        ],
    }


def _attraction_image_node(attraction):
    if not attraction.image:
        return _image_node(
            "foto/dum.jpg",
            1600,
            1200,
            _("Apartmán Cvikov se zahradou"),
        )
    return _image_node(
        attraction.image,
        attraction.image_width,
        attraction.image_height,
        attraction.name,
        attraction=attraction,
    )


def _attraction_node(request, attraction, image_node):
    page_url = _page_url(request)
    return {
        "@type": "TouristAttraction",
        "@id": f"{page_url}#attraction",
        "name": str(attraction.name),
        "description": str(attraction.description),
        "url": page_url,
        "image": {"@id": image_node["@id"]},
        "sameAs": attraction.official_url,
        "mainEntityOfPage": {"@id": f"{page_url}#webpage"},
    }


def _trip_list_node():
    list_url = _absolute(reverse("vylety"))
    return {
        "@type": "ItemList",
        "@id": f"{list_url}#item-list",
        "name": str(_("Výlety z Apartmánu Cvikov")),
        "numberOfItems": len(ATTRACTIONS),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": position,
                "item": {
                    "@type": "TouristAttraction",
                    "@id": f"{_absolute(reverse('attraction_detail', kwargs={'slug': item.slug}))}#attraction",
                    "name": str(item.name),
                    "url": _absolute(
                        reverse("attraction_detail", kwargs={"slug": item.slug})
                    ),
                    "image": _image_url(item.image) if item.image else None,
                },
            }
            for position, item in enumerate(ATTRACTIONS, start=1)
        ],
    }


def build_structured_data(request):
    """Build one linked JSON-LD graph for the current localized page."""
    match = request.resolver_match
    if match is None or match.url_name not in {
        "home",
        "vylety",
        "attraction_detail",
        "cenik",
        "obsazenost",
        "kontakt",
    }:
        return {"@context": "https://schema.org", "@graph": []}

    view_name = match.url_name
    nodes = [_website_node(), _operator_node(), _lodging_node(), *_offer_nodes()]
    home_url = _absolute(reverse("home"))

    if view_name == "attraction_detail":
        attraction = ATTRACTIONS_BY_SLUG[match.kwargs["slug"]]
        image_node = _attraction_image_node(attraction)
        attraction_node = _attraction_node(request, attraction, image_node)
        page_node = _webpage_node(
            request,
            ("WebPage", attraction.name, attraction.description),
            image_node,
            attraction_node["@id"],
        )
        breadcrumb = _breadcrumb_node(
            request,
            [
                (_("Ubytování"), home_url),
                (_("Výlety"), _absolute(reverse("vylety"))),
                (attraction.name, _page_url(request)),
            ],
        )
        nodes.extend([page_node, image_node, attraction_node, breadcrumb])
    else:
        page_type, name, description = _page_metadata(view_name)
        if view_name == "vylety":
            first_attraction = ATTRACTIONS[0]
            image_node = _attraction_image_node(first_attraction)
            item_list = _trip_list_node()
            main_entity = item_list["@id"]
        else:
            image_node = _image_node(
                "foto/dum.jpg",
                1600,
                1200,
                _("Apartmán Cvikov se zahradou"),
            )
            item_list = None
            main_entity = ACCOMMODATION_ID if view_name == "home" else None

        page_node = _webpage_node(
            request,
            (page_type, name, description),
            image_node,
            main_entity,
        )
        if view_name == "home":
            nodes[2]["mainEntityOfPage"] = {"@id": page_node["@id"]}
        nodes.extend([page_node, image_node])
        if item_list:
            nodes.append(item_list)
        if view_name != "home":
            nodes.append(
                _breadcrumb_node(
                    request,
                    [(_("Ubytování"), home_url), (name, _page_url(request))],
                )
            )

    return {"@context": "https://schema.org", "@graph": nodes}
