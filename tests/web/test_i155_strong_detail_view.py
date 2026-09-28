from __future__ import annotations

import io
import sqlite3

from provoware_db.application.catalog_service import CatalogService
from provoware_db.domain.models import Category, Entry, FieldDefinition, FieldScope, FieldType
from provoware_db.storage.sqlite.repositories import CategoryRepository, EntryRepository, FieldRepository
from provoware_db.web.http_app import make_app


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
          id TEXT PRIMARY KEY, field_definition_id TEXT NOT NULL,
          label TEXT NOT NULL, option_key TEXT NOT NULL,
          sort_order INTEGER NOT NULL DEFAULT 0, deleted_at TEXT
        );
        CREATE TABLE scalar_field_values(
          entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL,
          value_kind TEXT NOT NULL, value_text TEXT, value_integer INTEGER,
          value_real REAL
        );
        CREATE TABLE single_choice_values(
          entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL, option_id TEXT NOT NULL
        );
        CREATE TABLE multi_choice_values(
          entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL, option_id TEXT NOT NULL
        );
        """
    )
    return con


def _app(con: sqlite3.Connection):
    service = CatalogService.__new__(CatalogService)
    service.categories = CategoryRepository(con)
    service.entries = EntryRepository(con)
    service.fields = FieldRepository(con)
    service.categories.insert(Category.new("cat-1", "Werkzeug"))
    service.entries.insert(Entry.new("ent-1", "cat-1", "Akkuschrauber"))
    service.entries.insert(Entry.new("ent-empty", "cat-1", "Leerer Eintrag"))
    service.fields.insert_definition(
        FieldDefinition.new(
            id="fld-1",
            scope=FieldScope.CATEGORY,
            category_id="cat-1",
            name="Hersteller",
            field_type=FieldType.TEXT,
            is_required=True,
        )
    )
    return make_app(service)


def _request(app, query: str) -> str:
    captured: dict[str, object] = {}
    def start_response(status, headers):
        captured["status"] = status
    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/",
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(),
    }
    body = b"".join(app(environ, start_response)).decode("utf-8")
    assert captured["status"] == "200 OK"
    return body


def test_i155_strong_detail_has_explicit_context_count_and_stable_targets() -> None:
    con = _connection()
    try:
        app = _app(con)
        changes_before = con.total_changes
        body = _request(app, "category_id=cat-1&entry_id=ent-1")

        assert 'id="detail"' in body
        assert 'aria-labelledby="detail-title"' in body
        assert "Eintragsdetails" in body
        assert "Kategorie:" in body
        assert "Werkzeug" in body
        assert "<h3>Akkuschrauber</h3>" in body
        assert "1 sichtbare Felder" in body
        assert 'id="field-fld-1"' in body
        assert "Hersteller" in body
        assert con.total_changes == changes_before
    finally:
        con.close()


def test_i155_detail_empty_and_unselected_states_are_clear() -> None:
    con = _connection()
    try:
        app = _app(con)

        root = _request(app, "")
        assert "Bitte zuerst einen Eintrag wählen." in root

        empty = _request(app, "category_id=cat-1&entry_id=ent-empty")
        assert "<h3>Leerer Eintrag</h3>" in empty
        assert "0 sichtbare Felder" in empty
        assert 'id="detail-empty"' in empty
        assert "Keine sichtbaren Felder vorhanden." in empty
    finally:
        con.close()
