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
    service.fields.insert_definition(
        FieldDefinition.new(
            id="fld-cat",
            scope=FieldScope.CATEGORY,
            category_id="cat-1",
            name="Hersteller",
            field_type=FieldType.TEXT,
        )
    )
    service.fields.insert_definition(
        FieldDefinition.new(
            id="fld-ent",
            scope=FieldScope.ENTRY,
            entry_id="ent-1",
            name="Seriennummer",
            field_type=FieldType.TEXT,
        )
    )
    return service


def _request(app, *, query: str = "", method: str = "GET") -> tuple[str, dict[str, str], str]:
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": "/",
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(),
    }
    body = b"".join(app(environ, start_response)).decode("utf-8")
    return str(captured["status"]), dict(captured["headers"]), body


def test_i148_readonly_search_end_to_end_contract() -> None:
    con = _connection()
    try:
        service = _service(con)
        app = make_app(service)

        assert service.search("") == []
        assert service.search("   ") == []

        changes_before = con.total_changes

        status, headers, empty = _request(app)
        assert status == "200 OK"
        assert headers["Cache-Control"] == "no-store"
        assert "Suchbegriff eingeben." in empty

        status, _, category = _request(app, query="q=werk")
        assert status == "200 OK"
        assert "Kategorie · Werkzeug" in category
        assert 'href="/?category_id=cat-1"' in category

        status, _, entry = _request(app, query="q=akku")
        assert status == "200 OK"
        assert "Eintrag · Akkuschrauber" in entry
        assert 'href="/?category_id=cat-1&amp;entry_id=ent-1"' in entry

        status, _, category_field = _request(app, query="q=hersteller")
        assert status == "200 OK"
        assert "Feld · Hersteller" in category_field
        assert 'href="/?category_id=cat-1"' in category_field

        hits = service.search("serien")
        assert len(hits) == 1
        assert hits[0].entity_type == "field_definition"
        assert hits[0].category_id == "cat-1"
        assert hits[0].entry_id == "ent-1"

        status, _, entry_field = _request(app, query="q=serien")
        assert status == "200 OK"
        assert "Feld · Seriennummer" in entry_field
        assert 'href="/?category_id=cat-1&amp;entry_id=ent-1"' in entry_field

        status, _, none = _request(app, query="q=nichtvorhanden")
        assert status == "200 OK"
        assert "Keine Treffer für „nichtvorhanden“." in none

        assert con.total_changes == changes_before

        status, headers, body = _request(app, query="q=werk", method="POST")
        assert status == "405 Method Not Allowed"
        assert headers["Allow"] == "GET"
        assert "Nur lesender GET-Zugriff" in body
        assert con.total_changes == changes_before
    finally:
        con.close()


def test_i148_search_excludes_entry_field_when_parent_category_is_deleted() -> None:
    con = _connection()
    try:
        service = _service(con)
        con.execute("UPDATE categories SET deleted_at='2026-09-28T00:00:00Z' WHERE id='cat-1'")
        assert service.search("serien") == []
        assert service.search("akku") == []
    finally:
        con.close()
