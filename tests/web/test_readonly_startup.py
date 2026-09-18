from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from provoware_db.storage.sqlite.errors import SchemaGuardError
from provoware_db.web.startup import build_readonly_runtime, run_local_readonly


def _minimal_read_db(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
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
            INSERT INTO categories(id,name,name_key) VALUES('cat-1','Werkzeug','werkzeug');
            INSERT INTO entries(id,category_id,title,title_key)
            VALUES('ent-1','cat-1','Akkuschrauber','akkuschrauber');
            INSERT INTO field_definitions(
              id,scope,category_id,name,name_key,field_type,is_required
            ) VALUES('fld-1','category','cat-1','Hersteller','hersteller','text',1);
            """
        )
        con.commit()
    finally:
        con.close()


class ReadOnlyStartupTests(unittest.TestCase):
    def test_runtime_opens_database_read_only_and_validates_before_use(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "main.db"
            _minimal_read_db(db)
            calls: list[str] = []

            def guard(con, kind):
                calls.append(kind.value)
                self.assertEqual(con.execute("PRAGMA query_only").fetchone()[0], 1)

            with patch("provoware_db.web.startup.fast_validate", side_effect=guard):
                runtime = build_readonly_runtime(db)

            try:
                self.assertEqual(calls, ["main"])
                self.assertEqual(runtime.catalog.list_categories()[0].name, "Werkzeug")
                self.assertEqual(runtime.catalog.list_entries("cat-1")[0].title, "Akkuschrauber")
                self.assertEqual(runtime.catalog.list_fields("ent-1")[0].name, "Hersteller")
                with self.assertRaises(sqlite3.OperationalError):
                    runtime.connection.execute("CREATE TABLE forbidden(id INTEGER)")
            finally:
                runtime.close()

    def test_invalid_schema_blocks_server_before_serve(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "main.db"
            sqlite3.connect(db).close()
            served = False

            def fake_serve(*args, **kwargs):
                nonlocal served
                served = True

            with self.assertRaises(SchemaGuardError):
                run_local_readonly(db, serve_fn=fake_serve)

            self.assertFalse(served)

    def test_server_is_loopback_only_and_connection_closes_after_shutdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "main.db"
            _minimal_read_db(db)
            captured = {}

            def fake_serve(catalog, *, host, port):
                captured["catalog"] = catalog
                captured["connection"] = catalog.main_con
                captured["host"] = host
                captured["port"] = port

            with patch("provoware_db.web.startup.fast_validate"):
                run_local_readonly(db, port=8877, serve_fn=fake_serve)

            self.assertEqual(captured["host"], "127.0.0.1")
            self.assertEqual(captured["port"], 8877)
            with self.assertRaises(sqlite3.ProgrammingError):
                captured["connection"].execute("SELECT 1")


if __name__ == "__main__":
    unittest.main()
