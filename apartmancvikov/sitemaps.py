from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .content import ATTRACTIONS


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
        return urls


class StaticViewSitemap(LocalizedSitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        """Return the named static pages included in the sitemap."""
        return ["home", "vylety", "cenik", "obsazenost", "kontakt"]

    def location(self, item):
        """Resolve a named static page in the active language."""
        return reverse(item)


class AttractionSitemap(LocalizedSitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        """Return all attraction guide records."""
        return ATTRACTIONS

    def location(self, item):
        """Resolve an attraction guide in the active language."""
        return reverse("attraction_detail", kwargs={"slug": item.slug})
