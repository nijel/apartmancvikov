# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from functools import lru_cache

import qrcode
from django import template
from django.utils.safestring import mark_safe
from qrcode.image.svg import SvgPathFillImage

register = template.Library()


@lru_cache(maxsize=128)
def _qr_svg(url: str):
    """Generate a compact, print-ready SVG QR code for a canonical URL."""
    code = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=1,
        border=4,
        image_factory=SvgPathFillImage,
    )
    code.add_data(url)
    code.make(fit=True)
    image = code.make_image(
        attrib={
            "class": "print-header__qr-code",
            "aria-hidden": "true",
            "focusable": "false",
        }
    )
    return mark_safe(image.to_string(encoding="unicode"))  # noqa: S308


@register.inclusion_tag("snippets/print_header.html")
def trip_print_header(title, url, subtitle=None):
    """Render the apartment print header with a QR link to the current page."""
    canonical_url = str(url)
    return {
        "print_title": title,
        "print_subtitle": subtitle,
        "print_url": canonical_url,
        "print_qr_svg": _qr_svg(canonical_url),
    }
