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


def _real_read_service(con: sqlite3.Connection) -> CatalogService:
    service = CatalogService.__new__(CatalogService)
    service.categories = CategoryRepository(con)
    service.entries = EntryRepository(con)
    service.fields = FieldRepository(con)
    service.categories.insert(Category.new("cat-1", "Werkzeug"))
    service.entries.insert(Entry.new("ent-1", "cat-1", "Akkuschrauber"))
    service.fields.insert_definition(FieldDefinition.new(id="fld-1", scope=FieldScope.CATEGORY, category_id="cat-1", name="Hersteller", field_type=FieldType.TEXT, is_required=True))
    return service


def _request(app, *, query: str = "", method: str = "GET", path: str = "/") -> tuple[str, dict[str, str], str]:
    captured: dict[str, object] = {}
    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)
    environ = {"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query, "wsgi.input": io.BytesIO()}
    body = b"".join(app(environ, start_response)).decode("utf-8")
    return str(captured["status"]), dict(captured["headers"]), body


class ReadOnlyHttpNavigationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.con = _connection()
        self.app = make_app(_real_read_service(self.con))

    def tearDown(self) -> None:
        self.con.close()

    def test_category_entry_field_navigation_marks_current_selection(self) -> None:
        status, _, root = _request(self.app)
        self.assertEqual(status, "200 OK")
        self.assertIn("Werkzeug", root)
        self.assertNotIn("✓ Ausgewählt", root)
        status, _, category = _request(self.app, query="category_id=cat-1")
        self.assertEqual(status, "200 OK")
        self.assertIn("Akkuschrauber", category)
        self.assertIn('data-id="cat-1" aria-current="true"', category)
        self.assertEqual(category.count("✓ Ausgewählt"), 1)
        status, headers, entry = _request(self.app, query="category_id=cat-1&entry_id=ent-1")
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn('data-id="cat-1" aria-current="true"', entry)
        self.assertIn('data-id="ent-1" aria-current="true"', entry)
        self.assertEqual(entry.count("✓ Ausgewählt"), 2)
        self.assertIn("Hersteller", entry)
        self.assertIn("text · Pflichtfeld", entry)

    def test_http_surface_is_read_only_and_serves_only_fixed_css_asset(self) -> None:
        status, headers, css = _request(self.app, path="/static/app.css")
        self.assertEqual(status, "200 OK")
        self.assertIn("text/css", headers["Content-Type"])
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIn(":root", css)
        status, headers, _ = _request(self.app, method="POST")
        self.assertEqual(status, "405 Method Not Allowed")
        self.assertEqual(headers["Allow"], "GET")
        status, _, _ = _request(self.app, path="/write")
        self.assertEqual(status, "404 Not Found")
        status, _, _ = _request(self.app, path="/static/anything-else.css")
        self.assertEqual(status, "404 Not Found")


if __name__ == "__main__":
    unittest.main()
