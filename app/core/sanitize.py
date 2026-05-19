import re

_HTML_TAG_RE = re.compile(r'<[^>]+>')
_NULL_BYTE_RE = re.compile(r'\x00')


def strip_html(value: str) -> str:
    value = _NULL_BYTE_RE.sub('', value)
    return _HTML_TAG_RE.sub('', value)


def sanitize_text(value: str | None) -> str | None:
    if value is None:
        return None
    return strip_html(value).strip()
