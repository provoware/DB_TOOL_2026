from __future__ import annotations

import sqlite3

from provoware_db.domain.errors import NotFoundError
from provoware_db.domain.models import Category, Entry, FieldDefinition, FieldOption, ScalarValue
from provoware_db.storage.sqlite.repositories import CategoryRepository, EntryRepository, FieldRepository


class CatalogReadProvider:
    """Read-only catalog provider over a borrowed SQLite connection."""

    def __init__(self, con: sqlite3.Connection) -> None:
        self._categories = CategoryRepository(con)
        self._entries = EntryRepository(con)
        self._fields = FieldRepository(con)

    def list_categories(self) -> list[Category]:
        return self._categories.list_active()

    def list_entries(self, category_id: str) -> list[Entry]:
        if self._categories.get_active(category_id) is None:
            return []
        return self._entries.list_active_by_category(category_id)

    def list_fields_with_values(
        self,
        entry_id: str,
    ) -> list[tuple[FieldDefinition, ScalarValue | FieldOption | list[FieldOption] | None]]:
        entry = self._entries.get_active(entry_id)
        if entry is None:
            raise NotFoundError("DOM-101: Eintrag wurde nicht gefunden.")
        fields = self._fields.list_visible_for_entry(entry.id, entry.category_id)
        values = self._fields.list_values_for_entry(entry.id)
        return [(field, values.get(field.id)) for field in fields]
