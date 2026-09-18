from __future__ import annotations

import sqlite3
import unittest

from provoware_db.application.catalog_service import CatalogService
from provoware_db.domain.models import (
    Category,
    Entry,
    FieldDefinition,
    FieldScope,
    FieldType,
    ScalarValue,
)
from provoware_db.storage.sqlite.repositories import (
    CategoryRepository,
    EntryRepository,
    FieldRepository,
)
from provoware_db.web.read_adapter import WebCatalogReadAdapter


def _connection() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE categories(
          id TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL,
          description TEXT, sort_order INTEGER NOT NULL DEFAULT 0,
          created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', deleted_at TEXT,
          revision INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE entries(
          id TEXT PRIMARY KEY, category_id TEXT NOT NULL, title TEXT NOT NULL,
          title_key TEXT NOT NULL, is_favorite INTEGER NOT NULL DEFAULT 0,
          sort_order INTEGER NOT NULL DEFAULT 0, created_at TEXT DEFAULT '',
          updated_at TEXT DEFAULT '', deleted_at TEXT, revision INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE field_definitions(
          id TEXT PRIMARY KEY, scope TEXT NOT NULL, category_id TEXT, entry_id TEXT,
          name TEXT NOT NULL, name_key TEXT NOT NULL, field_type TEXT NOT NULL,
          is_required INTEGER NOT NULL DEFAULT 0, sort_order INTEGER NOT NULL DEFAULT 0,
          help_text TEXT, placeholder TEXT, unit_label TEXT, currency_code TEXT,
          created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', deleted_at TEXT,
          revision INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE field_options(
          id TEXT PRIMARY KEY, field_definition_id TEXT NOT NULL, label TEXT NOT NULL,
          option_key TEXT NOT NULL, sort_order INTEGER NOT NULL DEFAULT 0,
          created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', deleted_at TEXT
        );
        CREATE TABLE scalar_field_values(
          entry_id TEXT, field_definition_id TEXT, value_kind TEXT,
          value_text TEXT, value_integer INTEGER, value_real REAL,
          created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '',
          revision INTEGER NOT NULL DEFAULT 1,
          PRIMARY KEY(entry_id, field_definition_id)
        );
        CREATE TABLE single_choice_values(
          entry_id TEXT, field_definition_id TEXT, option_id TEXT,
          created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '',
          revision INTEGER NOT NULL DEFAULT 1,
          PRIMARY KEY(entry_id, field_definition_id)
        );
        CREATE TABLE multi_choice_values(
          entry_id TEXT, field_definition_id TEXT, option_id TEXT,
          created_at TEXT DEFAULT '',
          PRIMARY KEY(entry_id, field_definition_id, option_id)
        );
        """
    )
    return con


def _service(con: sqlite3.Connection) -> CatalogService:
    service = CatalogService.__new__(CatalogService)
    service.categories = CategoryRepository(con)
    service.entries = EntryRepository(con)
    service.fields = FieldRepository(con)
    service.categories.insert(Category.new("cat-1", "Werkzeug"))
    service.entries.insert(Entry.new("ent-1", "cat-1", "Akkuschrauber"))
    return service


class ValueFormatAndQueryGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.con = _connection()
        self.service = _service(self.con)

    def tearDown(self) -> None:
        self.con.close()

    def _add_scalar(
        self,
        field_id: str,
        name: str,
        field_type: FieldType,
        value,
        *,
        unit_label: str | None = None,
        currency_code: str | None = None,
        sort_order: int = 0,
    ) -> None:
        field = FieldDefinition.new(
            id=field_id,
            scope=FieldScope.CATEGORY,
            category_id="cat-1",
            name=name,
            field_type=field_type,
            unit_label=unit_label,
            currency_code=currency_code,
            sort_order=sort_order,
        )
        self.service.fields.insert_definition(field)
        self.service.fields.upsert_scalar_value(
            "ent-1",
            field_id,
            ScalarValue.from_input(field_type, value),
        )

    def test_beginner_friendly_value_formats(self) -> None:
        self._add_scalar("f-date", "Kaufdatum", FieldType.DATE, "2026-09-18", sort_order=1)
        self._add_scalar(
            "f-datetime",
            "Erfasst",
            FieldType.DATETIME,
            "2026-09-18T21:30:00",
            sort_order=2,
        )
        self._add_scalar(
            "f-money",
            "Preis",
            FieldType.MONEY,
            12345,
            currency_code="EUR",
            sort_order=3,
        )
        self._add_scalar("f-int", "Stückzahl", FieldType.INTEGER, 7, sort_order=4)
        self._add_scalar("f-dec", "Spannung", FieldType.DECIMAL, "18.5", unit_label="V", sort_order=5)
        self._add_scalar("f-yes", "Geprüft", FieldType.BOOLEAN, True, sort_order=6)
        self._add_scalar("f-no", "Defekt", FieldType.BOOLEAN, False, sort_order=7)

        items = {item.label: item.value for item in WebCatalogReadAdapter(self.service).fields("ent-1")}

        self.assertEqual(items["Kaufdatum"], "18.09.2026")
        self.assertEqual(items["Erfasst"], "18.09.2026, 21:30")
        self.assertEqual(items["Preis"], "123,45 EUR")
        self.assertEqual(items["Stückzahl"], "7")
        self.assertEqual(items["Spannung"], "18,5 V")
        self.assertEqual(items["Geprüft"], "Ja")
        self.assertEqual(items["Defekt"], "Nein")

    def test_many_scalar_fields_do_not_scale_queries_per_field(self) -> None:
        for index in range(12):
            self._add_scalar(
                f"f-{index:02d}",
                f"Feld {index:02d}",
                FieldType.TEXT,
                f"Wert {index:02d}",
                sort_order=index,
            )

        statements: list[str] = []
        self.con.set_trace_callback(
            lambda sql: statements.append(sql)
            if sql.lstrip().upper().startswith("SELECT")
            else None
        )
        try:
            items = WebCatalogReadAdapter(self.service).fields("ent-1")
        finally:
            self.con.set_trace_callback(None)

        self.assertEqual(len(items), 12)
        query_count = len(statements)
        self.assertLessEqual(
            query_count,
            8,
            f"N+1-Befund: 12 Felder verursachten {query_count} SELECT-Abfragen.",
        )


if __name__ == "__main__":
    unittest.main()
