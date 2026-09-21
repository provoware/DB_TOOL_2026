from enum import StrEnum

from provoware_db.field_type_labels import FIELD_TYPE_LABELS, field_type_label


class Kind(StrEnum):
    TEXT = "text"


def test_field_type_labels_cover_all_current_domain_values() -> None:
    assert FIELD_TYPE_LABELS == {
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


def test_field_type_label_accepts_enum_or_raw_string_and_falls_back() -> None:
    assert field_type_label(Kind.TEXT) == "Text"
    assert field_type_label("boolean") == "Ja / Nein"
    assert field_type_label("future_type") == "future_type"


if __name__ == "__main__":
    test_field_type_labels_cover_all_current_domain_values()
    test_field_type_label_accepts_enum_or_raw_string_and_falls_back()
