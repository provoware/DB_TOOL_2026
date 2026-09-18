from __future__ import annotations

import os
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, TypeVar

from provoware_db.storage.sqlite.constants import DatabaseKind, SCHEMA_VERSION
from provoware_db.storage.sqlite.errors import (
    PostCommitValidationError, PostValidationError, PreValidationError,
)
from provoware_db.storage.sqlite.schema_guard import assert_schema_identity
from provoware_db.storage.sqlite.unit_of_work import SQLiteUnitOfWork

T = TypeVar("T")
Check = Callable[[sqlite3.Connection], bool]


@dataclass(frozen=True)
class GatePolicy:
    minimum_free_bytes: int = 8 * 1024 * 1024


def pre_write_gate(con: sqlite3.Connection, db_path: Path, *, policy: GatePolicy = GatePolicy()) -> None:
    assert_schema_identity(con, DatabaseKind.MAIN)
    if con.in_transaction:
        raise PreValidationError("VAL-301: Schreibvorgang startete in einer offenen Transaktion.")
    if int(con.execute("PRAGMA foreign_keys").fetchone()[0]) != 1:
        raise PreValidationError("VAL-302: Fremdschlüsselprüfung deaktiviert.")
    if int(con.execute("PRAGMA query_only").fetchone()[0]) != 0:
        raise PreValidationError("VAL-303: Datenbank ist im Nur-Lesen-Modus.")
    if int(con.execute("PRAGMA user_version").fetchone()[0]) != SCHEMA_VERSION:
        raise PreValidationError("VAL-304: Unerwartete Schema-Version.")
    parent = db_path.resolve().parent
    if not os.access(parent, os.W_OK):
        raise PreValidationError("SYS-301: Datenbankordner ist nicht beschreibbar.")
    if shutil.disk_usage(parent).free < policy.minimum_free_bytes:
        raise PreValidationError("SYS-302: Zu wenig freier Speicher für sicheren Schreibvorgang.")
    con.execute("SELECT 1").fetchone()


def _run_checks(con: sqlite3.Connection, checks: Iterable[Check], error_type: type[Exception], code: str) -> None:
    for index, check in enumerate(checks, start=1):
        try:
            ok = bool(check(con))
        except Exception as exc:
            raise error_type(f"{code}: Prüfschritt {index} war nicht ausführbar: {exc}") from exc
        if not ok:
            raise error_type(f"{code}: Prüfschritt {index} meldet Abweichung.")


def execute_validated_write(
    con: sqlite3.Connection,
    db_path: Path,
    action: Callable[[sqlite3.Connection], T],
    *,
    preconditions: Iterable[Check] = (),
    transactional_postconditions: Iterable[Check] = (),
    committed_postconditions: Iterable[Check] = (),
    policy: GatePolicy = GatePolicy(),
) -> T:
    pre_write_gate(con, db_path, policy=policy)
    _run_checks(con, preconditions, PreValidationError, "VAL-310")
    with SQLiteUnitOfWork(con) as uow:
        result = action(con)
        _run_checks(con, transactional_postconditions, PostValidationError, "VAL-320")
        uow.commit()
    try:
        _run_checks(con, committed_postconditions, PostCommitValidationError, "VAL-330")
    except PostCommitValidationError:
        # Committed data is never silently reversed here; caller must escalate/safe-mode.
        raise
    return result
