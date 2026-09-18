from __future__ import annotations

import hashlib
import signal
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path

from provoware_db.storage.sqlite.constants import APPLICATION_IDS, DatabaseKind
from provoware_db.storage.sqlite.schema_guard import fast_validate
from provoware_db.web.startup import build_readonly_runtime


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/cp03_main_schema_v1.sql"
EXPECTED_FIXTURE_SHA256 = "4119f49eef696cb7bafaed5bf4147c03e8340848381946adaed77227c76c81f6"
EXPECTED_SCHEMA_FINGERPRINT = "3376adc9284f6668d86bd20a673938227ab2c95c22d0810f0186c708ef162d48"


def _create_cp03_db(path: Path) -> None:
    schema_bytes = FIXTURE.read_bytes()
    assert hashlib.sha256(schema_bytes).hexdigest() == EXPECTED_FIXTURE_SHA256
    con = sqlite3.connect(path)
    try:
        con.executescript(schema_bytes.decode("utf-8"))
        con.execute(f"PRAGMA application_id = {APPLICATION_IDS[DatabaseKind.MAIN]}")
        con.execute(
            "INSERT INTO schema_migrations(version,name,checksum,app_version) VALUES(?,?,?,?)",
            (1, "CP03_main_schema", EXPECTED_FIXTURE_SHA256, "0.4.0"),
        )
        con.execute(
            "INSERT INTO categories(id,name,name_key,description,sort_order) VALUES(?,?,?,?,?)",
            ("cat-tool", "Werkzeug", "werkzeug", "Deterministische Testkategorie", 0),
        )
        con.execute(
            "INSERT INTO entries(id,category_id,title,title_key,is_favorite,sort_order) VALUES(?,?,?,?,?,?)",
            ("ent-drill", "cat-tool", "Akkuschrauber", "akkuschrauber", 1, 0),
        )
        fields = (
            ("fld-maker", "category", "cat-tool", None, "Hersteller", "hersteller", "text", 1, 0, "Name des Herstellers", "z. B. Bosch"),
            ("fld-state", "category", "cat-tool", None, "Zustand", "zustand", "single_choice", 0, 1, "Aktueller Zustand", None),
            ("fld-date", "entry", None, "ent-drill", "Kaufdatum", "kaufdatum", "date", 0, 2, "Datum des Kaufs", "YYYY-MM-DD"),
        )
        for field in fields:
            con.execute(
                """
                INSERT INTO field_definitions(
                  id,scope,category_id,entry_id,name,name_key,field_type,is_required,
                  sort_order,help_text,placeholder,unit_label,currency_code,validation_json
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (*field, None, None, None),
            )
        con.execute(
            "INSERT INTO field_options(id,field_definition_id,label,option_key,sort_order) VALUES(?,?,?,?,?)",
            ("opt-good", "fld-state", "Gut", "gut", 0),
        )
        con.commit()
    finally:
        con.close()


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class CP03PositiveSmokeTests(unittest.TestCase):
    def test_real_fast_validate_and_readonly_runtime_succeed_without_mock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "main.db"
            _create_cp03_db(db)
            runtime = build_readonly_runtime(db)
            try:
                status = fast_validate(runtime.connection, DatabaseKind.MAIN)
                self.assertEqual(status.schema_fingerprint, EXPECTED_SCHEMA_FINGERPRINT)
                self.assertEqual(status.user_version, 1)
                self.assertEqual(status.application_id, APPLICATION_IDS[DatabaseKind.MAIN])
                self.assertEqual(runtime.catalog.list_categories()[0].name, "Werkzeug")
                self.assertEqual(runtime.catalog.list_entries("cat-tool")[0].title, "Akkuschrauber")
                self.assertEqual(
                    [field.name for field in runtime.catalog.list_fields("ent-drill")],
                    ["Hersteller", "Zustand", "Kaufdatum"],
                )
            finally:
                runtime.close()

    def test_real_cli_starts_fixture_and_serves_readonly_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "main.db"
            _create_cp03_db(db)
            port = _free_port()
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "scripts/start_readonly_web.py"),
                    "--main-db",
                    str(db),
                    "--port",
                    str(port),
                ],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                body = None
                deadline = time.monotonic() + 8.0
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        break
                    try:
                        with urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/?category_id=cat-tool&entry_id=ent-drill",
                            timeout=0.4,
                        ) as response:
                            body = response.read().decode("utf-8")
                            self.assertEqual(response.status, 200)
                            break
                    except OSError:
                        time.sleep(0.1)

                self.assertIsNotNone(body, "CLI-Server wurde nicht rechtzeitig erreichbar.")
                self.assertIn("Werkzeug", body)
                self.assertIn("Akkuschrauber", body)
                self.assertIn("Hersteller", body)
            finally:
                if process.poll() is None:
                    process.send_signal(signal.SIGINT)
                stdout, stderr = process.communicate(timeout=5)

            self.assertEqual(process.returncode, 0, stderr)
            self.assertIn("Modus: NUR LESEN", stdout)
            self.assertIn(f"http://127.0.0.1:{port}", stdout)


if __name__ == "__main__":
    unittest.main()
