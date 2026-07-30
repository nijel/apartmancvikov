# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

import json
import re
import time
from datetime import date, timedelta
from pathlib import Path
from smtplib import SMTPException
from unittest.mock import patch

from django.conf import settings
from django.core import mail, signing
from django.test import TestCase, override_settings
from django.utils.safestring import mark_safe

from .content import ATTRACTIONS, SWIMMING_TIPS
from .forms import FORM_TOKEN_SALT
from .image_config import variant_path
from .models import Booking
from .site_config import (
    CONTACT_EMAIL,
    CONTACT_PHONE_DISPLAY,
    MAX_GUESTS,
    OPERATOR_NAME,
    PRICE_CURRENCY,
    STANDARD_ADULT_PRICE_CZK,
    STANDARD_CHILD_PRICE_CZK,
    STANDARD_INFANT_PRICE_CZK,
    STANDARD_PAID_PRICE_MAX_CZK,
    STANDARD_PAID_PRICE_MIN_CZK,
)


class SeoTest(TestCase):
    languages = ("cs", "en", "de")

    def get_schema_graph(self, path):
        """Return the sole JSON-LD graph rendered for a page."""
        response = self.client.get(path)
        self.assertEqual(response.status_code, 200)
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            response.content.decode(),
            re.DOTALL,
        )
        self.assertEqual(len(scripts), 1)
        schema = json.loads(scripts[0])
        self.assertEqual(schema["@context"], "https://schema.org")
        return schema["@graph"]

    def schema_node(self, graph, node_type):
        """Find exactly one node of a given type in a JSON-LD graph."""
        nodes = [node for node in graph if node.get("@type") == node_type]
        self.assertEqual(len(nodes), 1)
        return nodes[0]

    def test_localized_pages_have_seo_metadata(self):
        """Localized home pages expose consistent SEO annotations."""
        for language in self.languages:
            with self.subTest(language=language):
                response = self.client.get(f"/{language}/")
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                canonical = f"https://apartmancvikov.cz/{language}/"
                self.assertIn(f'<html lang="{language}">', html)
                self.assertIn(f'<link rel="canonical" href="{canonical}"', html)
                self.assertIn('hreflang="cs"', html)
                self.assertIn('hreflang="en"', html)
                self.assertIn('hreflang="de"', html)
                self.assertIn('hreflang="x-default"', html)
                self.assertEqual(len(re.findall(r"<h1(?:\s|>)", html)), 1)
                self.assertEqual(html.count('name="description"'), 1)

    def test_supported_and_unsupported_languages(self):
        """Only the three translated language prefixes are accepted."""
        self.assertEqual(self.client.get("/cs/").status_code, 200)
        self.assertEqual(self.client.get("/en/").status_code, 200)
        self.assertEqual(self.client.get("/de/").status_code, 200)
        self.assertEqual(self.client.get("/fr/").status_code, 404)

    def test_pages_use_local_design_without_bootstrap(self):
        """The custom responsive design has no Bootstrap dependency."""
        response = self.client.get("/cs/")
        self.assertNotContains(response, "bootstrap")
        self.assertNotContains(response, "jsdelivr")
        self.assertContains(response, "/static/style.css")
        self.assertContains(response, "/static/site.js")
        self.assertContains(response, 'class="nav-menu"')
        self.assertContains(response, 'class="lightbox__image-stage"')
        self.assertContains(response, 'class="lightbox__zoom"')
        self.assertContains(response, 'class="lightbox__nav lightbox__nav--previous"')
        self.assertContains(response, 'class="lightbox__nav lightbox__nav--next"')

    def test_pages_render_responsive_images(self):
        """Photos have discoverable JPEG fallbacks and responsive WebP sources."""
        response = self.client.get("/cs/")
        html = response.content.decode()
        self.assertIn('<source type="image/webp"', html)
        self.assertIn('srcset="/static/responsive/foto/dum-480.jpg 480w,', html)
        self.assertIn('sizes="(min-width: 54rem) 50vw, 100vw"', html)
        self.assertIn('class="site-header__media"', html)
        self.assertIn('fetchpriority="high"', html)
        self.assertEqual(html.count('fetchpriority="high"'), 1)
        self.assertIn('content="index, follow, max-image-preview:large"', html)

    def test_home_links_selected_reviews_to_their_original_sources(self):
        """Selected review excerpts identify and link to their source portals."""
        response = self.client.get("/cs/")
        html = response.content.decode()

        self.assertEqual(html.count('class="review-card"'), 3)
        self.assertIn(
            "https://www.firmy.cz/detail/13404124-apartman-cvikov-cvikov-ii.html",
            html,
        )
        self.assertIn("https://www.e-chalupy.cz/apartman-cvikov-o16404", html)
        self.assertIn("https://www.google.com/maps?cid=5382507699096848928", html)
        self.assertIn('rel="external noopener noreferrer"', html)
        self.assertNotIn("<iframe", html)

    def test_responsive_image_paths_accept_template_safe_strings(self):
        """Django's quoted template arguments work with pathlib on Python 3.11."""
        self.assertEqual(
            variant_path(mark_safe("foto/dum.jpg"), 800, "webp"),
            "responsive/foto/dum-800.webp",
        )

    def test_availability_calendar_exposes_semantic_statuses(self):
        """Availability remains understandable without relying on color or CSS."""
        start = date.today() + timedelta(days=10)  # noqa: DTZ011
        end = start + timedelta(days=3)
        booking = Booking.objects.create(start=start, end=end, uid="private-booking")

        response = self.client.get("/cs/obsazenost/")
        html = response.content.decode()

        self.assertIn("<caption>", html)
        self.assertIn('scope="col"', html)
        self.assertIn('data-status="available"', html)
        self.assertIn('data-status="arrival"', html)
        self.assertIn('data-status="occupied"', html)
        self.assertIn('data-status="departure"', html)
        self.assertIn(f'<time datetime="{booking.start.isoformat()}">', html)
        self.assertIn("Začátek pobytu", html)
        self.assertIn("Konec pobytu", html)
        self.assertIn("Obsazeno", html)
        self.assertNotIn(booking.uid, html)

    def test_responsive_image_manifest_matches_committed_assets(self):
        """Every recorded derivative exists and source photos are represented."""
        static_dir = Path(settings.BASE_DIR) / "apartmancvikov" / "static"
        manifest_path = static_dir / "responsive" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        source_paths = {
            "bg.jpg",
            *(
                path.relative_to(static_dir).as_posix()
                for path in (static_dir / "foto").glob("*.jpg")
            ),
            *(
                path.relative_to(static_dir).as_posix()
                for path in (static_dir / "vylety").glob("*.jpg")
            ),
        }
        self.assertEqual(set(manifest["sources"]), source_paths)
        for relative in manifest["outputs"]:
            self.assertTrue((static_dir / relative).is_file(), relative)

    def test_heading_prepositions_do_not_wrap_alone(self):
        """Short Czech prepositions stay attached to the following word."""
        response = self.client.get("/cs/vylety/")
        self.assertContains(response, "Výlety z\N{NO-BREAK SPACE}Apartmánu Cvikov")
        self.assertContains(
            response,
            "Kam na\N{NO-BREAK SPACE}výlet ve\N{NO-BREAK SPACE}Cvikově "
            "a\N{NO-BREAK SPACE}okolí",
        )

    def test_all_attraction_pages_exist_in_all_languages(self):
        """Every curated guide renders for each supported language."""
        for language in self.languages:
            for attraction in ATTRACTIONS:
                with self.subTest(language=language, attraction=attraction.slug):
                    response = self.client.get(f"/{language}/vylety/{attraction.slug}/")
                    self.assertEqual(response.status_code, 200)
                    html = response.content.decode()
                    self.assertEqual(len(re.findall(r"<h1(?:\s|>)", html)), 1)
                    self.assertIn(str(attraction.official_url), html)

    def test_trip_guide_includes_swimming_tips(self):
        """One trip card opens the complete swimming guide."""
        overview = self.client.get("/cs/vylety/")
        self.assertContains(overview, 'href="/cs/vylety/koupani/"')
        self.assertNotContains(overview, 'class="swimming-card"')

        response = self.client.get("/cs/vylety/koupani/")
        html = response.content.decode()
        self.assertEqual(html.count('class="swimming-card"'), len(SWIMMING_TIPS))
        self.assertEqual(len(re.findall(r"<h1(?:\s|>)", html)), 1)
        self.assertContains(
            response,
            "/static/responsive/vylety/koupaliste-jonsdorf-480.webp",
        )
        for tip in SWIMMING_TIPS:
            with self.subTest(tip=tip.name):
                self.assertContains(response, tip.name)
                self.assertContains(response, tip.official_url)

    def test_swimming_tips_are_translated(self):
        """The dedicated guide remains useful in every supported language."""
        english = self.client.get("/en/vylety/koupani/")
        self.assertContains(english, "Swimming trips")
        self.assertContains(english, "Česká Kamenice municipal swimming pool")

        german = self.client.get("/de/vylety/koupani/")
        self.assertContains(german, "Badeausflüge")
        self.assertContains(german, "Städtisches Freibad Česká Kamenice")

    def test_unknown_attraction_returns_404(self):
        """Unknown attraction slugs do not create soft 404 pages."""
        response = self.client.get("/cs/vylety/nezname-misto/")
        self.assertEqual(response.status_code, 404)

    def test_licensed_photo_includes_attribution(self):
        """Third-party imagery links to its source and license."""
        response = self.client.get("/cs/vylety/duty-kamen/")
        self.assertContains(response, "/static/vylety/duty-kamen.jpg")
        self.assertContains(
            response, "https://commons.wikimedia.org/wiki/File:Koerner.jpg"
        )
        self.assertContains(response, "https://creativecommons.org/licenses/by-sa/3.0/")

    def test_structured_data_is_valid_json(self):
        """Attraction pages expose one linked graph with all expected entities."""
        graph = self.get_schema_graph("/cs/vylety/oybin/")
        lodging = self.schema_node(graph, "VacationRental")
        attraction = self.schema_node(graph, "TouristAttraction")
        page = self.schema_node(graph, "WebPage")
        breadcrumb = self.schema_node(graph, "BreadcrumbList")

        self.assertEqual(lodging["containsPlace"]["occupancy"]["value"], 9)
        self.assertEqual(page["mainEntity"]["@id"], attraction["@id"])
        self.assertEqual(attraction["mainEntityOfPage"]["@id"], page["@id"])
        self.assertEqual(len(breadcrumb["itemListElement"]), 3)

    def test_lodging_schema_contains_confirmed_property_details(self):
        """The rental entity publishes confirmed layout and identity details."""
        graph = self.get_schema_graph("/cs/")
        lodging = self.schema_node(graph, "VacationRental")
        accommodation = lodging["containsPlace"]

        self.assertEqual(lodging["additionalType"], "Apartment")
        self.assertEqual(accommodation["@type"], "Accommodation")
        self.assertNotIn('"Product"', json.dumps(graph))
        self.assertEqual(lodging["checkinTime"], "15:00")
        self.assertEqual(lodging["checkoutTime"], "10:00")
        self.assertEqual(lodging["knowsLanguage"], ["cs-CZ", "en"])
        self.assertEqual(
            lodging["sameAs"],
            [
                "https://maps.google.com/maps?cid=5382507699096848928",
                "https://www.firmy.cz/detail/13404124-apartman-cvikov-cvikov-ii.html",
                "https://www.e-chalupy.cz/apartman-cvikov-o16404",
                "https://www.facebook.com/apartman.cvikov/",
            ],
        )
        self.assertEqual(accommodation["floorSize"]["value"], 130)
        self.assertEqual(accommodation["floorSize"]["unitCode"], "MTK")
        self.assertEqual(accommodation["numberOfRooms"], 5)
        self.assertEqual(accommodation["numberOfBedrooms"], 3)
        self.assertEqual(accommodation["numberOfBathroomsTotal"], 2)
        self.assertEqual(
            accommodation["bed"],
            [
                {"@type": "BedDetails", "numberOfBeds": 2, "typeOfBed": "Double"},
                {"@type": "BedDetails", "numberOfBeds": 3, "typeOfBed": "Single"},
                {
                    "@type": "BedDetails",
                    "numberOfBeds": 2,
                    "typeOfBed": "Floor mattress",
                },
            ],
        )
        self.assertEqual(
            lodging["mainEntityOfPage"]["@id"],
            "https://apartmancvikov.cz/cs/#webpage",
        )

    def test_lodging_schema_contains_standard_prices(self):
        """Standard per-person rates are linked to the rental as qualified offers."""
        graph = self.get_schema_graph("/cs/cenik/")
        lodging = self.schema_node(graph, "VacationRental")
        service = self.schema_node(graph, "Service")
        operator = self.schema_node(graph, "Person")
        page = self.schema_node(graph, "WebPage")
        offers = [node for node in graph if node.get("@type") == "Offer"]

        self.assertEqual(len(offers), 3)
        self.assertNotIn("makesOffer", lodging)
        self.assertEqual(
            page["mainEntity"]["@id"],
            "https://apartmancvikov.cz/#accommodation-service",
        )
        self.assertEqual(service["provider"]["@id"], operator["@id"])
        self.assertEqual(
            {offer["@id"] for offer in service["offers"]},
            {
                "https://apartmancvikov.cz/#offer-adult",
                "https://apartmancvikov.cz/#offer-child",
                "https://apartmancvikov.cz/#offer-infant",
            },
        )
        self.assertEqual(
            lodging["priceRange"],
            f"{STANDARD_PAID_PRICE_MIN_CZK}-{STANDARD_PAID_PRICE_MAX_CZK} "
            f"{PRICE_CURRENCY} per person per night",
        )
        self.assertEqual(
            {offer["priceSpecification"]["price"] for offer in offers},
            {
                STANDARD_INFANT_PRICE_CZK,
                STANDARD_CHILD_PRICE_CZK,
                STANDARD_ADULT_PRICE_CZK,
            },
        )
        for offer in offers:
            price = offer["priceSpecification"]
            self.assertEqual(price["priceCurrency"], PRICE_CURRENCY)
            self.assertEqual(price["priceType"], "RegularPrice")
            self.assertEqual(price["unitCode"], "IE")
            self.assertEqual(price["billingDuration"], "P1D")
            self.assertEqual(
                offer["itemOffered"]["@id"],
                "https://apartmancvikov.cz/#accommodation-service",
            )
            self.assertEqual(offer["offeredBy"]["@id"], operator["@id"])

        home_graph = self.get_schema_graph("/cs/")
        home_lodging = self.schema_node(home_graph, "VacationRental")
        self.assertNotIn("makesOffer", home_lodging)
        self.assertFalse(
            any(node.get("@type") == "Offer" for node in home_graph),
        )

        response = self.client.get("/cs/cenik/")
        self.assertContains(
            response,
            f"Standardní cena za dospělého je {STANDARD_ADULT_PRICE_CZK},- Kč",
        )
        self.assertContains(
            response,
            f"standardní cena {STANDARD_CHILD_PRICE_CZK},- Kč za noc",
        )
        self.assertContains(response, "v dalších nestandardních situacích")
        self.assertNotContains(response, "Silvestr")
        self.assertNotIn("Silvestr", json.dumps(graph, ensure_ascii=False))

    def test_page_specific_schema_types(self):
        """Static and listing pages identify their role and main entity."""
        cases = (
            ("/cs/vylety/", "CollectionPage", "ItemList", len(ATTRACTIONS) + 1),
            (
                "/cs/vylety/koupani/",
                "CollectionPage",
                "ItemList",
                len(SWIMMING_TIPS),
            ),
            ("/cs/kontakt/", "ContactPage", None, None),
            ("/cs/poptavka/", "WebPage", None, None),
            ("/cs/cenik/", "WebPage", "Service", None),
            ("/cs/obsazenost/", "WebPage", None, None),
            ("/cs/ochrana-osobnich-udaju/", "WebPage", None, None),
            ("/cs/podminky-uziti-fotografii/", "WebPage", None, None),
        )
        for path, page_type, main_type, expected_count in cases:
            with self.subTest(path=path):
                graph = self.get_schema_graph(path)
                page = self.schema_node(graph, page_type)
                self.schema_node(graph, "BreadcrumbList")
                if main_type:
                    main = self.schema_node(graph, main_type)
                    self.assertEqual(page["mainEntity"]["@id"], main["@id"])
                    if main_type == "ItemList":
                        self.assertEqual(main["numberOfItems"], expected_count)
                else:
                    self.assertEqual(
                        page["about"]["@id"],
                        "https://apartmancvikov.cz/#accommodation",
                    )

    def test_schema_is_localized_without_external_review_markup(self):
        """Localized graphs do not republish ratings from third-party profiles."""
        for language, language_tag in (("cs", "cs-CZ"), ("en", "en"), ("de", "de")):
            with self.subTest(language=language):
                graph = self.get_schema_graph(f"/{language}/")
                page = self.schema_node(graph, "WebPage")
                schema_text = json.dumps(graph)
                self.assertEqual(page["inLanguage"], language_tag)
                self.assertNotIn("AggregateRating", schema_text)
                self.assertNotIn('"Review"', schema_text)

    def test_licensed_image_has_machine_readable_attribution(self):
        """Licensed attraction photography carries source and license metadata."""
        graph = self.get_schema_graph("/cs/vylety/duty-kamen/")
        image = self.schema_node(graph, "ImageObject")
        self.assertEqual(image["creditText"], "Lutz Maertens")
        self.assertEqual(
            image["license"], "https://creativecommons.org/licenses/by-sa/3.0/"
        )
        self.assertEqual(
            image["acquireLicensePage"],
            "https://commons.wikimedia.org/wiki/File:Koerner.jpg",
        )
        self.assertEqual(image["copyrightNotice"], "© Lutz Maertens")

    def test_own_image_has_machine_readable_authorship(self):
        """Property photography identifies the operator as its rights holder."""
        graph = self.get_schema_graph("/cs/")
        image = self.schema_node(graph, "ImageObject")
        operator = self.schema_node(graph, "Person")
        self.assertEqual(image["creditText"], "Apartmán Cvikov")
        self.assertEqual(image["creator"]["@id"], operator["@id"])
        self.assertEqual(image["copyrightHolder"]["@id"], operator["@id"])
        self.assertEqual(image["copyrightNotice"], f"© {OPERATOR_NAME}")
        self.assertEqual(
            image["license"],
            "https://apartmancvikov.cz/cs/podminky-uziti-fotografii/",
        )
        self.assertEqual(
            image["acquireLicensePage"],
            "https://apartmancvikov.cz/cs/kontakt/",
        )
        license_page = self.client.get("/cs/podminky-uziti-fotografii/")
        self.assertContains(license_page, f"© {OPERATOR_NAME}")
        self.assertNotContains(license_page, "© Apartmán Cvikov")

    def test_sitemap_contains_all_localized_urls(self):
        """The sitemap contains each static and attraction language variant."""
        response = self.client.get(
            "/sitemap.xml", headers={"host": "apartmancvikov.cz"}, secure=True
        )
        self.assertEqual(response.status_code, 200)
        sitemap = response.content.decode()
        locations = re.findall(r"<loc>(.*?)</loc>", sitemap)
        self.assertEqual(len(locations), 57)
        self.assertIn("https://apartmancvikov.cz/cs/", locations)
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/koupani/",
            locations,
        )
        self.assertIn(
            "https://apartmancvikov.cz/de/vylety/motyli-dum-jonsdorf/", locations
        )
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/pumptrack-cvikov/", locations
        )
        self.assertIn("https://apartmancvikov.cz/cs/ochrana-osobnich-udaju/", locations)
        self.assertIn(
            "https://apartmancvikov.cz/cs/podminky-uziti-fotografii/", locations
        )
        self.assertIn("https://apartmancvikov.cz/cs/poptavka/", locations)
        self.assertIn(
            'hreflang="x-default" href="https://apartmancvikov.cz/cs/vylety/oybin/"',
            sitemap,
        )
        self.assertIn(
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"',
            sitemap,
        )
        self.assertIn(
            "<image:loc>https://apartmancvikov.cz/static/vylety/duty-kamen.jpg</image:loc>",
            sitemap,
        )
        self.assertIn(
            "<image:loc>https://apartmancvikov.cz/static/vylety/"
            "koupaliste-jonsdorf.jpg</image:loc>",
            sitemap,
        )

    def test_machine_readable_endpoints(self):
        """Robots and agent summaries publish their essential information."""
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertContains(
            robots,
            "Content-Signal: search=yes, ai-input=yes, ai-train=no",
        )
        self.assertContains(robots, "Sitemap: https://apartmancvikov.cz/sitemap.xml")
        self.assertContains(robots, "Disallow: /admin/")

        llms = self.client.get("/llms.txt")
        self.assertEqual(llms.status_code, 200)
        self.assertContains(llms, "Spacious 130 m² apartment with 3 bedrooms")
        self.assertContains(llms, "2 additional floor mattresses")
        self.assertContains(llms, "https://apartmancvikov.cz/cs/vylety/")
        self.assertContains(
            llms,
            "https://apartmancvikov.cz/cs/vylety/koupani/",
        )
        self.assertContains(llms, "https://apartmancvikov.cz/cs/poptavka/")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL=CONTACT_EMAIL,
)
class ContactInquiryTest(TestCase):
    def inquiry_data(self, **overrides):
        """Return a valid inquiry payload with optional field overrides."""
        arrival = date.today() + timedelta(days=14)  # noqa: DTZ011
        data = {
            "name": "Jana Nováková",
            "email": "jana@example.com",
            "phone": "+420 123 456 789",
            "arrival": arrival.isoformat(),
            "departure": (arrival + timedelta(days=4)).isoformat(),
            "adults": 2,
            "children": 1,
            "infants": 0,
            "message": "Prosím o potvrzení dostupnosti.",
            "website": "",
            "started_at": signing.dumps(
                {"started": time.time() - 5}, salt=FORM_TOKEN_SALT
            ),
        }
        data.update(overrides)
        return data

    def test_inquiry_page_exposes_structured_form(self):
        """The inquiry page exposes semantic stay and guest fields."""
        response = self.client.get("/cs/poptavka/")

        self.assertContains(response, 'name="arrival"')
        self.assertContains(response, 'name="departure"')
        self.assertContains(response, 'name="adults"')
        self.assertContains(response, 'name="children"')
        self.assertContains(response, 'name="infants"')
        self.assertContains(response, "Zkontrolovat obsazenost")

    def test_primary_navigation_links_directly_to_inquiry(self):
        """The main navigation makes the inquiry action prominent."""
        response = self.client.get("/cs/")

        self.assertContains(
            response,
            'class="nav-links__inquiry"',
        )
        self.assertContains(response, 'href="/cs/poptavka/"')
        self.assertContains(response, "Poptat pobyt")

        contact = self.client.get("/cs/kontakt/")
        self.assertContains(contact, 'href="/cs/poptavka/"')
        self.assertNotContains(contact, 'name="arrival"')
        self.assertContains(contact, CONTACT_EMAIL)
        self.assertContains(contact, CONTACT_PHONE_DISPLAY)

    def test_valid_inquiry_sends_one_message_to_central_contact(self):
        """A valid inquiry reaches only the configured contact address."""
        response = self.client.post("/cs/poptavka/", self.inquiry_data(), follow=True)

        self.assertRedirects(response, "/cs/poptavka/")
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, [CONTACT_EMAIL])
        self.assertEqual(message.from_email, CONTACT_EMAIL)
        self.assertEqual(message.reply_to, ["jana@example.com"])
        self.assertIn("Jana Nováková", message.body)
        self.assertIn("Prosím o potvrzení dostupnosti.", message.body)

        self.assertContains(response, "Děkujeme, poptávka byla odeslána")

    def test_capacity_and_dates_are_validated_without_sending(self):
        """Invalid dates and excessive capacity never produce an e-mail."""
        yesterday = date.today() - timedelta(days=1)  # noqa: DTZ011
        response = self.client.post(
            "/cs/poptavka/",
            self.inquiry_data(
                arrival=yesterday.isoformat(),
                departure=yesterday.isoformat(),
                adults=MAX_GUESTS,
                children=1,
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Datum příjezdu nemůže být v minulosti")
        self.assertContains(response, "Datum odjezdu musí být později")
        self.assertContains(response, "kapacitu nejvýše")
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_does_not_send_message(self):
        """A filled honeypot receives a generic success without an e-mail."""
        response = self.client.post(
            "/cs/poptavka/", self.inquiry_data(website="https://spam.example")
        )

        self.assertRedirects(response, "/cs/poptavka/")
        self.assertEqual(len(mail.outbox), 0)

    def test_too_fast_submission_is_rejected(self):
        """An implausibly quick submission is rejected before sending."""
        response = self.client.post(
            "/cs/poptavka/",
            self.inquiry_data(
                started_at=signing.dumps({"started": time.time()}, salt=FORM_TOKEN_SALT)
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Formulář byl odeslán příliš rychle")
        self.assertEqual(len(mail.outbox), 0)

    @patch("apartmancvikov.views.EmailMessage.send", side_effect=SMTPException)
    def test_smtp_failure_keeps_form_and_shows_error(self, _send):
        """SMTP failure preserves values and does not claim success."""
        with self.assertLogs("apartmancvikov.views", level="ERROR"):
            response = self.client.post("/cs/poptavka/", self.inquiry_data())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Poptávku se nepodařilo odeslat")
        self.assertContains(response, "Jana Nováková")
        self.assertEqual(len(mail.outbox), 0)

    def test_privacy_page_describes_retention_without_consent_checkbox(self):
        """The privacy notice explains retention without needless consent."""
        response = self.client.get("/cs/ochrana-osobnich-udaju/")

        self.assertContains(response, "nejdéle 6 měsíců")
        self.assertContains(response, CONTACT_EMAIL)
        self.assertNotContains(response, 'type="checkbox"')
