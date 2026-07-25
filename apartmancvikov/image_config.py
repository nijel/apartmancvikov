# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

from pathlib import PurePosixPath

IMAGE_WIDTHS = (480, 800, 1200, 1600, 1920)


def available_widths(source_width):
    """Return generated widths which do not upscale the source image."""
    return tuple(width for width in IMAGE_WIDTHS if width <= source_width)


def variant_path(path, width, extension):
    """Return the stable static path for one generated image variant."""
    # Django template literals are SafeString instances. Python 3.11's
    # pathlib passes str subclasses to sys.intern(), which only accepts an
    # exact str instance.
    source = PurePosixPath(str.__str__(path))
    return str(
        PurePosixPath("responsive")
        / source.parent
        / f"{source.stem}-{width}.{extension}"
    )
