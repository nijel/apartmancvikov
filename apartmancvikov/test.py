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
from django.templatetags.static import static
from django.test import TestCase, override_settings
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from icalendar import Calendar

from .availability import maximum_inquiry_date
from .content import ATTRACTIONS, CYCLING_TRIPS, SWIMMING_TIPS
from .forms import FORM_TOKEN_SALT
from .image_config import variant_path
from .models import Booking
from .restaurants import RESTAURANTS
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
        self.assertContains(response, static("style.css"))
        self.assertContains(response, static("site.js"))
        self.assertRegex(static("style.css"), r"^/static/style\.[0-9a-f]{12}\.css$")
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
        self.assertIn(
            f'srcset="{static("responsive/foto/dum-480.jpg")} 480w,',
            html,
        )
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

    def test_single_day_event_shows_departure_on_following_morning(self):
        """A one-day calendar event also occupies the next morning."""
        start = date.today() + timedelta(days=10)  # noqa: DTZ011
        following_day = start + timedelta(days=1)
        Booking.objects.create(start=start, end=start, uid="one-day-event")

        html = self.client.get("/cs/obsazenost/").content.decode()

        self.assertIn(
            f'class="booking_start" data-status="arrival"><time datetime="{start}">',
            html,
        )
        self.assertIn(
            f'class="booking_end" data-status="departure"><time '
            f'datetime="{following_day}">',
            html,
        )

    def test_ical_feed_matches_aggregated_calendar_periods(self):
        """The iCalendar feed merges adjoining bookings and gaps like HTML."""
        start = date.today() + timedelta(days=10)  # noqa: DTZ011
        first_end = start + timedelta(days=3)
        gap = start + timedelta(days=4)
        joined_start = start + timedelta(days=5)
        joined_end = start + timedelta(days=7)
        separate_start = start + timedelta(days=10)
        separate_end = start + timedelta(days=12)
        Booking.objects.create(
            start=joined_start,
            end=joined_end,
            uid="private-joined-booking",
        )
        Booking.objects.create(
            start=separate_start,
            end=separate_end,
            uid="private-separate-booking",
        )
        Booking.objects.create(
            start=start,
            end=first_end,
            uid="private-first-booking",
        )

        html = self.client.get("/cs/obsazenost/").content.decode()
        response = self.client.get("/obsazenost.ics")
        calendar_text = response.content.decode()
        calendar = Calendar.from_ical(response.content)
        events = calendar.walk("VEVENT")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["Content-Type"], "text/calendar; charset=utf-8"
        )
        self.assertEqual(
            response.headers["Content-Disposition"],
            'inline; filename="apartman-cvikov-obsazenost.ics"',
        )
        self.assertTrue(calendar_text.startswith("BEGIN:VCALENDAR\r\n"))
        self.assertTrue(calendar_text.endswith("END:VCALENDAR\r\n"))
        self.assertEqual(len(events), 2)
        self.assertEqual(
            [(event.decoded("dtstart"), event.decoded("dtend")) for event in events],
            [(start, joined_end), (separate_start, separate_end)],
        )
        self.assertEqual(
            str(events[0]["uid"]),
            f"obsazenost-{start:%Y%m%d}-{joined_end:%Y%m%d}@apartmancvikov.cz",
        )
        self.assertEqual(str(events[0]["summary"]), "Obsazeno")
        self.assertNotIn("private-first-booking", calendar_text)
        self.assertNotIn("private-joined-booking", calendar_text)
        self.assertNotIn("ATTENDEE", calendar_text)
        self.assertIn(
            f'class="booking_middle" data-status="occupied"><time datetime="{gap}">',
            html,
        )
        self.assertIn(
            f'class="booking_middle" data-status="occupied"><time '
            f'datetime="{joined_start}">',
            html,
        )

    def test_single_day_event_has_next_day_as_ical_end(self):
        """A one-day source event exports as one overnight iCalendar stay."""
        start = date.today() + timedelta(days=10)  # noqa: DTZ011
        following_day = start + timedelta(days=1)
        Booking.objects.create(start=start, end=start, uid="private-one-day-event")

        response = self.client.get("/obsazenost.ics")
        events = Calendar.from_ical(response.content).walk("VEVENT")

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].decoded("dtstart"), start)
        self.assertEqual(events[0].decoded("dtend"), following_day)
        self.assertNotIn("private-one-day-event", response.content.decode())

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
                    self.assertIn(escape(str(attraction.official_url)), html)

    def test_walking_loop_length_is_not_presented_as_distance(self):
        """A complete walking circuit is clearly distinguished from distance."""
        overview = self.client.get("/cs/vylety/")
        self.assertContains(overview, "Délka pěšího okruhu: 8,7 km")
        self.assertContains(overview, "Délka pěšího okruhu: 4,5 km")
        self.assertNotContains(overview, "Přibližně 8,7 km od apartmánu")
        self.assertNotContains(overview, "Přibližně 4,5 km od apartmánu")

        detail = self.client.get("/cs/vylety/cvikovske-vyhlidky/")
        self.assertContains(detail, "Délka okruhu")

        shortened_route = self.client.get("/cs/vylety/duty-kamen/")
        self.assertContains(shortened_route, "zkrácenou variantou")
        self.assertContains(shortened_route, "https://mapy.com/s/madepucoso")

    def test_pumptrack_has_cycling_distance_and_nearby_facilities(self):
        """The pump track guide states the travel mode and adjacent amenities."""
        overview = self.client.get("/cs/vylety/")
        self.assertContains(overview, "Na kole od apartmánu: 1,3 km")
        self.assertNotContains(overview, "Přibližně 1,3 km od apartmánu")

        detail = self.client.get("/cs/vylety/pumptrack-cvikov/")
        self.assertContains(detail, "Vzdálenost na kole")
        self.assertContains(detail, "https://mapy.com/s/dezohapela")
        for facility in (
            "velké dětské hřiště",
            "workoutové hřiště",
            "atletický ovál",
            "občerstvení",
            "placené vzduchové trampolíny",
        ):
            self.assertContains(detail, facility)

    def test_driving_distances_are_labeled(self):
        """Distances measured by car are labeled in the overview and detail."""
        overview = self.client.get("/cs/vylety/")
        self.assertContains(overview, "Autem od apartmánu: 8 km")
        self.assertContains(overview, "Autem od apartmánu: 6 km")
        self.assertContains(overview, "Autem od apartmánu: 17 km")
        self.assertContains(overview, "Autem od apartmánu: 15 km")

        sloup_detail = self.client.get("/cs/vylety/skalni-hrad-sloup/")
        self.assertContains(sloup_detail, "Vzdálenost autem")
        self.assertContains(sloup_detail, "možné dojet také autobusem")
        self.assertContains(sloup_detail, "https://mapy.com/s/judatacovu")

        ajeto_detail = self.client.get("/cs/vylety/ajeto-lindava/")
        self.assertContains(ajeto_detail, "Vzdálenost autem")
        self.assertContains(ajeto_detail, "https://mapy.com/s/budufokado")

        oybin_detail = self.client.get("/cs/vylety/oybin/")
        self.assertContains(oybin_detail, "Vzdálenost autem")
        self.assertContains(oybin_detail, "17 km")
        self.assertContains(oybin_detail, "https://mapy.com/s/locacosoge")

        exotenhaus_detail = self.client.get("/cs/vylety/motyli-dum-jonsdorf/")
        self.assertContains(exotenhaus_detail, "Vzdálenost autem")
        self.assertContains(exotenhaus_detail, "15 km")
        self.assertContains(exotenhaus_detail, "https://mapy.com/s/mamubazode")

    def test_pacinek_uses_supplied_map(self):
        """Pačinek Glass links to the supplied map."""
        detail = self.client.get("/cs/vylety/pacinek-glass/")
        self.assertContains(detail, "https://mapy.com/s/fejukapobu")

    def test_klic_shows_drive_and_walking_loop_distances(self):
        """Klíč distinguishes the drive from the following walking loop."""
        overview = self.client.get("/cs/vylety/")
        self.assertContains(overview, "Autem od apartmánu: 6 km")
        self.assertContains(overview, "Délka pěšího okruhu: 2,8 km")

        detail = self.client.get("/cs/vylety/klic/")
        self.assertContains(detail, "Vzdálenost autem")
        self.assertContains(detail, "6 km")
        self.assertContains(detail, "Délka okruhu")
        self.assertContains(detail, "2,8 km")
        self.assertContains(detail, "https://mapy.com/s/masavogaza")

    def test_polevsko_has_driving_distance_and_summer_tips(self):
        """Polevsko includes the parking route and summer activities."""
        overview = self.client.get("/cs/vylety/")
        self.assertContains(overview, "Autem od apartmánu: 12 km")

        detail = self.client.get("/cs/vylety/polevsko/")
        self.assertContains(detail, "Vzdálenost autem")
        self.assertContains(detail, "https://mapy.com/s/gunedatolu")
        self.assertContains(detail, "Za polevskými obry")
        self.assertContains(detail, "mohutné stromy")
        self.assertContains(detail, "bikepark")

    def test_existing_trips_include_extended_descriptions_from_guest_documents(self):
        """Guest handouts enrich matching trip pages with reusable detail."""
        expected_details = {
            "cvikovske-vyhlidky": (
                "Johann Franz Richter",
                "lesního divadla",
                "Schillerově vyhlídce",
            ),
            "duty-kamen": (
                "600 metrů dlouhý",
                "Karolínin odpočinek",
                "Theodora Körnera",
            ),
            "skalni-hrad-sloup": (
                "více než třicet metrů",
                "barokní úpravy",
            ),
            "pacinek-glass": (
                "Skleněné květy",
                "tradiční sklářská huť",
            ),
            "klic": (
                "Kamzičí studánku",
                "kamenné moře",
            ),
            "polevsko": (
                "trasy pro zkušenější jezdce i děti",
                "pastvinám",
            ),
            "motyli-dum-jonsdorf": (
                "bezbariérová",
                "Gondelfahrt",
                "horském koupališti",
            ),
        }
        for slug, details in expected_details.items():
            with self.subTest(slug=slug):
                response = self.client.get(f"/cs/vylety/{slug}/")
                for detail in details:
                    self.assertContains(response, detail)

    def test_new_guest_document_trips_have_routes_photos_and_practical_data(self):
        """The eight added handout trips render their supplied planning details."""
        expected = {
            "kunraticke-svycarsko": (
                "https://mapy.com/s/bupomahunu",
                "8 km",
                "Karlův odpočinek",
            ),
            "panska-skala": (
                "https://mapy.com/s/nupocenega",
                "13 km",
                "parkovné 70 Kč",
            ),
            "sloni-kameny": (
                "https://mapy.com/s/bokedakepe",
                "2 km",
                "zakázáno lézt přímo na skály",
            ),
            "hvozd": (
                "https://mapy.com/s/hacajetave",
                "6,5 km",
                "také autobusem",
            ),
            "loreta-rumburk": (
                "https://mapy.com/s/fokuhejoko",
                "31 km",
                "Dospělý 80 Kč",
            ),
            "transborder-chrastava": (
                "https://mapy.com/s/latagomabe",
                "8,3 km",
                "vlastní silou",
            ),
            "lesopark-horka": (
                "https://mapy.com/s/leredazeka",
                "1–2 km",
                "spící obr Máza",
            ),
            "stezky-brniste": (
                "https://mapy.com/s/nujepuhota",
                "3,7 km",
                "okolní pozemky jsou soukromé",
            ),
        }
        for slug, details in expected.items():
            with self.subTest(slug=slug):
                response = self.client.get(f"/cs/vylety/{slug}/")
                self.assertEqual(response.status_code, 200)
                image_slug = "brniste-stezky" if slug == "stezky-brniste" else slug
                self.assertContains(response, static(f"vylety/{image_slug}.jpg"))
                for detail in details:
                    self.assertContains(response, detail)

    def test_route_variants_have_individual_lengths_and_maps(self):
        """Multi-route trips keep each walking option and its map together."""
        brniste = self.client.get("/cs/vylety/stezky-brniste/")
        self.assertContains(brniste, 'class="route-variant"', count=3)
        self.assertContains(brniste, "Sochy ve skalách")
        self.assertContains(brniste, "1,5 km")
        self.assertContains(brniste, "https://mapy.com/s/jenojasole")
        self.assertContains(brniste, "Stezka Hastrmanů")
        self.assertContains(brniste, "6 km")
        self.assertContains(brniste, "https://mapy.com/s/jatubucura")
        self.assertContains(brniste, "Skleněná stezka")
        self.assertContains(brniste, "3,7 km")
        self.assertContains(brniste, "https://mapy.com/s/nujepuhota")
        self.assertNotContains(brniste, 'href="None"')

        horka = self.client.get("/cs/vylety/lesopark-horka/")
        self.assertContains(horka, 'class="route-variant"', count=1)
        self.assertContains(horka, "1–2 km")
        self.assertContains(horka, "https://mapy.com/s/leredazeka")
        self.assertNotContains(horka, 'href="None"')

        milstejn = self.client.get("/cs/vylety/milstejn-nadeje/")
        self.assertContains(milstejn, 'class="route-variant"', count=2)
        self.assertContains(
            milstejn,
            "Hlavní okruh přes Milštejn a\N{NO-BREAK SPACE}Naději",
        )
        self.assertContains(milstejn, "8,2 km")
        self.assertContains(milstejn, "https://mapy.com/s/nojudacesu")
        self.assertContains(milstejn, "Kočárková varianta")
        self.assertContains(milstejn, "8,4 km")
        self.assertContains(milstejn, "https://mapy.com/s/galusenedu")
        self.assertContains(milstejn, "4 km")
        self.assertContains(milstejn, "autem nebo autobusem")
        self.assertContains(milstejn, "Volně přístupné")
        self.assertContains(
            milstejn,
            static("responsive/vylety/milstejn-480.webp"),
        )
        self.assertContains(
            milstejn,
            'href="/cs/vylety/koupani/#nadrz-nadeje"',
        )
        self.assertNotContains(milstejn, 'href="None"')

    def test_recommended_cycling_routes_have_lengths_elevations_and_maps(self):
        """Every recommended cycle route keeps its supplied facts together."""
        overview = self.client.get("/cs/vylety/")
        self.assertContains(overview, 'href="/cs/vylety/cyklovylety/"')
        self.assertContains(overview, "Pět tras z Cvikova")
        self.assertNotContains(overview, 'class="cycling-route"')

        response = self.client.get("/cs/vylety/cyklovylety/")
        self.assertContains(response, 'class="cycling-route"', count=5)
        expected_routes = (
            (
                "Okruh přes Nový Bor",
                "20 km",
                "237 m",
                "jahafutero",
                "Údolím samoty přes Radvanec do Nového Boru.",
            ),
            (
                "Okolo Klíče",
                "20 km",
                "316 m",
                "kafofavuba",
                "Krátká, ale výživná vyjížďka okolo Klíče.",
            ),
            (
                "Milštejn a Naděje",
                "16 km",
                "235 m",
                "pacapemude",
                "Vystoupejte k Milštejnu a horské nádrži Naděje.",
            ),
            (
                "Na Novou Huť",
                "22 km",
                "347 m",
                "hajucesele",
                "Okruh Lužickými lesy na Novou Huť s návratem přes Rousínov.",
            ),
            (
                "Okruh přes Kunratice",
                "12 km",
                "82 m",
                "jogogapaca",
                "Nenáročná projížďka do Kunratic u Cvikova.",
            ),
        )
        for name, distance, elevation, map_slug, description in expected_routes:
            with self.subTest(name=name):
                self.assertContains(response, name)
                self.assertContains(response, distance)
                self.assertContains(response, elevation)
                self.assertContains(response, f"https://mapy.com/s/{map_slug}")
                self.assertContains(response, description)

        english = self.client.get("/en/vylety/cyklovylety/")
        self.assertContains(english, "Recommended cycle routes")
        self.assertContains(english, "Elevation gain")
        self.assertContains(english, "A short but challenging ride around Klíč.")
        self.assertNotContains(english, "Doporučené cyklotrasy")

        german = self.client.get("/de/vylety/cyklovylety/")
        self.assertContains(german, "Empfohlene Radrouten")
        self.assertContains(german, "Höhenmeter")
        self.assertContains(german, "Eine leichte Tour nach Kunratice u Cvikova.")
        self.assertNotContains(german, "Doporučené cyklotrasy")

    def test_cycling_trips_link_bidirectionally_to_swimming_and_restaurants(self):
        """Cycling cards participate in the same relation graph as other tips."""
        overview = self.client.get("/cs/vylety/cyklovylety/")
        self.assertContains(overview, 'id="cyklotrasa-novy-bor"')
        self.assertContains(overview, 'id="cyklotrasa-milstejn-nadeje"')
        self.assertContains(
            overview,
            'href="/cs/vylety/restaurace/#bep-novy-bor"',
        )
        self.assertContains(
            overview,
            'href="/cs/vylety/restaurace/#la-vita"',
        )
        self.assertContains(
            overview,
            'href="/cs/vylety/restaurace/#royal-maharaja"',
        )
        self.assertContains(
            overview,
            'href="/cs/vylety/koupani/#nadrz-nadeje"',
        )

        swimming = self.client.get("/cs/vylety/koupani/")
        self.assertContains(
            swimming,
            'href="/cs/vylety/cyklovylety/#cyklotrasa-milstejn-nadeje"',
        )
        self.assertContains(swimming, "šestnáctikilometrové cyklotrase")

        restaurants = self.client.get("/cs/vylety/restaurace/")
        self.assertContains(
            restaurants,
            'href="/cs/vylety/cyklovylety/#cyklotrasa-novy-bor"',
            count=3,
        )
        self.assertContains(restaurants, "cyklistickém okruhu přes Nový Bor", count=3)

        english = self.client.get("/en/vylety/cyklovylety/")
        self.assertContains(
            english,
            "During the circuit, stop in Nový Bor for Asian cuisine at BẾP.",
        )
        self.assertContains(
            english,
            'href="/en/vylety/restaurace/#bep-novy-bor"',
        )

        german = self.client.get("/de/vylety/koupani/")
        self.assertContains(
            german,
            "16 Kilometer langen Radroute über Milštejn",
        )
        self.assertContains(
            german,
            'href="/de/vylety/cyklovylety/#cyklotrasa-milstejn-nadeje"',
        )

    def test_jablonne_lemberk_trip_has_routes_and_official_links(self):
        """The Jablonné guide keeps both supplied routes and distinct sources."""
        response = self.client.get("/cs/vylety/jablonne-lemberk/")
        self.assertContains(response, "Jablonné a Lemberk")
        self.assertContains(response, "Vzdálenost autem")
        self.assertContains(response, "10 km")
        self.assertContains(response, "Do Jablonného v Podještědí je možné")
        self.assertContains(response, "autem nebo autobusem")
        self.assertContains(response, "Základní okruh")
        self.assertContains(response, "6,2 km")
        self.assertContains(response, "https://mapy.com/s/nuderocako")
        self.assertContains(response, "Kočárková varianta")
        self.assertContains(response, "6,4 km")
        self.assertContains(response, "https://mapy.com/s/catadakube")
        self.assertContains(response, "Bazilika sv. Vavřince a sv. Zdislavy")
        self.assertContains(response, "https://www.zamek-lemberk.cz/")
        self.assertContains(
            response,
            "https://rybylemberk.cz/obcersteni-parkovani/zip-line",
        )
        self.assertContains(
            response,
            'href="/cs/vylety/koupani/#koupaliste-jablonne"',
        )
        self.assertContains(
            response,
            'href="/cs/vylety/restaurace/#lemberk"',
        )

        graph = self.get_schema_graph("/cs/vylety/jablonne-lemberk/")
        attraction = self.schema_node(graph, "TouristAttraction")
        self.assertEqual(
            attraction["sameAs"],
            [
                "https://www.zdislava.cz/",
                "https://www.zamek-lemberk.cz/",
                "https://rybylemberk.cz/obcersteni-parkovani/zip-line",
            ],
        )

    def test_extended_trip_descriptions_are_translated(self):
        """New paragraphs remain useful in both translated site versions."""
        english = self.client.get("/en/vylety/klic/")
        self.assertContains(english, "stone sea")
        self.assertNotContains(english, "kamenné moře")

        german = self.client.get("/de/vylety/duty-kamen/")
        self.assertContains(german, "Felsbank Karolínin odpočinek")
        self.assertNotContains(german, "skalní lavici")

        new_english = self.client.get("/en/vylety/lesopark-horka/")
        self.assertContains(new_english, "Horka Forest Park")
        self.assertContains(new_english, "Forest park walk")
        self.assertNotContains(new_english, "Procházka lesoparkem")

        new_german = self.client.get("/de/vylety/stezky-brniste/")
        self.assertContains(new_german, "Wege rund um Brniště")
        self.assertContains(new_german, "Routenkarte anzeigen")
        self.assertNotContains(new_german, "Zobrazit mapu trasy")

        milstejn_english = self.client.get("/en/vylety/milstejn-nadeje/")
        self.assertContains(milstejn_english, "Milštejn and Naděje")
        self.assertContains(milstejn_english, "Pushchair-friendly route")
        self.assertNotContains(milstejn_english, "Kočárková varianta")

        milstejn_german = self.client.get("/de/vylety/milstejn-nadeje/")
        self.assertContains(milstejn_german, "Milštejn und Naděje")
        self.assertContains(milstejn_german, "Kinderwagentaugliche Route")
        self.assertNotContains(milstejn_german, "Kočárková varianta")

        lemberk_english = self.client.get("/en/vylety/jablonne-lemberk/")
        self.assertContains(lemberk_english, "Jablonné and Lemberk")
        self.assertContains(lemberk_english, "Pushchair-friendly route")
        self.assertNotContains(lemberk_english, "Kočárková varianta")

        lemberk_german = self.client.get("/de/vylety/jablonne-lemberk/")
        self.assertContains(lemberk_german, "Jablonné und Lemberk")
        self.assertContains(lemberk_german, "Kinderwagentaugliche Route")
        self.assertNotContains(lemberk_german, "Kočárková varianta")

    def test_every_destination_has_structured_practical_information(self):
        """Trips and swimming tips expose only the facts maintained for them."""
        for attraction in ATTRACTIONS:
            with self.subTest(attraction=attraction.name):
                self.assertTrue(str(attraction.stroller_access))
                self.assertTrue(str(attraction.admission))
                self.assertTrue(str(attraction.opening_hours))
        for swimming_tip in SWIMMING_TIPS:
            with self.subTest(swimming_tip=swimming_tip.name):
                self.assertFalse(hasattr(swimming_tip, "stroller_access"))
                self.assertTrue(str(swimming_tip.admission))
                self.assertTrue(str(swimming_tip.opening_hours))

    def test_attraction_detail_shows_structured_practical_information(self):
        """Trip facts include access, prices, hours, and a freshness warning."""
        response = self.client.get("/cs/vylety/skalni-hrad-sloup/")
        self.assertContains(response, "Kočárek")
        self.assertContains(response, "Vstupné")
        self.assertContains(response, "rodinné vstupné 330 Kč")
        self.assertContains(response, "Provozní doba")
        self.assertContains(response, "o víkendech 9–16")
        self.assertContains(response, "Ceny a provozní doba se mohou změnit")

    def test_swimming_destinations_show_structured_practical_information(self):
        """Each swimming card contains admission and summer hours without access."""
        response = self.client.get("/cs/vylety/koupani/")
        html = response.content.decode()
        self.assertEqual(
            html.count('class="swimming-facts"'),
            len(SWIMMING_TIPS),
        )
        self.assertNotContains(response, "Kočárek")
        self.assertContains(response, "parkování auta 100 Kč")
        self.assertContains(response, "V létě 11–19")
        self.assertContains(response, "celodenní parkování 150 Kč")
        self.assertContains(response, "<dt>Doprava</dt>", count=3, html=True)
        self.assertContains(response, "Ceny, provozní doba i podmínky se mohou změnit")

    def test_practical_information_is_translated(self):
        """Maintained facts and their warning are localized."""
        english = self.client.get("/en/vylety/motyli-dum-jonsdorf/")
        self.assertContains(english, "Pushchair")
        self.assertContains(english, "Adult €9")
        self.assertContains(english, "Daily 10:00–18:00")
        self.assertContains(english, "Prices and opening hours may change")
        self.assertNotContains(english, "Provozní doba")

        german = self.client.get("/de/vylety/koupani/")
        self.assertNotContains(german, "Kinderwagen")
        self.assertContains(german, "Erwachsene 5 €")
        self.assertContains(german, "Im Sommer 11–19 Uhr")
        self.assertContains(
            german,
            "Preise, Öffnungszeiten und Bedingungen können sich ändern",
        )
        self.assertNotContains(german, "Vstupné")

    def test_related_trip_graph_is_valid_and_bidirectional(self):
        """Every curated relation resolves and has the expected reverse edge."""
        destinations = {
            **{("attraction", item.slug): item for item in ATTRACTIONS},
            **{("cycling", item.slug): item for item in CYCLING_TRIPS},
            **{("swimming", item.slug): item for item in SWIMMING_TIPS},
            **{("restaurant", item.slug): item for item in RESTAURANTS},
        }
        actual_pairs = set()
        relation_count = 0
        for source, destination in destinations.items():
            for relation in destination.related_trips:
                relation_count += 1
                target = (relation.target_kind, relation.target_slug)
                self.assertIn(target, destinations)
                reverse_relations = destinations[target].related_trips
                self.assertTrue(
                    any(
                        reverse.target_kind == source[0]
                        and reverse.target_slug == source[1]
                        for reverse in reverse_relations
                    )
                )
                actual_pairs.add(frozenset((source, target)))

        expected_pairs = {
            frozenset(
                (
                    ("attraction", "cvikovske-vyhlidky"),
                    ("attraction", "duty-kamen"),
                )
            ),
            frozenset(
                (
                    ("attraction", "skalni-hrad-sloup"),
                    ("swimming", "koupaliste-sloup"),
                )
            ),
            frozenset(
                (
                    ("attraction", "pacinek-glass"),
                    ("attraction", "ajeto-lindava"),
                )
            ),
            frozenset(
                (
                    ("attraction", "ajeto-lindava"),
                    ("restaurant", "sklarska-krcma"),
                )
            ),
            frozenset(
                (
                    ("attraction", "klic"),
                    ("attraction", "polevsko"),
                )
            ),
            frozenset(
                (
                    ("attraction", "oybin"),
                    ("attraction", "motyli-dum-jonsdorf"),
                )
            ),
            frozenset(
                (
                    ("attraction", "motyli-dum-jonsdorf"),
                    ("swimming", "koupaliste-jonsdorf"),
                )
            ),
            frozenset(
                (
                    ("attraction", "privoz-mlynky-vyhlidky"),
                    ("swimming", "koupaliste-ceska-kamenice"),
                )
            ),
            frozenset(
                (
                    ("attraction", "duty-kamen"),
                    ("attraction", "kunraticke-svycarsko"),
                )
            ),
            frozenset(
                (
                    ("attraction", "oybin"),
                    ("attraction", "hvozd"),
                )
            ),
            frozenset(
                (
                    ("attraction", "pacinek-glass"),
                    ("attraction", "stezky-brniste"),
                )
            ),
            frozenset(
                (
                    ("attraction", "privoz-mlynky-vyhlidky"),
                    ("attraction", "transborder-chrastava"),
                )
            ),
            frozenset(
                (
                    ("attraction", "pumptrack-cvikov"),
                    ("restaurant", "na-krajicku"),
                )
            ),
            frozenset(
                (
                    ("attraction", "hvozd"),
                    ("restaurant", "resort-hvozd"),
                )
            ),
            frozenset(
                (
                    ("attraction", "hvozd"),
                    ("restaurant", "pivovar-krompach"),
                )
            ),
            frozenset(
                (
                    ("attraction", "skalni-hrad-sloup"),
                    ("restaurant", "na-strazi"),
                )
            ),
            frozenset(
                (
                    ("swimming", "koupaliste-sloup"),
                    ("restaurant", "na-strazi"),
                )
            ),
            frozenset(
                (
                    ("attraction", "skalni-hrad-sloup"),
                    ("restaurant", "sloupska-terasa"),
                )
            ),
            frozenset(
                (
                    ("swimming", "koupaliste-sloup"),
                    ("restaurant", "sloupska-terasa"),
                )
            ),
            frozenset(
                (
                    ("swimming", "koupaliste-dubice"),
                    ("restaurant", "kaido-sushi"),
                )
            ),
            frozenset(
                (
                    ("attraction", "milstejn-nadeje"),
                    ("swimming", "nadrz-nadeje"),
                )
            ),
            frozenset(
                (
                    ("cycling", "milstejn-nadeje"),
                    ("swimming", "nadrz-nadeje"),
                )
            ),
            frozenset(
                (
                    ("cycling", "novy-bor"),
                    ("restaurant", "bep-novy-bor"),
                )
            ),
            frozenset(
                (
                    ("cycling", "novy-bor"),
                    ("restaurant", "la-vita"),
                )
            ),
            frozenset(
                (
                    ("cycling", "novy-bor"),
                    ("restaurant", "royal-maharaja"),
                )
            ),
            frozenset(
                (
                    ("attraction", "jablonne-lemberk"),
                    ("swimming", "koupaliste-jablonne"),
                )
            ),
            frozenset(
                (
                    ("attraction", "jablonne-lemberk"),
                    ("restaurant", "lemberk"),
                )
            ),
        }
        self.assertEqual(relation_count, 54)
        self.assertEqual(actual_pairs, expected_pairs)

    def test_attraction_details_link_to_related_trips(self):
        """Detail recommendations explain and link each curated connection."""
        shortened = self.client.get("/cs/vylety/duty-kamen/")
        self.assertContains(shortened, "Výlety v okolí")
        self.assertContains(
            shortened,
            'href="/cs/vylety/cvikovske-vyhlidky/"',
        )
        self.assertContains(shortened, "projděte celý okruh přes Kalvárii")

        exotenhaus = self.client.get("/cs/vylety/motyli-dum-jonsdorf/")
        self.assertContains(exotenhaus, 'class="related-trip-card"', count=2)
        self.assertContains(
            exotenhaus,
            'href="/cs/vylety/koupani/#koupaliste-jonsdorf"',
        )
        self.assertContains(exotenhaus, 'href="/cs/vylety/oybin/"')
        self.assertContains(exotenhaus, "Výlety v okolí")
        self.assertContains(exotenhaus, "Koupání v okolí")
        self.assertNotContains(exotenhaus, "Související výlety")

    def test_swimming_cards_link_to_related_attractions(self):
        """The curated swimming cards carry contextual trip links."""
        response = self.client.get("/cs/vylety/koupani/")
        self.assertContains(response, 'class="swimming-card__related"', count=6)
        self.assertContains(response, 'id="koupaliste-sloup"')
        self.assertContains(response, 'id="koupaliste-jonsdorf"')
        self.assertContains(response, 'id="koupaliste-ceska-kamenice"')
        self.assertContains(response, 'id="nadrz-nadeje"')
        self.assertContains(response, 'href="/cs/vylety/skalni-hrad-sloup/"')
        self.assertContains(response, 'href="/cs/vylety/motyli-dum-jonsdorf/"')
        self.assertContains(
            response,
            'href="/cs/vylety/privoz-mlynky-vyhlidky/"',
        )
        self.assertContains(response, 'href="/cs/vylety/milstejn-nadeje/"')
        self.assertContains(response, "Výlety v okolí")
        self.assertContains(response, "Cyklotrasy v okolí")
        self.assertNotContains(response, "Spojte s výletem")

    def test_nadeje_swimming_tip_has_map_distance_and_access_note(self):
        """The natural reservoir uses its map without implying direct car access."""
        response = self.client.get("/cs/vylety/koupani/")
        self.assertContains(response, "Nádrž Naděje")
        self.assertContains(response, "chladnou horskou vodou")
        self.assertContains(response, "Vzdálenost od apartmánu")
        self.assertContains(response, "13 km")
        self.assertContains(response, "Přímo k nádrži nelze dojet autem")
        self.assertContains(response, "https://mapy.com/s/jamobakeju")
        self.assertNotContains(response, 'href="None"')

    def test_restaurants_are_linked_bidirectionally_from_nearby_trips(self):
        """Food tips have their own section and lead back to the matching trips."""
        pumptrack = self.client.get("/cs/vylety/pumptrack-cvikov/")
        self.assertContains(pumptrack, "Kde se najíst poblíž")
        self.assertContains(
            pumptrack,
            'href="/cs/vylety/restaurace/#na-krajicku"',
        )
        self.assertContains(pumptrack, "Přímo u pumptracku a trampolín")

        ajeto = self.client.get("/cs/vylety/ajeto-lindava/")
        self.assertContains(
            ajeto,
            'href="/cs/vylety/restaurace/#sklarska-krcma"',
        )
        self.assertContains(ajeto, "tradiční českou kuchyni")

        hvozd = self.client.get("/cs/vylety/hvozd/")
        self.assertContains(
            hvozd,
            'href="/cs/vylety/restaurace/#resort-hvozd"',
        )
        self.assertContains(
            hvozd,
            'href="/cs/vylety/restaurace/#pivovar-krompach"',
        )

        sloup = self.client.get("/cs/vylety/koupani/")
        self.assertContains(
            sloup,
            'href="/cs/vylety/restaurace/#na-strazi"',
        )
        self.assertContains(
            sloup,
            'href="/cs/vylety/restaurace/#sloupska-terasa"',
        )
        self.assertContains(
            sloup,
            'href="/cs/vylety/restaurace/#kaido-sushi"',
        )

        restaurants = self.client.get("/cs/vylety/restaurace/")
        self.assertContains(restaurants, 'id="sklarska-krcma"')
        self.assertContains(restaurants, 'href="/cs/vylety/ajeto-lindava/"')
        self.assertContains(restaurants, "ukázkou ruční výroby skla")
        self.assertContains(restaurants, "Výlety v okolí")
        self.assertContains(restaurants, "Cyklotrasy v okolí")
        self.assertContains(restaurants, "Koupání v okolí")
        self.assertNotContains(restaurants, "Spojte s výletem")

        cycling = self.client.get("/cs/vylety/cyklovylety/")
        self.assertContains(cycling, "Koupání po cestě")
        self.assertContains(cycling, "Kde se najíst po cestě")
        self.assertNotContains(cycling, "Spojte s výletem")

        self.assertContains(ajeto, "Tip na jídlo")
        self.assertNotContains(ajeto, "Doporučená restaurace")

    def test_related_destination_headings_are_translated(self):
        """Typed relation headings stay clear in both translated versions."""
        cycling_english = self.client.get("/en/vylety/cyklovylety/")
        self.assertContains(cycling_english, "Swimming along the way")
        self.assertContains(cycling_english, "Where to eat along the way")
        self.assertNotContains(cycling_english, "Koupání po cestě")

        cycling_german = self.client.get("/de/vylety/cyklovylety/")
        self.assertContains(cycling_german, "Baden unterwegs")
        self.assertContains(cycling_german, "Essen unterwegs")
        self.assertNotContains(cycling_german, "Kde se najíst po cestě")

        ajeto_english = self.client.get("/en/vylety/ajeto-lindava/")
        self.assertContains(ajeto_english, "Food tip")
        self.assertNotContains(ajeto_english, "Tip na jídlo")

        ajeto_german = self.client.get("/de/vylety/ajeto-lindava/")
        self.assertContains(ajeto_german, "Essenstipp")
        self.assertNotContains(ajeto_german, "Tip na jídlo")

    def test_ceska_kamenice_trip_has_both_route_lengths(self):
        """The long loop and stroller-friendly short route stay distinct."""
        response = self.client.get("/cs/vylety/privoz-mlynky-vyhlidky/")
        self.assertContains(response, "Přívoz, Mlýnky a vyhlídky")
        self.assertContains(response, "<dt>Vzdálenost autem</dt>", html=True)
        self.assertContains(response, "<dt>Délka okruhu</dt>", html=True)
        self.assertContains(response, "<dt>K Mlýnkům a zpět</dt>", html=True)
        self.assertContains(response, "22 km")
        self.assertContains(response, "4 km")
        self.assertContains(response, "1,4 km")
        self.assertContains(response, "Přívoz, Mlýnky i vyhlídky jsou volně přístupné")
        self.assertContains(
            response,
            static("responsive/vylety/ceska-kamenice-privoz-480.webp"),
        )
        self.assertContains(
            response,
            'href="/cs/vylety/koupani/#koupaliste-ceska-kamenice"',
        )

        swimming = self.client.get("/cs/vylety/koupani/")
        self.assertContains(swimming, "Koupaliště s bistrem.")
        self.assertContains(swimming, "22 km")

        english = self.client.get("/en/vylety/privoz-mlynky-vyhlidky/")
        self.assertContains(english, "Ferry, Mlýnky and viewpoints")
        self.assertContains(english, "To Mlýnky and back")
        self.assertContains(english, "freely accessible")
        self.assertNotContains(english, "volně přístupné")

        german = self.client.get("/de/vylety/privoz-mlynky-vyhlidky/")
        self.assertContains(german, "Fähre, Mlýnky und Aussichtspunkte")
        self.assertContains(german, "Zu Mlýnky und zurück")
        self.assertContains(german, "frei zugänglich")
        self.assertNotContains(german, "volně přístupné")

    def test_related_trip_links_and_copy_are_translated(self):
        """Related links preserve the active language and localized rationale."""
        english = self.client.get("/en/vylety/motyli-dum-jonsdorf/")
        self.assertContains(english, "Trips nearby")
        self.assertContains(english, "Swimming nearby")
        self.assertContains(
            english,
            'href="/en/vylety/koupani/#koupaliste-jonsdorf"',
        )
        self.assertContains(english, "On a warm day, combine your visit")
        self.assertNotContains(english, "V teplém dni")

        german = self.client.get("/de/vylety/koupani/")
        self.assertContains(german, "Ausflüge in der Umgebung")
        self.assertContains(german, "Radrouten in der Umgebung")
        self.assertContains(
            german,
            'href="/de/vylety/motyli-dum-jonsdorf/"',
        )
        self.assertContains(german, "Verbinden Sie das Baden")
        self.assertNotContains(german, "Koupání můžete spojit")

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
            static("responsive/vylety/koupaliste-jonsdorf-480.webp"),
        )
        for tip in SWIMMING_TIPS:
            with self.subTest(tip=tip.name):
                self.assertContains(response, tip.name)
                if tip.official_url:
                    self.assertContains(response, tip.official_url)
                if tip.map_url:
                    self.assertContains(response, tip.map_url)

    def test_trip_guide_includes_recommended_restaurants(self):
        """The overview opens one complete, distance-sorted restaurant guide."""
        overview = self.client.get("/cs/vylety/")
        self.assertContains(overview, 'href="/cs/vylety/restaurace/"')
        self.assertContains(overview, "Čtrnáct tipů v okolí")

        response = self.client.get("/cs/vylety/restaurace/")
        html = response.content.decode()
        self.assertEqual(
            html.count('class="restaurant-card"'),
            len(RESTAURANTS),
        )
        self.assertContains(response, "Pěšky z apartmánu")
        self.assertContains(response, "Autem nebo autobusem")
        self.assertContains(response, "0,3 km")
        self.assertContains(response, "19 km")
        self.assertContains(response, "Sushi a ramen v České Lípě")
        self.assertContains(response, "Sklářská krčma")
        self.assertContains(response, "Tradiční česká kuchyně")
        self.assertContains(response, 'id="la-vita"')
        self.assertContains(response, "Moderní italská restaurace v Novém Boru")
        self.assertContains(response, "https://www.lavita173.cz/")
        self.assertContains(response, "https://www.ajetoglass.com/sklarska-krcma")
        self.assertContains(
            response,
            "https://www.facebook.com/p/Kaido-Sushi-%C4%8CL-61556848413838/",
        )
        self.assertContains(
            response,
            "https://www.facebook.com/groups/662887772360954",
        )
        self.assertContains(response, "Obědy v pracovní dny")
        self.assertContains(response, "V létě se zde v pátek konají koncerty")
        self.assertContains(
            response,
            "Do Nového Boru je možné dojet také autobusem",
            count=3,
        )
        self.assertContains(
            response,
            "Do Sloupu v Čechách je možné dojet také autobusem",
            count=2,
        )
        self.assertContains(
            response,
            "Do Krompachu je možné dojet také autobusem ze Cvikova",
            count=2,
        )
        self.assertContains(
            response,
            'href="/cs/vylety/pumptrack-cvikov/"',
        )
        self.assertContains(response, 'href="/cs/vylety/hvozd/"')
        self.assertContains(
            response,
            'href="/cs/vylety/koupani/#koupaliste-dubice"',
        )
        self.assertContains(
            response,
            "Před návštěvou si vždy ověřte aktuální informace",
        )
        for tip in RESTAURANTS:
            with self.subTest(tip=tip.name):
                self.assertContains(response, tip.name)
                self.assertContains(response, tip.official_url)

    def test_restaurant_guide_is_localized(self):
        """Restaurant recommendations and their internal links keep the language."""
        english = self.client.get("/en/vylety/restaurace/")
        self.assertContains(english, "Recommended restaurants")
        self.assertContains(english, "On foot from the apartment")
        self.assertContains(english, "Traditional Czech cuisine")
        self.assertContains(english, "A modern Italian restaurant in Nový Bor")
        self.assertContains(english, "Combine a visit to Sklářská krčma")
        self.assertContains(
            english,
            'href="/en/vylety/pumptrack-cvikov/"',
        )
        self.assertContains(english, 'href="/en/vylety/ajeto-lindava/"')
        self.assertNotContains(english, "Pěšky z apartmánu")
        english_ajeto = self.client.get("/en/vylety/ajeto-lindava/")
        self.assertContains(english_ajeto, "After touring the glassworks")

        german = self.client.get("/de/vylety/restaurace/")
        self.assertContains(german, "Empfohlene Restaurants")
        self.assertContains(german, "Zu Fuß vom Apartment")
        self.assertContains(german, "Traditionelle tschechische Küche")
        self.assertContains(german, "Ein modernes italienisches Restaurant in Nový Bor")
        self.assertContains(german, "Verbinden Sie einen Besuch")
        self.assertContains(german, 'href="/de/vylety/hvozd/"')
        self.assertContains(german, 'href="/de/vylety/ajeto-lindava/"')
        self.assertNotContains(german, "Autem nebo autobusem")
        german_ajeto = self.client.get("/de/vylety/ajeto-lindava/")
        self.assertContains(german_ajeto, "Nach der Besichtigung der Glashütte")

    def test_swimming_tips_are_translated(self):
        """The dedicated guide remains useful in every supported language."""
        english = self.client.get("/en/vylety/koupani/")
        self.assertContains(english, "Swimming trips")
        self.assertContains(english, "Česká Kamenice municipal swimming pool")
        self.assertContains(english, "Naděje Reservoir")
        self.assertContains(english, "Distance from the apartment")

        german = self.client.get("/de/vylety/koupani/")
        self.assertContains(german, "Badeausflüge")
        self.assertContains(german, "Städtisches Freibad Česká Kamenice")
        self.assertContains(german, "Stausee Naděje")
        self.assertContains(german, "Entfernung von der Ferienwohnung")

    def test_trip_pages_include_a_print_header_and_current_page_qr(self):
        """Every trip layout carries a local SVG QR code for its canonical URL."""
        pages = (
            (
                "/cs/vylety/",
                "trip-print--overview",
                "Výlety z\N{NO-BREAK SPACE}Apartmánu Cvikov",
                "Kam na\N{NO-BREAK SPACE}výlet ve\N{NO-BREAK SPACE}Cvikově",
            ),
            (
                "/cs/vylety/koupani/",
                "trip-print--swimming",
                "Výlety s\N{NO-BREAK SPACE}koupáním",
                "Sedm míst pro malé i velké plavce",
            ),
            (
                "/cs/vylety/cyklovylety/",
                "trip-print--cycling",
                "Doporučené cyklotrasy",
                "Pět tras pro výlet na kole",
            ),
            (
                "/cs/vylety/restaurace/",
                "trip-print--restaurants",
                "Doporučené restaurace",
                "Ověřené tipy pro oběd, večeři i sladkou zastávku",
            ),
            (
                "/cs/vylety/klic/",
                "trip-print--detail",
                "Výstup na\N{NO-BREAK SPACE}Klíč",
                "Praktické informace",
            ),
            (
                "/cs/vylety/milstejn-nadeje/",
                "trip-print--detail",
                "Milštejn a\N{NO-BREAK SPACE}Naděje",
                "Varianty výletu",
            ),
        )
        for path, page_class, print_title, content_heading in pages:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertContains(response, page_class)
                self.assertContains(response, 'class="print-header"')
                self.assertContains(response, 'class="print-header__qr-code"')
                self.assertContains(response, print_title)
                self.assertContains(response, content_heading)
                self.assertContains(response, f"https://apartmancvikov.cz{path}")
                self.assertContains(response, static("logo.png"))

        home = self.client.get("/cs/")
        self.assertNotContains(home, 'class="print-header"')

    def test_trip_print_styles_target_one_a4_page(self):
        """The print stylesheet defines compact A4 layouts for all trip pages."""
        stylesheet = (
            Path(settings.BASE_DIR) / "apartmancvikov" / "static" / "style.css"
        ).read_text(encoding="utf-8")

        self.assertIn("@media print", stylesheet)
        self.assertIn("size: A4 portrait", stylesheet)
        self.assertIn("body.trip-print--overview .attraction-grid", stylesheet)
        self.assertIn("body.trip-print--cycling .cycling-routes__grid", stylesheet)
        self.assertIn("body.trip-print--cycling .cycling-route__related", stylesheet)
        self.assertIn("body.trip-print--swimming .swimming-grid", stylesheet)
        self.assertIn("body.trip-print--swimming .swimming-photo img", stylesheet)
        self.assertIn(
            "body.trip-print--swimming .swimming-card__related",
            stylesheet,
        )
        self.assertIn(
            "body.trip-print--restaurants .restaurant-grid",
            stylesheet,
        )
        self.assertIn(
            "body.trip-print--restaurants .restaurant-card__related",
            stylesheet,
        )
        self.assertIn("body.trip-print--detail .attraction-detail", stylesheet)
        self.assertIn("body.trip-print--detail .route-variants", stylesheet)
        self.assertIn("body.trip-print--detail .related-trips", stylesheet)
        self.assertIn("body.trip-print .button-row", stylesheet)
        self.assertIn("body.trip-print .text-link", stylesheet)

    def test_unknown_attraction_returns_404(self):
        """Unknown attraction slugs do not create soft 404 pages."""
        response = self.client.get("/cs/vylety/nezname-misto/")
        self.assertEqual(response.status_code, 404)

    def test_exotenhaus_uses_current_information(self):
        """The former butterfly-house guide reflects the current exhibition."""
        response = self.client.get("/cs/vylety/motyli-dum-jonsdorf/")

        self.assertContains(response, "Dům exotických zvířat")
        self.assertContains(response, "2 000 litrů")
        self.assertContains(response, "Část s motýly je momentálně uzavřená")
        self.assertContains(response, "https://www.exotenhaus.info/")
        self.assertNotContains(response, "https://www.schmetterlingshaus.info/")
        self.assertContains(response, static("vylety/jonsdorf.jpg"))

    def test_mountain_express_is_listed_for_reachable_attractions(self):
        """Jonsdorf, Oybin and the swimming guide mention the seasonal service."""
        message = "termín a dostupnost jízdenek si ověřte předem"
        for path in (
            "/cs/vylety/motyli-dum-jonsdorf/",
            "/cs/vylety/oybin/",
            "/cs/vylety/koupani/",
        ):
            with self.subTest(path=path):
                self.assertContains(self.client.get(path), message)

    def test_own_duty_kamen_photo_replaces_wikimedia_image(self):
        """The new own photo is shown without the former external attribution."""
        response = self.client.get("/cs/vylety/duty-kamen/")
        self.assertContains(response, static("vylety/duty-kamen.jpg"))
        self.assertNotContains(response, "Lutz Maertens")
        self.assertNotContains(response, "commons.wikimedia.org")

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
            (
                "/cs/vylety/",
                "CollectionPage",
                "ItemList",
                len(ATTRACTIONS) + 3,
            ),
            (
                "/cs/vylety/cyklovylety/",
                "CollectionPage",
                "ItemList",
                len(CYCLING_TRIPS),
            ),
            (
                "/cs/vylety/koupani/",
                "CollectionPage",
                "ItemList",
                len(SWIMMING_TIPS),
            ),
            (
                "/cs/vylety/restaurace/",
                "CollectionPage",
                "ItemList",
                len(RESTAURANTS),
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
                        if path.endswith("/restaurace/"):
                            self.assertTrue(
                                all(
                                    entry["item"]["@type"] == "FoodEstablishment"
                                    for entry in main["itemListElement"]
                                )
                            )
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

    def test_duty_kamen_image_has_own_photo_metadata(self):
        """The new own attraction photo identifies the operator as rights holder."""
        graph = self.get_schema_graph("/cs/vylety/duty-kamen/")
        image = self.schema_node(graph, "ImageObject")
        operator = self.schema_node(graph, "Person")
        self.assertEqual(image["width"], 4000)
        self.assertEqual(image["height"], 3000)
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
        self.assertEqual(len(locations), 99)
        self.assertIn("https://apartmancvikov.cz/cs/", locations)
        self.assertIn("https://apartmancvikov.cz/cs/pocasi/", locations)
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/cyklovylety/",
            locations,
        )
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/koupani/",
            locations,
        )
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/restaurace/",
            locations,
        )
        self.assertIn(
            "https://apartmancvikov.cz/de/vylety/motyli-dum-jonsdorf/", locations
        )
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/privoz-mlynky-vyhlidky/",
            locations,
        )
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/pumptrack-cvikov/", locations
        )
        self.assertIn(
            "https://apartmancvikov.cz/de/vylety/stezky-brniste/",
            locations,
        )
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/milstejn-nadeje/",
            locations,
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
            f"<image:loc>{settings.SITE_URL}"
            f"{static('vylety/duty-kamen.jpg')}</image:loc>",
            sitemap,
        )
        self.assertIn(
            f"<image:loc>{settings.SITE_URL}"
            f"{static('vylety/koupaliste-jonsdorf.jpg')}</image:loc>",
            sitemap,
        )
        self.assertIn(
            f"<image:loc>{settings.SITE_URL}"
            f"{static('vylety/ceska-kamenice-privoz.jpg')}</image:loc>",
            sitemap,
        )
        self.assertIn(
            f"<image:loc>{settings.SITE_URL}"
            f"{static('vylety/brniste-stezky.jpg')}</image:loc>",
            sitemap,
        )
        self.assertIn(
            f"<image:loc>{settings.SITE_URL}"
            f"{static('vylety/milstejn.jpg')}</image:loc>",
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
            "https://apartmancvikov.cz/cs/vylety/cyklovylety/",
        )
        self.assertContains(
            llms,
            "https://apartmancvikov.cz/cs/vylety/koupani/",
        )
        self.assertContains(
            llms,
            "https://apartmancvikov.cz/cs/vylety/restaurace/",
        )
        self.assertContains(llms, "https://apartmancvikov.cz/cs/pocasi/")
        self.assertContains(llms, "https://apartmancvikov.cz/cs/poptavka/")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL=CONTACT_EMAIL,
)
class ContactInquiryTest(TestCase):
    def inquiry_data(self, **overrides):
        """Return a valid inquiry payload with optional field overrides."""
        arrival = timezone.localdate() + timedelta(days=14)
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

    def test_date_inputs_start_at_next_availability_and_end_in_two_years(self):
        """Date inputs expose useful bounds based on current availability."""
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        occupied_until = tomorrow + timedelta(days=3)
        Booking.objects.create(
            start=tomorrow,
            end=occupied_until,
            uid="upcoming-booking",
        )

        response = self.client.get("/cs/poptavka/")
        form = response.context["form"]

        self.assertEqual(
            form.fields["arrival"].widget.attrs["min"],
            (occupied_until + timedelta(days=1)).isoformat(),
        )
        self.assertEqual(
            form.fields["departure"].widget.attrs["min"],
            (occupied_until + timedelta(days=2)).isoformat(),
        )
        maximum = maximum_inquiry_date(today).isoformat()
        self.assertEqual(form.fields["arrival"].widget.attrs["max"], maximum)
        self.assertEqual(form.fields["departure"].widget.attrs["max"], maximum)

    def test_today_and_dates_after_two_year_horizon_are_rejected(self):
        """The server enforces the same minimum and maximum as date inputs."""
        today = timezone.localdate()
        maximum = maximum_inquiry_date(today)

        today_response = self.client.post(
            "/cs/poptavka/",
            self.inquiry_data(
                arrival=today.isoformat(),
                departure=(today + timedelta(days=2)).isoformat(),
            ),
        )
        self.assertEqual(today_response.status_code, 200)
        self.assertContains(today_response, "Nejbližší možné datum příjezdu")

        late_response = self.client.post(
            "/cs/poptavka/",
            self.inquiry_data(
                arrival=maximum.isoformat(),
                departure=(maximum + timedelta(days=1)).isoformat(),
            ),
        )
        self.assertEqual(late_response.status_code, 200)
        self.assertContains(late_response, "Termín lze poptat nejpozději")
        self.assertEqual(len(mail.outbox), 0)

    def test_booking_conflict_is_rejected_without_sending(self):
        """An inquiry overlapping any occupied date does not send an e-mail."""
        arrival = timezone.localdate() + timedelta(days=7)
        Booking.objects.create(
            start=arrival + timedelta(days=2),
            end=arrival + timedelta(days=4),
            uid="conflicting-booking",
        )

        response = self.client.post(
            "/cs/poptavka/",
            self.inquiry_data(
                arrival=arrival.isoformat(),
                departure=(arrival + timedelta(days=6)).isoformat(),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "zasahuje do již obsazeného období")
        self.assertEqual(len(mail.outbox), 0)

    def test_stay_ending_when_next_booking_starts_is_allowed(self):
        """A departure on the next booking's arrival date is not an overlap."""
        arrival = timezone.localdate() + timedelta(days=7)
        next_arrival = arrival + timedelta(days=3)
        Booking.objects.create(
            start=next_arrival,
            end=next_arrival + timedelta(days=4),
            uid="following-booking",
        )

        response = self.client.post(
            "/cs/poptavka/",
            self.inquiry_data(
                arrival=arrival.isoformat(),
                departure=next_arrival.isoformat(),
            ),
        )

        self.assertRedirects(response, "/cs/poptavka/")
        self.assertEqual(len(mail.outbox), 1)

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
        yesterday = timezone.localdate() - timedelta(days=1)
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
