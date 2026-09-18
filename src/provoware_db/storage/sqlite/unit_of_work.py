from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass
class SQLiteUnitOfWork:
    con: sqlite3.Connection
    _finished: bool = False

    def __enter__(self) -> "SQLiteUnitOfWork":
        if self.con.in_transaction:
            raise RuntimeError("TX-001: Verschachtelte Unit-of-Work ist nicht erlaubt.")
        self.con.execute("BEGIN IMMEDIATE")
        return self

    def commit(self) -> None:
        if self._finished:
            raise RuntimeError("TX-002: Unit-of-Work wurde bereits abgeschlossen.")
        self.con.commit()
        self._finished = True

    def rollback(self) -> None:
        if not self._finished and self.con.in_transaction:
            self.con.rollback()
        self._finished = True

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None:
            self.rollback()
            return False
        if not self._finished:
            self.rollback()
        return False
