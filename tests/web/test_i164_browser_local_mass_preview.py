from __future__ import annotations

import io
import sqlite3
from pathlib import Path

from provoware_db.application.catalog_service import CatalogService
from provoware_db.domain.models import Category, Entry
from provoware_db.storage.sqlite.repositories import CategoryRepository, EntryRepository, FieldRepository
from provoware_db.web.http_app import make_app


ROOT = Path(__file__).resolve().parents[2]
APP_JS = ROOT / "src" / "provoware_db" / "web" / "static" / "app.js"


def _connection() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE categories(id TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL,
          description TEXT, sort_order INTEGER NOT NULL DEFAULT 0, created_at TEXT DEFAULT '',
          updated_at TEXT DEFAULT '', deleted_at TEXT, revision INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE entries(id TEXT PRIMARY KEY, category_id TEXT NOT NULL, title TEXT NOT NULL,
          title_key TEXT NOT NULL, is_favorite INTEGER NOT NULL DEFAULT 0, sort_order INTEGER NOT NULL DEFAULT 0,
          created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', deleted_at TEXT, revision INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE field_definitions(id TEXT PRIMARY KEY, scope TEXT NOT NULL, category_id TEXT, entry_id TEXT,
          name TEXT NOT NULL, name_key TEXT NOT NULL, field_type TEXT NOT NULL, is_required INTEGER NOT NULL DEFAULT 0,
          sort_order INTEGER NOT NULL DEFAULT 0, help_text TEXT, placeholder TEXT, unit_label TEXT, currency_code TEXT,
          created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', deleted_at TEXT, revision INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE field_options(id TEXT PRIMARY KEY, field_definition_id TEXT NOT NULL, label TEXT NOT NULL,
          option_key TEXT NOT NULL, sort_order INTEGER NOT NULL DEFAULT 0, deleted_at TEXT);
        CREATE TABLE scalar_field_values(entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL,
          value_kind TEXT NOT NULL, value_text TEXT, value_integer INTEGER, value_real REAL);
        CREATE TABLE single_choice_values(entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL, option_id TEXT NOT NULL);
        CREATE TABLE multi_choice_values(entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL, option_id TEXT NOT NULL);
        """
    )
    return con


def _app(con: sqlite3.Connection):
    service = CatalogService.__new__(CatalogService)
    service.categories = CategoryRepository(con)
    service.entries = EntryRepository(con)
    service.fields = FieldRepository(con)
    service.categories.insert(Category.new("cat-1", "Werkzeug"))
    service.entries.insert(Entry.new("ent-a", "cat-1", "Akkuschrauber"))
    service.entries.insert(Entry.new("ent-b", "cat-1", "Bohrhammer"))
    return make_app(service)


def _request(app, query: str = "") -> str:
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


def test_i164_preview_markup_is_read_only_and_explicit() -> None:
    con = _connection()
    try:
        app = _app(con)
        changes_before = con.total_changes
        body = _request(app, "category_id=cat-1")

        assert 'id="mass-preview"' in body
        assert "Vorschau für Massenaktion" in body
        assert 'id="mass-preview-summary"' in body
        assert "Keine Einträge ausgewählt." in body
        assert 'id="mass-preview-list"' in body
        assert "Es wird nichts geändert oder gespeichert." in body
        assert con.total_changes == changes_before
    finally:
        con.close()


def test_i164_script_builds_preview_from_current_dom_only() -> None:
    source = APP_JS.read_text(encoding="utf-8")

    assert "mass-preview-summary" in source
    assert "mass-preview-list" in source
    assert "replaceChildren" in source
    assert "document.createElement" in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source
    assert "fetch(" not in source
    assert "XMLHttpRequest" not in source
    assert "Diese Vorschau würde" in source


def test_i164_preview_has_no_execute_control() -> None:
    con = _connection()
    try:
        body = _request(_app(con), "category_id=cat-1")
        assert "Massenaktion ausführen" not in body
        assert "Jetzt anwenden" not in body
        assert 'type="submit"' not in body.split('id="mass-preview"', 1)[1].split("</section>", 1)[0]
    finally:
        con.close()
