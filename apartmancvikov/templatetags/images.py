# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from django import template

from apartmancvikov.images import responsive_image_context, variant_url

register = template.Library()


@register.inclusion_tag("snippets/responsive_image.html")
def responsive_image(  # noqa: PLR0913
    path,
    width,
    height,
    alt,
    *,
    sizes="100vw",
    loading="lazy",
    fetchpriority=None,
    picture_class=None,
    image_class=None,
):
    """Render an image with responsive JPEG and WebP alternatives."""
    return responsive_image_context(
        path,
        width,
        height,
        alt,
        sizes=sizes,
        loading=loading,
        fetchpriority=fetchpriority,
        picture_class=picture_class,
        image_class=image_class,
    )


@register.simple_tag
def responsive_image_url(path, width, preferred_width=None):
    """Return a large optimized JPEG URL suitable for the lightbox."""
    return variant_url(path, width, preferred_width=preferred_width)
