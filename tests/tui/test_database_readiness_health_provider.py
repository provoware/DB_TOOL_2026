from __future__ import annotations

import sqlite3

import provoware_db.tui.health_provider as health_provider
from provoware_db.storage.sqlite.errors import SchemaGuardError
from provoware_db.tui.health_provider import DatabaseReadinessHealthProvider
from provoware_db.tui.view_models import HealthLevel


class _Cursor:
    def fetchone(self) -> tuple[int]:
        return (1,)


class _Connection:
    def __init__(self, *, select_error: Exception | None = None) -> None:
        self.select_error = select_error
        self.executed: list[str] = []

    def execute(self, sql: str) -> _Cursor:
        self.executed.append(sql)
        if self.select_error is not None:
            raise self.select_error
        return _Cursor()


def test_ready_database_projects_ok(monkeypatch) -> None:
    connection = _Connection()
    seen: list[object] = []
    monkeypatch.setattr(
        health_provider,
        "assert_schema_identity",
        lambda con, kind: seen.append((con, kind)),
    )

    items = DatabaseReadinessHealthProvider(connection).health()

    assert connection.executed == ["SELECT 1"]
    assert seen == [(connection, health_provider.DatabaseKind.MAIN)]
    assert len(items) == 1
    assert items[0].level is HealthLevel.OK


def test_unreadable_database_projects_error(monkeypatch) -> None:
    connection = _Connection(select_error=sqlite3.OperationalError("unreadable"))
    called = False

    def _unexpected_schema_check(con, kind) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(health_provider, "assert_schema_identity", _unexpected_schema_check)

    items = DatabaseReadinessHealthProvider(connection).health()

    assert items[0].level is HealthLevel.ERROR
    assert called is False


def test_incompatible_schema_projects_error(monkeypatch) -> None:
    connection = _Connection()

    def _fail_schema(con, kind) -> None:
        raise SchemaGuardError("schema mismatch")

    monkeypatch.setattr(health_provider, "assert_schema_identity", _fail_schema)

    items = DatabaseReadinessHealthProvider(connection).health()

    assert items[0].level is HealthLevel.ERROR
    assert HealthLevel.WARNING not in {item.level for item in items}


def test_provider_does_not_close_borrowed_connection(monkeypatch) -> None:
    connection = _Connection()
    monkeypatch.setattr(health_provider, "assert_schema_identity", lambda con, kind: None)

    DatabaseReadinessHealthProvider(connection).health()

    assert not hasattr(connection, "close")
