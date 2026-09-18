from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from .constants import DatabaseKind
from .schema_guard import assert_schema_identity


@dataclass(frozen=True)
class JournalRecord:
    operation_id: str
    state: str
    operation_type: str
    entity_type: str | None
    entity_id: str | None
    error_code: str | None
    recovery_action: str | None


class OperationJournal:
    def __init__(self, con: sqlite3.Connection, *, app_session_id: str, app_version: str) -> None:
        assert_schema_identity(con, DatabaseKind.STATE)
        self.con = con
        self.app_session_id = app_session_id
        self.app_version = app_version
        self.ensure_session()

    def ensure_session(self) -> None:
        self.con.execute(
            "INSERT INTO app_sessions(id,app_version,pid) VALUES(?,?,NULL) "
            "ON CONFLICT(id) DO UPDATE SET last_heartbeat_at=(strftime('%Y-%m-%dT%H:%M:%fZ','now'))",
            (self.app_session_id, self.app_version),
        )

    def start(self, operation_id: str, operation_type: str, entity_type: str | None, entity_id: str | None) -> None:
        self.con.execute(
            "INSERT INTO operation_journal(operation_id,app_session_id,operation_type,entity_type,entity_id,state) "
            "VALUES(?,?,?,?,?,'started')",
            (operation_id, self.app_session_id, operation_type, entity_type, entity_id),
        )

    def mark_committed(self, operation_id: str) -> None:
        self._finish(operation_id, "committed")

    def mark_rolled_back(self, operation_id: str, *, error_code: str | None = None) -> None:
        self._finish(operation_id, "rolled_back", error_code=error_code)

    def mark_failed(self, operation_id: str, *, error_code: str | None = None) -> None:
        self._finish(operation_id, "failed", error_code=error_code)

    def mark_recovered(self, operation_id: str, recovery_action: str) -> None:
        self._finish(operation_id, "recovered", recovery_action=recovery_action)

    def _finish(
        self,
        operation_id: str,
        state: str,
        *,
        error_code: str | None = None,
        recovery_action: str | None = None,
    ) -> None:
        cur = self.con.execute(
            "UPDATE operation_journal SET state=?,completed_at=(strftime('%Y-%m-%dT%H:%M:%fZ','now'))," 
            "error_code=COALESCE(?,error_code),recovery_action=COALESCE(?,recovery_action) "
            "WHERE operation_id=? AND state='started'",
            (state, error_code, recovery_action, operation_id),
        )
        if cur.rowcount != 1:
            raise RuntimeError(f"REC-510: Operation {operation_id} ist nicht mehr im Zustand started.")

    def get(self, operation_id: str) -> JournalRecord | None:
        row = self.con.execute(
            "SELECT operation_id,state,operation_type,entity_type,entity_id,error_code,recovery_action "
            "FROM operation_journal WHERE operation_id=?",
            (operation_id,),
        ).fetchone()
        return None if row is None else JournalRecord(**dict(row))

    def list_started(self) -> list[JournalRecord]:
        rows = self.con.execute(
            "SELECT operation_id,state,operation_type,entity_type,entity_id,error_code,recovery_action "
            "FROM operation_journal WHERE state='started' ORDER BY started_at,operation_id"
        ).fetchall()
        return [JournalRecord(**dict(row)) for row in rows]
