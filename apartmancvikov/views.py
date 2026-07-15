import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView

from .content import ATTRACTIONS, ATTRACTIONS_BY_SLUG
from .forms import ContactInquiryForm
from .site_config import (
    ADDRESS_LOCALITY,
    ADDRESS_POSTAL_CODE,
    ADDRESS_STREET,
    CONTACT_EMAIL,
    CONTACT_PHONE_DISPLAY,
)

logger = logging.getLogger(__name__)


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

        context.update(
            {
                "attraction": attraction,
                "attraction_meta_description": "{} {}".format(
                    attraction.summary,
                    _("Přibližně %(distance)s km od Apartmánu Cvikov.")
                    % {"distance": attraction.distance_km},
                ),
            }
        )
        return context


class InquiryView(FormView):
    template_name = "poptavka.html"
    form_class = ContactInquiryForm

    def get_success_url(self):
        """Return to the inquiry section after successful submission."""
        return reverse("poptavka")

    def form_valid(self, form):
        """Send a valid inquiry or quietly discard a honeypot submission."""
        if not form.is_honeypot_filled:
            inquiry = form.cleaned_data
            body = render_to_string(
                "emails/contact_inquiry.txt",
                {
                    "inquiry": inquiry,
                    "language": self.request.LANGUAGE_CODE,
                },
            )
            email = EmailMessage(
                subject=_("Nová poptávka pobytu z webu Apartmánu Cvikov"),
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[CONTACT_EMAIL],
                reply_to=[inquiry["email"]],
            )
            try:
                sent = email.send(fail_silently=False)
            except (OSError, SMTPException):
                logger.exception("Contact inquiry e-mail could not be sent")
                form.add_error(
                    None,
                    _(
                        "Poptávku se nepodařilo odeslat. Zkuste to prosím "
                        "později nebo nás kontaktujte přímo e-mailem či telefonem."
                    ),
                )
                return self.form_invalid(form)
            if sent != 1:
                logger.error("Contact inquiry backend did not send a message")
                form.add_error(
                    None,
                    _(
                        "Poptávku se nepodařilo odeslat. Zkuste to prosím "
                        "později nebo nás kontaktujte přímo e-mailem či telefonem."
                    ),
                )
                return self.form_invalid(form)

        messages.success(
            self.request,
            _("Děkujeme, poptávka byla odeslána. Ozveme se vám co nejdříve."),
        )
        return redirect(self.get_success_url())


def robots_txt(_request):
    """Publish crawler rules and point crawlers to the sitemap."""
    content = "\n".join(
        [
            "User-agent: *",
            "Content-Signal: search=yes, ai-input=yes, ai-train=no",
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

- Address: {ADDRESS_STREET}, {ADDRESS_POSTAL_CODE} {ADDRESS_LOCALITY}, Czechia
- Spacious 130 m² apartment with 3 bedrooms
- 7 standard beds, 2 additional floor mattresses, maximum capacity 9 guests
- Baby cot available
- 2 bathrooms, equipped kitchen, Wi-Fi, free private parking
- Garden, children's play equipment, pump track and seasonal outdoor pool
- Pets are not accepted
- Phone: {CONTACT_PHONE_DISPLAY}
- Email: {CONTACT_EMAIL}

## Canonical pages

- Czech: {settings.SITE_URL}/cs/
- English: {settings.SITE_URL}/en/
- German: {settings.SITE_URL}/de/
- Family trip guide: {settings.SITE_URL}/cs/vylety/
- Availability: {settings.SITE_URL}/cs/obsazenost/
- Prices and conditions: {settings.SITE_URL}/cs/cenik/
- Contact: {settings.SITE_URL}/cs/kontakt/
- Stay enquiry: {settings.SITE_URL}/cs/poptavka/

## Stay enquiries

The localized stay enquiry page contains a non-binding form. It asks
for name, e-mail, optional phone, arrival and departure dates, numbers of
adults, children aged 3-12 and children under 3, and an optional note. Sending
the form does not confirm a reservation; availability is confirmed by the host.

The trip guide contains individual pages for ten attractions around Cvikov.
For changeable admission prices and opening hours, follow the official
attraction links on those pages.
"""
    return HttpResponse(content, content_type="text/plain; charset=utf-8")
