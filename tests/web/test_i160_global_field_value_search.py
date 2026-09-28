from __future__ import annotations

import io
import sqlite3

from provoware_db.application.catalog_service import CatalogService
from provoware_db.domain.models import Category, Entry, FieldDefinition, FieldOption, FieldScope, FieldType, ScalarValue
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


def _service(con: sqlite3.Connection) -> CatalogService:
    service = CatalogService.__new__(CatalogService)
    service.categories = CategoryRepository(con)
    service.entries = EntryRepository(con)
    service.fields = FieldRepository(con)

    service.categories.insert(Category.new("cat-1", "Werkzeug"))
    service.entries.insert(Entry.new("ent-1", "cat-1", "Akkuschrauber"))

    text_field = FieldDefinition.new(
        id="fld-text",
        scope=FieldScope.ENTRY,
        entry_id="ent-1",
        name="Notiz",
        field_type=FieldType.TEXT,
    )
    money_field = FieldDefinition.new(
        id="fld-money",
        scope=FieldScope.ENTRY,
        entry_id="ent-1",
        name="Preis",
        field_type=FieldType.MONEY,
        currency_code="EUR",
    )
    choice_field = FieldDefinition.new(
        id="fld-choice",
        scope=FieldScope.ENTRY,
        entry_id="ent-1",
        name="Hersteller",
        field_type=FieldType.SINGLE_CHOICE,
    )
    for field in (text_field, money_field, choice_field):
        service.fields.insert_definition(field)

    service.fields.upsert_scalar_value("ent-1", "fld-text", ScalarValue.from_input(FieldType.TEXT, "Robustes Profigerät"))
    service.fields.upsert_scalar_value("ent-1", "fld-money", ScalarValue.from_input(FieldType.MONEY, 1299))
    option = FieldOption.new("opt-bosch", "fld-choice", "Bosch")
    service.fields.insert_option(option)
    service.fields.set_single_choice("ent-1", "fld-choice", option.id)
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


def test_i160_field_value_search_reaches_service_and_web_with_location() -> None:
    con = _connection()
    try:
        service = _service(con)
        changes_before = con.total_changes

        hits = service.search("profi")
        value_hits = [hit for hit in hits if hit.match_kind == "field_value"]
        assert len(value_hits) == 1
        hit = value_hits[0]
        assert hit.field_id == "fld-text"
        assert hit.value_preview == "Robustes Profigerät"
        assert hit.category_id == "cat-1"
        assert hit.entry_id == "ent-1"

        app = make_app(service)
        status, headers, body = _request(app, query="q=profi")
        assert status == "200 OK"
        assert headers["Cache-Control"] == "no-store"
        assert "Feldwert · Notiz" in body
        assert "Fundstelle: Werkzeug → Akkuschrauber → Notiz" in body
        assert "Wert: Robustes Profigerät" in body
        assert 'href="/?category_id=cat-1&amp;entry_id=ent-1#field-fld-text"' in body

        _, _, money = _request(app, query="q=12%2C99")
        assert "Feldwert · Preis" in money
        assert "Wert: 12,99 EUR" in money

        _, _, choice = _request(app, query="q=bosch")
        assert "Feldwert · Hersteller" in choice
        assert "Wert: Bosch" in choice

        assert con.total_changes == changes_before
    finally:
        con.close()


def test_i160_existing_search_contract_and_get_only_boundary_remain_intact() -> None:
    con = _connection()
    try:
        service = _service(con)
        app = make_app(service)
        changes_before = con.total_changes

        assert service.search("") == []
        existing = service.search("akku")
        assert any(hit.match_kind == "entry_title" and hit.entity_type == "entry" for hit in existing)

        status, headers, body = _request(app, query="q=profi", method="POST")
        assert status == "405 Method Not Allowed"
        assert headers["Allow"] == "GET"
        assert "Nur lesender GET-Zugriff" in body
        assert con.total_changes == changes_before
    finally:
        con.close()


def test_i160_global_limit_remains_authoritative() -> None:
    con = _connection()
    try:
        service = _service(con)
        hits = service.search("a", limit=2)
        assert len(hits) <= 2
    finally:
        con.close()
