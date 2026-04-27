"""Shared Pydantic validators and sanitizers used across schema modules."""

import re

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(v: str | None) -> str | None:
    """Remove HTML tags from a string value.

    Use in Pydantic field_validator(mode="before") to sanitize user input.
    """
    if v is None:
        return v
    return _HTML_TAG_RE.sub("", v).strip()
