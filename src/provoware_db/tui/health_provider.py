from __future__ import annotations

import sqlite3

from provoware_db.storage.sqlite.constants import DatabaseKind
from provoware_db.storage.sqlite.schema_guard import assert_schema_identity
from provoware_db.tui.view_models import HealthItem, HealthLevel


class DatabaseReadinessHealthProvider:
    """Project the authorized read-only database readiness contract to TUI health."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def health(self) -> tuple[HealthItem, ...]:
        try:
            self._connection.execute("SELECT 1").fetchone()
            assert_schema_identity(self._connection, DatabaseKind.MAIN)
        except (sqlite3.Error, RuntimeError):
            return (
                HealthItem(
                    "Datenbank",
                    HealthLevel.ERROR,
                    "Nicht lesebereit oder nicht kompatibel.",
                ),
            )
        return (
            HealthItem(
                "Datenbank",
                HealthLevel.OK,
                "Lesebereit und kompatibel.",
            ),
        )
