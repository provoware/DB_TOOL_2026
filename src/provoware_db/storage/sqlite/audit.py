from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, is_dataclass
from typing import Any
from uuid import uuid4


def _json_payload(value: Any) -> str | None:
    if value is None:
        return None
    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


class AuditWriter:
    def __init__(self, con: sqlite3.Connection, *, app_version: str, schema_version: int = 1) -> None:
        self.con = con
        self.app_version = app_version
        self.schema_version = schema_version

    def record(
        self,
        *,
        operation_id: str,
        action: str,
        entity_type: str,
        entity_id: str | None,
        summary: str,
        before: Any = None,
        after: Any = None,
        category_id: str | None = None,
        entry_id: str | None = None,
        actor_kind: str = "user",
        is_undoable: bool = True,
    ) -> str:
        audit_id = f"aud_{uuid4().hex}"
        self.con.execute(
            "INSERT INTO audit_events("
            "id,operation_id,actor_kind,action,entity_type,entity_id,category_id,entry_id,summary,"
            "before_json,after_json,is_undoable,app_version,schema_version"
            ") VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                audit_id, operation_id, actor_kind, action, entity_type, entity_id,
                category_id, entry_id, summary, _json_payload(before), _json_payload(after),
                int(is_undoable), self.app_version, self.schema_version,
            ),
        )
        return audit_id

    def exists_for_operation(self, operation_id: str) -> bool:
        return self.con.execute(
            "SELECT 1 FROM audit_events WHERE operation_id=? LIMIT 1", (operation_id,)
        ).fetchone() is not None
