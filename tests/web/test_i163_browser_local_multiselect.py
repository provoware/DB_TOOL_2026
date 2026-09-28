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


def _request(app, path: str = "/", query: str = "") -> tuple[str, dict[str, str], str]:
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(),
    }
    body = b"".join(app(environ, start_response)).decode("utf-8")
    return str(captured["status"]), dict(captured["headers"]), body


def test_i163_multiselect_markup_is_browser_local_and_read_only() -> None:
    con = _connection()
    try:
        app = _app(con)
        changes_before = con.total_changes
        status, _, body = _request(app, query="category_id=cat-1")

        assert status == "200 OK"
        assert "Mehrfachauswahl" in body
        assert 'id="multiselect-count"' in body
        assert "0 ausgewählt" in body
        assert 'id="multiselect-clear" disabled' in body
        assert body.count('class="entry-multiselect"') == 2
        assert 'data-entry-id="ent-a"' in body
        assert 'data-entry-id="ent-b"' in body
        assert "Nur temporär im Browser · keine Speicherung" in body
        assert '<script src="/static/app.js" defer></script>' in body
        assert con.total_changes == changes_before
    finally:
        con.close()


def test_i163_script_is_static_and_uses_no_persistence_or_network() -> None:
    source = APP_JS.read_text(encoding="utf-8")

    assert "localStorage" not in source
    assert "sessionStorage" not in source
    assert "fetch(" not in source
    assert "XMLHttpRequest" not in source
    assert 'addEventListener("change"' in source
    assert 'addEventListener("click"' in source
    assert "toggleAttribute" in source


def test_i163_static_script_is_served_no_store() -> None:
    con = _connection()
    try:
        app = _app(con)
        status, headers, body = _request(app, path="/static/app.js")

        assert status == "200 OK"
        assert headers["Content-Type"] == "text/javascript; charset=utf-8"
        assert headers["Cache-Control"] == "no-store"
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert "multiselect-count" in body
    finally:
        con.close()
