import time

from django import forms
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .site_config import MAX_GUESTS

FORM_TOKEN_SALT = "contact-inquiry"
MINIMUM_FILL_TIME_SECONDS = 2
MAXIMUM_FORM_AGE_SECONDS = 24 * 60 * 60


class ContactInquiryForm(forms.Form):
    name = forms.CharField(
        label=_("Jméno a příjmení"),
        max_length=120,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label=_("E-mail"),
        max_length=254,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    phone = forms.CharField(
        label=_("Telefon"),
        required=False,
        max_length=40,
        widget=forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel"}),
    )
    arrival = forms.DateField(
        label=_("Příjezd"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    departure = forms.DateField(
        label=_("Odjezd"),
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    adults = forms.IntegerField(
        label=_("Dospělí"),
        min_value=1,
        max_value=MAX_GUESTS,
        initial=2,
        widget=forms.NumberInput(attrs={"inputmode": "numeric"}),
    )
    children = forms.IntegerField(
        label=_("Děti od 3 do 12 let"),
        min_value=0,
        max_value=MAX_GUESTS,
        initial=0,
        widget=forms.NumberInput(attrs={"inputmode": "numeric"}),
    )
    infants = forms.IntegerField(
        label=_("Děti do 3 let"),
        min_value=0,
        max_value=MAX_GUESTS,
        initial=0,
        widget=forms.NumberInput(attrs={"inputmode": "numeric"}),
    )
    message = forms.CharField(
        label=_("Poznámka"),
        required=False,
        max_length=2000,
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    website = forms.CharField(
        required=False,
        label="Website",
        widget=forms.TextInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
    )
    started_at = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        """Set date bounds and issue a signed anti-spam timestamp."""
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields["arrival"].widget.attrs["min"] = today.isoformat()
        self.fields["departure"].widget.attrs["min"] = today.isoformat()
        if not self.is_bound:
            self.initial["started_at"] = signing.dumps(
                {"started": time.time()}, salt=FORM_TOKEN_SALT
            )

    def clean_started_at(self):
        """Reject expired, forged, or implausibly fresh form tokens."""
        token = self.cleaned_data["started_at"]
        try:
            payload = signing.loads(
                token,
                salt=FORM_TOKEN_SALT,
                max_age=MAXIMUM_FORM_AGE_SECONDS,
            )
            elapsed = time.time() - float(payload["started"])
        except (signing.BadSignature, KeyError, TypeError, ValueError) as error:
            raise ValidationError(
                _("Platnost formuláře vypršela. Obnovte stránku a zkuste to znovu."),
                code="invalid_form_token",
            ) from error
        if elapsed < MINIMUM_FILL_TIME_SECONDS:
            raise ValidationError(
                _("Formulář byl odeslán příliš rychle. Zkuste to prosím znovu."),
                code="submitted_too_fast",
            )
        return token

    def clean(self):
        """Validate the requested dates and the apartment capacity."""
        cleaned_data = super().clean()
        arrival = cleaned_data.get("arrival")
        departure = cleaned_data.get("departure")
        today = timezone.localdate()
        if arrival and arrival < today:
            self.add_error("arrival", _("Datum příjezdu nemůže být v minulosti."))
        if arrival and departure and departure <= arrival:
            self.add_error(
                "departure", _("Datum odjezdu musí být později než příjezd.")
            )

        guest_counts = (
            cleaned_data.get("adults"),
            cleaned_data.get("children"),
            cleaned_data.get("infants"),
        )
        if all(count is not None for count in guest_counts):
            total_guests = sum(guest_counts)
            if total_guests > MAX_GUESTS:
                raise ValidationError(
                    _("Apartmán má kapacitu nejvýše %(capacity)s hostů."),
                    code="too_many_guests",
                    params={"capacity": MAX_GUESTS},
                )
        return cleaned_data

    @property
    def is_honeypot_filled(self):
        """Return whether an automated submitter filled the trap field."""
        return bool(self.cleaned_data.get("website"))
