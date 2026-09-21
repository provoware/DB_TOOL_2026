from __future__ import annotations

from collections.abc import Mapping


FIELD_TYPE_LABELS: Mapping[str, str] = {
    "text": "Text",
    "long_text": "Langer Text",
    "integer": "Ganzzahl",
    "decimal": "Dezimalzahl",
    "money": "Geldbetrag",
    "date": "Datum",
    "datetime": "Datum und Uhrzeit",
    "boolean": "Ja / Nein",
    "single_choice": "Einfachauswahl",
    "multi_choice": "Mehrfachauswahl",
}


def field_type_label(value: object) -> str:
    """Return the shared lay-friendly label for a field-type value."""
    raw = str(getattr(value, "value", value))
    return FIELD_TYPE_LABELS.get(raw, raw)
