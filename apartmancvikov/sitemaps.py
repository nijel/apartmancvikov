from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.templatetags.static import static
from django.urls import reverse

from .content import ATTRACTIONS

HOME_IMAGES = (
    "foto/dum.jpg",
    "foto/tyrkys.jpg",
    "foto/levandule.jpg",
    "foto/fuchsie.jpg",
    "foto/obyvak.jpg",
    "foto/jidelna.jpg",
    "foto/kuchyn.jpg",
    "foto/koupelna-dole.jpg",
    "foto/koupelna-nahore.jpg",
    "foto/pradelna.jpg",
    "foto/pumptrack.jpg",
    "foto/stena.jpg",
    "foto/houpacka.jpg",
    "foto/kuchynka.jpg",
    "foto/trampolina.jpg",
    "foto/terasa.jpg",
    "foto/letecky.jpg",
)


def _absolute_image_url(path):
    return f"{settings.SITE_URL}{static(path)}"


class LocalizedSitemap(Sitemap):
    i18n = True
    alternates = True
    x_default = True
    protocol = "https"

    def _urls(self, page, protocol, domain):
        urls = super()._urls(page, protocol, domain)
        for url in urls:
            alternates = url["alternates"]
            czech_url = next(
                alternate["location"]
                for alternate in alternates
                if alternate["lang_code"] == "cs"
            )
            for alternate in alternates:
                if alternate["lang_code"] == "x-default":
                    alternate["location"] = czech_url
            item = url["item"][0] if self.i18n else url["item"]
            url["images"] = [
                _absolute_image_url(path) for path in self.image_paths(item)
            ]
        return urls

    def image_paths(self, _item):
        """Return canonical source images associated with one sitemap item."""
        return ()


class StaticViewSitemap(LocalizedSitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        """Return the named static pages included in the sitemap."""
        return [
            "home",
            "vylety",
            "cenik",
            "obsazenost",
            "kontakt",
            "poptavka",
            "privacy",
            "image_license",
        ]

    def location(self, item):
        """Resolve a named static page in the active language."""
        return reverse(item)

    def image_paths(self, item):
        """Expose the accommodation gallery and trip guide photographs."""
        if item == "home":
            return ("bg.jpg", *HOME_IMAGES)
        if item == "vylety":
            return ("bg.jpg", *(item.image for item in ATTRACTIONS if item.image))
        return ("bg.jpg",)


class AttractionSitemap(LocalizedSitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        """Return all attraction guide records."""
        return ATTRACTIONS

    def location(self, item):
        """Resolve an attraction guide in the active language."""
        return reverse("attraction_detail", kwargs={"slug": item.slug})

    def image_paths(self, item):
        """Expose the photograph displayed on an attraction detail page."""
        return ("bg.jpg", item.image) if item.image else ("bg.jpg",)
