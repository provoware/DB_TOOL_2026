from __future__ import annotations

from .errors import ValidationError
from .models import Entry, FieldDefinition, FieldScope


def assert_field_applies_to_entry(field: FieldDefinition, entry: Entry) -> None:
    if field.scope is FieldScope.CATEGORY and field.category_id != entry.category_id:
        raise ValidationError("VAL-440: Dieses Kategorie-Feld gehört nicht zur Kategorie des Eintrags.")
    if field.scope is FieldScope.ENTRY and field.entry_id != entry.id:
        raise ValidationError("VAL-441: Dieses Feld gehört zu einem anderen Eintrag.")
