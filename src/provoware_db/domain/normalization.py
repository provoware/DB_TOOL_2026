from __future__ import annotations

import re
import unicodedata

_SPACE_RE = re.compile(r"\s+")


def clean_text(value: str) -> str:
    return _SPACE_RE.sub(" ", unicodedata.normalize("NFKC", value).strip())


def make_key(value: str) -> str:
    return clean_text(value).casefold()
