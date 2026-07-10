import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def json_ld(value):
    """Serialize a value as an injection-safe JSON-LD script element."""
    payload = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e")
    payload = payload.replace("&", "\\u0026")
    return mark_safe(f'<script type="application/ld+json">{payload}</script>')  # noqa: S308
