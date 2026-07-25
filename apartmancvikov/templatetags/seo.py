# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: AGPL-3.0

import json
import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def nbsp_prepositions(value):
    """Keep short Czech prepositions and conjunctions with the next word."""
    return re.sub(
        r"(?i)\b(a|i|k|o|s|u|v|z|na|ve|do|ke|ze|od|po|za|pro|při|bez|pod|nad|před|mezi) ",
        lambda match: f"{match.group(1)}\N{NO-BREAK SPACE}",
        str(value),
    )


@register.simple_tag
def json_ld(value):
    """Serialize a value as an injection-safe JSON-LD script element."""
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e")
    payload = payload.replace("&", "\\u0026")
    return mark_safe(f'<script type="application/ld+json">{payload}</script>')  # noqa: S308
