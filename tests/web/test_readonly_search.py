from __future__ import annotations

import io
import sqlite3
import unittest

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
            id="fld-1",
            scope=FieldScope.CATEGORY,
            category_id="cat-1",
            name="Hersteller",
            field_type=FieldType.TEXT,
        )
    )
    return service


def _request(app, *, query: str = "", method: str = "GET") -> tuple[str, str]:
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": "/",
        "QUERY_STRING": query,
        "wsgi.input": io.BytesIO(),
    }
    body = b"".join(app(environ, start_response)).decode("utf-8")
    return str(captured["status"]), body


class ReadOnlySearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.con = _connection()
        self.app = make_app(_service(self.con))

    def tearDown(self) -> None:
        self.con.close()

    def test_search_form_is_get_based_and_keyboard_native(self) -> None:
        status, page = _request(self.app)
        self.assertEqual(status, "200 OK")
        self.assertIn('form method="get" action="/" role="search"', page)
        self.assertIn('input id="search-query" name="q" type="search"', page)
        self.assertIn(">Suchen</button>", page)
        self.assertIn("Suchbegriff eingeben.", page)

    def test_search_returns_category_entry_and_field_hits(self) -> None:
        status, category = _request(self.app, query="q=werk")
        self.assertEqual(status, "200 OK")
        self.assertIn("Kategorie · Werkzeug", category)
        self.assertIn("category_id=cat-1", category)

        status, entry = _request(self.app, query="q=akku")
        self.assertEqual(status, "200 OK")
        self.assertIn("Eintrag · Akkuschrauber", entry)
        self.assertIn("category_id=cat-1&amp;entry_id=ent-1", entry)

        status, field = _request(self.app, query="q=hersteller")
        self.assertEqual(status, "200 OK")
        self.assertIn("Feld · Hersteller", field)

    def test_no_results_and_write_method_stay_clear_and_blocked(self) -> None:
        status, page = _request(self.app, query="q=nichtvorhanden")
        self.assertEqual(status, "200 OK")
        self.assertIn("Keine Treffer für „nichtvorhanden“.", page)

        status, body = _request(self.app, query="q=werk", method="POST")
        self.assertEqual(status, "405 Method Not Allowed")
        self.assertIn("Nur lesender GET-Zugriff", body)


if __name__ == "__main__":
    unittest.main()
