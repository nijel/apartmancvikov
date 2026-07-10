from django.conf import settings
from django.http import Http404, HttpResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from .content import ATTRACTIONS, ATTRACTIONS_BY_SLUG


class HomeView(TemplateView):
    template_name = "index.html"


class TripsView(TemplateView):
    template_name = "vylety.html"

    def get_context_data(self, **kwargs):
        """Add all curated attractions to the trips overview."""
        context = super().get_context_data(**kwargs)
        context["attractions"] = ATTRACTIONS
        return context


class AttractionDetailView(TemplateView):
    template_name = "attraction_detail.html"

    def get_context_data(self, **kwargs):
        """Resolve the attraction and build its structured metadata."""
        context = super().get_context_data(**kwargs)
        try:
            attraction = ATTRACTIONS_BY_SLUG[kwargs["slug"]]
        except KeyError as error:
            raise Http404 from error

        absolute_url = f"{settings.SITE_URL}{self.request.path}"
        image_url = (
            f"{settings.SITE_URL}{static(attraction.image)}"
            if attraction.image
            else f"{settings.SITE_URL}{static('foto/dum.jpg')}"
        )
        context.update(
            {
                "attraction": attraction,
                "attraction_schema": {
                    "@context": "https://schema.org",
                    "@type": "TouristAttraction",
                    "@id": f"{absolute_url}#attraction",
                    "name": str(attraction.name),
                    "description": str(attraction.description),
                    "url": absolute_url,
                    "image": image_url,
                    "sameAs": attraction.official_url,
                },
                "breadcrumb_schema": {
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": str(_("Ubytování")),
                            "item": f"{settings.SITE_URL}{reverse('home')}",
                        },
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": str(_("Výlety")),
                            "item": f"{settings.SITE_URL}{reverse('vylety')}",
                        },
                        {
                            "@type": "ListItem",
                            "position": 3,
                            "name": str(attraction.name),
                            "item": absolute_url,
                        },
                    ],
                },
            }
        )
        return context


def robots_txt(_request):
    """Publish crawler rules and point crawlers to the sitemap."""
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /admin/",
            f"Sitemap: {settings.SITE_URL}/sitemap.xml",
            "",
        ]
    )
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def llms_txt(_request):
    """Publish a concise, stable description for language-model agents."""
    content = f"""# Apartmán Cvikov

> Family-friendly holiday apartment in Cvikov, the gateway to the Lusatian Mountains.

## Key facts

- Address: Nábřežní 694, 471 54 Cvikov, Czechia
- 3 bedrooms, 7 standard beds, maximum capacity 9 guests, baby cot available
- 2 bathrooms, equipped kitchen, Wi-Fi, free private parking
- Garden, children's play equipment, pump track and seasonal outdoor pool
- Pets are not accepted
- Phone: +420 775 408 751
- Email: ubytovani@apartmancvikov.cz

## Canonical pages

- Czech: {settings.SITE_URL}/cs/
- English: {settings.SITE_URL}/en/
- German: {settings.SITE_URL}/de/
- Family trip guide: {settings.SITE_URL}/cs/vylety/
- Availability: {settings.SITE_URL}/cs/obsazenost/
- Prices and conditions: {settings.SITE_URL}/cs/cenik/
- Contact: {settings.SITE_URL}/cs/kontakt/

The trip guide contains individual pages for ten attractions around Cvikov.
For changeable admission prices and opening hours, follow the official
attraction links on those pages.
"""
    return HttpResponse(content, content_type="text/plain; charset=utf-8")
