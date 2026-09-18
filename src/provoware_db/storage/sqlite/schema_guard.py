from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass

from .constants import APPLICATION_IDS, EXPECTED_TABLES, SCHEMA_VERSION, DatabaseKind
from .errors import SchemaGuardError
from .schema_manifest import EXPECTED_SCHEMA_FINGERPRINTS


@dataclass(frozen=True)
class SchemaStatus:
    kind: DatabaseKind
    user_version: int
    application_id: int
    quick_check: str
    foreign_key_violations: int
    schema_fingerprint: str


def _user_tables(con: sqlite3.Connection) -> set[str]:
    return {
        row[0] for row in con.execute(
            "SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }


def schema_fingerprint(con: sqlite3.Connection) -> str:
    rows = con.execute(
        "SELECT type,name,tbl_name,sql FROM sqlite_schema "
        "WHERE name NOT LIKE 'sqlite_%' AND sql IS NOT NULL ORDER BY type,name"
    ).fetchall()
    normalized = []
    for row in rows:
        sql = " ".join(str(row[3]).split())
        normalized.append("|".join((str(row[0]), str(row[1]), str(row[2]), sql)))
    return hashlib.sha256("\n".join(normalized).encode("utf-8")).hexdigest()


def assert_schema_identity(con: sqlite3.Connection, kind: DatabaseKind) -> None:
    user_version = int(con.execute("PRAGMA user_version").fetchone()[0])
    app_id = int(con.execute("PRAGMA application_id").fetchone()[0])
    if user_version != SCHEMA_VERSION:
        raise SchemaGuardError(f"DB-201: Schema-Version {user_version}, erwartet {SCHEMA_VERSION}.")
    if app_id != APPLICATION_IDS[kind]:
        raise SchemaGuardError(f"DB-202: Falsche Datenbankidentität für {kind.value}.")
    actual = _user_tables(con)
    expected = EXPECTED_TABLES[kind]
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        raise SchemaGuardError(f"DB-203: Tabellenabweichung missing={missing}, unexpected={unexpected}")
    fingerprint = schema_fingerprint(con)
    if fingerprint != EXPECTED_SCHEMA_FINGERPRINTS[kind]:
        raise SchemaGuardError(
            f"DB-208: Schema-Fingerprint abweichend für {kind.value}: {fingerprint[:12]}…"
        )


def fast_validate(con: sqlite3.Connection, kind: DatabaseKind) -> SchemaStatus:
    assert_schema_identity(con, kind)
    fk_enabled = int(con.execute("PRAGMA foreign_keys").fetchone()[0])
    if fk_enabled != 1:
        raise SchemaGuardError("DB-204: Fremdschlüsselprüfung ist deaktiviert.")
    quick = str(con.execute("PRAGMA quick_check").fetchone()[0])
    if quick != "ok":
        raise SchemaGuardError(f"DB-205: quick_check fehlgeschlagen: {quick}")
    fk = list(con.execute("PRAGMA foreign_key_check"))
    if fk:
        raise SchemaGuardError(f"DB-206: {len(fk)} Fremdschlüsselverletzung(en).")
    return SchemaStatus(
        kind,
        int(con.execute("PRAGMA user_version").fetchone()[0]),
        int(con.execute("PRAGMA application_id").fetchone()[0]),
        quick, 0, schema_fingerprint(con),
    )


def deep_validate(con: sqlite3.Connection, kind: DatabaseKind) -> SchemaStatus:
    assert_schema_identity(con, kind)
    integrity = [row[0] for row in con.execute("PRAGMA integrity_check")]
    if integrity != ["ok"]:
        raise SchemaGuardError(f"DB-207: integrity_check fehlgeschlagen: {integrity[:3]}")
    fk = list(con.execute("PRAGMA foreign_key_check"))
    if fk:
        raise SchemaGuardError(f"DB-206: {len(fk)} Fremdschlüsselverletzung(en).")
    return SchemaStatus(
        kind,
        int(con.execute("PRAGMA user_version").fetchone()[0]),
        int(con.execute("PRAGMA application_id").fetchone()[0]),
        "ok", 0, schema_fingerprint(con),
    )
