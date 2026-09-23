from __future__ import annotations

import sqlite3

from .view_models import EventItem


_MAX_EVENTS = 100
_NEUTRAL_SYMBOL = "·"


class AuditEventReadProvider:
    """Read-only EventItem projection over a borrowed SQLite connection."""

    def __init__(self, con: sqlite3.Connection) -> None:
        self._con = con

    def recent_events(self, limit: int = 10) -> tuple[EventItem, ...]:
        if limit <= 0:
            return ()
        bounded_limit = min(limit, _MAX_EVENTS)
        rows = self._con.execute(
            "SELECT occurred_at, summary FROM audit_events "
            "ORDER BY occurred_at DESC, id DESC LIMIT ?",
            (bounded_limit,),
        ).fetchall()
        return tuple(
            EventItem(time_label=str(occurred_at), symbol=_NEUTRAL_SYMBOL, text=str(summary))
            for occurred_at, summary in rows
        )
