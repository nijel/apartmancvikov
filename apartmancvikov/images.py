# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from django.templatetags.static import static

from .image_config import available_widths, variant_path


def variant_url(path, source_width, extension="jpg", preferred_width=None):
    """Return the URL of the best generated variant at or below a target width."""
    widths = available_widths(source_width)
    if not widths:
        return static(path)
    target = preferred_width or widths[-1]
    width = max((item for item in widths if item <= target), default=widths[0])
    return static(variant_path(path, width, extension))


def responsive_image_context(  # noqa: PLR0913
    path,
    source_width,
    source_height,
    alt,
    sizes="100vw",
    loading="lazy",
    fetchpriority=None,
    picture_class=None,
    image_class=None,
):
    """Build URLs and dimensions for the responsive image inclusion template."""
    widths = available_widths(source_width)
    if not widths:
        return {
            "alt": alt,
            "fetchpriority": fetchpriority,
            "height": source_height,
            "image_class": image_class,
            "jpeg_srcset": "",
            "loading": loading,
            "picture_class": picture_class,
            "sizes": sizes,
            "src": static(path),
            "webp_srcset": "",
            "width": source_width,
        }

    def srcset(extension):
        return ", ".join(
            f"{static(variant_path(path, width, extension))} {width}w"
            for width in widths
        )

    return {
        "alt": alt,
        "fetchpriority": fetchpriority,
        "height": source_height,
        "image_class": image_class,
        "jpeg_srcset": srcset("jpg"),
        "loading": loading,
        "picture_class": picture_class,
        "sizes": sizes,
        "src": static(path),
        "webp_srcset": srcset("webp"),
        "width": source_width,
    }
