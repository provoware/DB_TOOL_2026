from __future__ import annotations

import sqlite3
import unittest

from provoware_db.application.catalog_service import CatalogService
from provoware_db.domain.models import (
    Category,
    Entry,
    FieldDefinition,
    FieldOption,
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
from provoware_db.web.render import render_page


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


def _service_with_values(con: sqlite3.Connection) -> CatalogService:
    service = CatalogService.__new__(CatalogService)
    service.categories = CategoryRepository(con)
    service.entries = EntryRepository(con)
    service.fields = FieldRepository(con)

    service.categories.insert(Category.new("cat-1", "Werkzeug"))
    service.entries.insert(Entry.new("ent-1", "cat-1", "Akkuschrauber"))

    text_field = FieldDefinition.new(
        id="fld-text",
        scope=FieldScope.CATEGORY,
        category_id="cat-1",
        name="Hersteller",
        field_type=FieldType.TEXT,
        sort_order=1,
    )
    single_field = FieldDefinition.new(
        id="fld-single",
        scope=FieldScope.CATEGORY,
        category_id="cat-1",
        name="Zustand",
        field_type=FieldType.SINGLE_CHOICE,
        sort_order=2,
    )
    multi_field = FieldDefinition.new(
        id="fld-multi",
        scope=FieldScope.CATEGORY,
        category_id="cat-1",
        name="Merkmale",
        field_type=FieldType.MULTI_CHOICE,
        sort_order=3,
    )
    empty_field = FieldDefinition.new(
        id="fld-empty",
        scope=FieldScope.CATEGORY,
        category_id="cat-1",
        name="Notiz",
        field_type=FieldType.TEXT,
        sort_order=4,
    )
    for field in (text_field, single_field, multi_field, empty_field):
        service.fields.insert_definition(field)

    good = FieldOption.new("opt-good", single_field.id, "Gut")
    battery = FieldOption.new("opt-battery", multi_field.id, "Akku")
    brushless = FieldOption.new("opt-brushless", multi_field.id, "Bürstenlos")
    for option in (good, battery, brushless):
        service.fields.insert_option(option)

    service.fields.upsert_scalar_value(
        "ent-1",
        text_field.id,
        ScalarValue.from_input(FieldType.TEXT, "Bosch"),
    )
    service.fields.set_single_choice("ent-1", single_field.id, good.id)
    service.fields.set_multi_choice(
        "ent-1",
        multi_field.id,
        [battery.id, brushless.id],
    )
    return service


class ReadOnlyFieldValueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.con = _connection()
        self.service = _service_with_values(self.con)
        self.adapter = WebCatalogReadAdapter(self.service)

    def tearDown(self) -> None:
        self.con.close()

    def test_service_and_adapter_read_scalar_single_and_multi_values(self) -> None:
        items = {item.label: item for item in self.adapter.fields("ent-1")}

        self.assertEqual(items["Hersteller"].value, "Bosch")
        self.assertEqual(items["Zustand"].value, "Gut")
        self.assertEqual(items["Merkmale"].value, "Akku, Bürstenlos")
        self.assertEqual(items["Notiz"].value, "Nicht gesetzt")

    def test_renderer_shows_values_without_exposing_write_controls(self) -> None:
        page = render_page(
            self.adapter,
            category_id="cat-1",
            entry_id="ent-1",
        )

        self.assertIn("Wert: </span><strong>Bosch</strong>", page)
        self.assertIn("Wert: </span><strong>Gut</strong>", page)
        self.assertIn("Wert: </span><strong>Akku, Bürstenlos</strong>", page)
        self.assertIn("Wert: </span><strong>Nicht gesetzt</strong>", page)
        self.assertIn("🔒 NUR LESEN", page)
        self.assertGreaterEqual(page.count('disabled aria-disabled="true"'), 4)


if __name__ == "__main__":
    unittest.main()
