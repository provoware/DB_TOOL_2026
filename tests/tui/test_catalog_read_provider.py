import sqlite3
from pathlib import Path

import pytest

from provoware_db.application.catalog_service import CatalogService
from provoware_db.domain.errors import NotFoundError
from provoware_db.tui.catalog_provider import CatalogReadProvider


SCHEMA = Path(__file__).parents[1] / "fixtures" / "cp03_main_schema_v1.sql"


def _connection() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    return con


def _seed(con: sqlite3.Connection) -> None:
    con.execute("INSERT INTO categories(id,name,name_key,sort_order) VALUES('cat-1','Musik','musik',0)")
    con.execute("INSERT INTO entries(id,category_id,title,title_key,is_favorite,sort_order) VALUES('ent-1','cat-1','Track','track',1,0)")
    con.execute("INSERT INTO field_definitions(id,scope,category_id,name,name_key,field_type,is_required,sort_order) VALUES('fld-cat','category','cat-1','BPM','bpm','integer',1,0)")
    con.execute("INSERT INTO field_definitions(id,scope,entry_id,name,name_key,field_type,is_required,sort_order) VALUES('fld-entry','entry','ent-1','Notiz','notiz','text',0,1)")
    con.execute("INSERT INTO scalar_field_values(entry_id,field_definition_id,value_kind,value_integer) VALUES('ent-1','fld-cat','integer',180)")
    con.execute("INSERT INTO scalar_field_values(entry_id,field_definition_id,value_kind,value_text) VALUES('ent-1','fld-entry','text','laut')")
    con.commit()


def _service_for_read_parity(con: sqlite3.Connection) -> CatalogService:
    service = object.__new__(CatalogService)
    from provoware_db.storage.sqlite.repositories import CategoryRepository, EntryRepository, FieldRepository
    service.categories = CategoryRepository(con)
    service.entries = EntryRepository(con)
    service.fields = FieldRepository(con)
    return service


def test_read_provider_matches_catalog_service_read_semantics():
    con = _connection()
    _seed(con)
    provider = CatalogReadProvider(con)
    service = _service_for_read_parity(con)

    assert provider.list_categories() == service.list_categories()
    assert provider.list_entries("cat-1") == service.list_entries("cat-1")
    assert provider.list_entries("missing") == service.list_entries("missing")
    assert provider.list_fields_with_values("ent-1") == service.list_fields_with_values("ent-1")


def test_missing_entry_preserves_dom_101():
    con = _connection()
    provider = CatalogReadProvider(con)

    with pytest.raises(NotFoundError, match="DOM-101: Eintrag wurde nicht gefunden"):
        provider.list_fields_with_values("missing")


def test_provider_does_not_own_or_close_borrowed_connection():
    con = _connection()
    provider = CatalogReadProvider(con)

    provider.list_categories()
    con.execute("SELECT 1").fetchone()
    assert not hasattr(provider, "close")
