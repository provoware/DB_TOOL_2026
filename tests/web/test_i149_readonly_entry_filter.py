from __future__ import annotations

import io
import sqlite3

from provoware_db.application.catalog_service import CatalogService
from provoware_db.domain.models import Category, Entry
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
          id TEXT PRIMARY KEY, field_definition_id TEXT NOT NULL, label TEXT NOT NULL,
          option_key TEXT NOT NULL, sort_order INTEGER NOT NULL DEFAULT 0, deleted_at TEXT
        );
        CREATE TABLE scalar_field_values(
          entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL, value_kind TEXT NOT NULL,
          value_text TEXT, value_integer INTEGER, value_real REAL
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
    service.entries.insert(Entry.new("ent-2", "cat-1", "Bohrhammer"))
    service.entries.insert(Entry.new("ent-3", "cat-1", "Akku Lampe"))
    return make_app(service)


def _request(app, query: str) -> tuple[str, str]:
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
    return str(captured["status"]), body


def test_i149_filters_only_visible_entry_titles_and_stays_read_only() -> None:
    con = _connection()
    try:
        app = _app(con)
        changes_before = con.total_changes

        status, body = _request(app, "category_id=cat-1&filter=AKKU")
        assert status == "200 OK"
        assert "Akkuschrauber" in body
        assert "Akku Lampe" in body
        assert "Bohrhammer" not in body
        assert "2 Einträge sichtbar" in body
        assert 'value="AKKU"' in body
        assert con.total_changes == changes_before
    finally:
        con.close()


def test_i149_empty_and_no_match_filter_states_are_clear() -> None:
    con = _connection()
    try:
        app = _app(con)

        _, unfiltered = _request(app, "category_id=cat-1&filter=%20%20")
        assert "Akkuschrauber" in unfiltered
        assert "Bohrhammer" in unfiltered
        assert "Titel-Filter ist aus." in unfiltered

        _, none = _request(app, "category_id=cat-1&filter=fr%C3%A4se")
        assert "Akkuschrauber" not in none
        assert "Bohrhammer" not in none
        assert "0 Einträge sichtbar" in none
        assert "Bitte zuerst eine Kategorie wählen." in none
    finally:
        con.close()
