import json
import re

from django.test import SimpleTestCase

from .content import ATTRACTIONS


class SeoTest(SimpleTestCase):
    languages = ("cs", "en", "de")

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
                self.assertEqual(html.count("<h1 "), 1)
                self.assertEqual(html.count('name="description"'), 1)

    def test_supported_and_unsupported_languages(self):
        """Only the three translated language prefixes are accepted."""
        self.assertEqual(self.client.get("/cs/").status_code, 200)
        self.assertEqual(self.client.get("/en/").status_code, 200)
        self.assertEqual(self.client.get("/de/").status_code, 200)
        self.assertEqual(self.client.get("/fr/").status_code, 404)

    def test_all_attraction_pages_exist_in_all_languages(self):
        """Every curated guide renders for each supported language."""
        for language in self.languages:
            for attraction in ATTRACTIONS:
                with self.subTest(language=language, attraction=attraction.slug):
                    response = self.client.get(f"/{language}/vylety/{attraction.slug}/")
                    self.assertEqual(response.status_code, 200)
                    html = response.content.decode()
                    self.assertEqual(html.count("<h1 "), 1)
                    self.assertIn(str(attraction.official_url), html)

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
        """Rendered JSON-LD is parseable and contains the expected entities."""
        response = self.client.get("/cs/vylety/oybin/")
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>',
            response.content.decode(),
            re.DOTALL,
        )
        self.assertEqual(len(scripts), 3)
        schemas = [json.loads(script) for script in scripts]
        self.assertEqual(schemas[0]["@type"], "VacationRental")
        self.assertEqual(schemas[0]["containsPlace"]["occupancy"]["value"], 9)
        self.assertEqual(schemas[1]["@type"], "TouristAttraction")
        self.assertEqual(schemas[2]["@type"], "BreadcrumbList")

    def test_sitemap_contains_all_localized_urls(self):
        """The sitemap contains each static and attraction language variant."""
        response = self.client.get(
            "/sitemap.xml", headers={"host": "apartmancvikov.cz"}, secure=True
        )
        self.assertEqual(response.status_code, 200)
        sitemap = response.content.decode()
        locations = re.findall(r"<loc>(.*?)</loc>", sitemap)
        self.assertEqual(len(locations), 45)
        self.assertIn("https://apartmancvikov.cz/cs/", locations)
        self.assertIn(
            "https://apartmancvikov.cz/de/vylety/motyli-dum-jonsdorf/", locations
        )
        self.assertIn(
            "https://apartmancvikov.cz/cs/vylety/pumptrack-cvikov/", locations
        )
        self.assertIn(
            'hreflang="x-default" href="https://apartmancvikov.cz/cs/vylety/oybin/"',
            sitemap,
        )

    def test_machine_readable_endpoints(self):
        """Robots and agent summaries publish their essential information."""
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertContains(robots, "Sitemap: https://apartmancvikov.cz/sitemap.xml")
        self.assertContains(robots, "Disallow: /admin/")

        llms = self.client.get("/llms.txt")
        self.assertEqual(llms.status_code, 200)
        self.assertContains(llms, "3 bedrooms, 7 standard beds")
        self.assertContains(llms, "https://apartmancvikov.cz/cs/vylety/")
