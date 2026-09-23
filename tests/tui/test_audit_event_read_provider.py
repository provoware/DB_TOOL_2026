from __future__ import annotations

import sqlite3

from provoware_db.tui.event_provider import AuditEventReadProvider


def _connection() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.execute(
        "CREATE TABLE audit_events (id TEXT PRIMARY KEY, occurred_at TEXT NOT NULL, summary TEXT NOT NULL)"
    )
    return con


def test_projects_newest_events_with_neutral_symbol() -> None:
    con = _connection()
    con.executemany(
        "INSERT INTO audit_events(id, occurred_at, summary) VALUES(?,?,?)",
        [
            ("a", "2026-09-23T05:00:00.000Z", "Alt"),
            ("b", "2026-09-23T06:00:00.000Z", "Neu"),
        ],
    )
    provider = AuditEventReadProvider(con)

    events = provider.recent_events(limit=10)

    assert [(item.time_label, item.symbol, item.text) for item in events] == [
        ("2026-09-23T06:00:00.000Z", "·", "Neu"),
        ("2026-09-23T05:00:00.000Z", "·", "Alt"),
    ]


def test_limit_is_deterministic_and_hard_capped() -> None:
    con = _connection()
    con.executemany(
        "INSERT INTO audit_events(id, occurred_at, summary) VALUES(?,?,?)",
        [(f"id-{i:03d}", "2026-09-23T06:00:00.000Z", f"Ereignis {i}") for i in range(120)],
    )
    provider = AuditEventReadProvider(con)

    assert provider.recent_events(limit=0) == ()
    assert provider.recent_events(limit=-1) == ()
    events = provider.recent_events(limit=1000)
    assert len(events) == 100
    assert events[0].text == "Ereignis 119"


def test_provider_does_not_close_borrowed_connection() -> None:
    con = _connection()
    provider = AuditEventReadProvider(con)

    assert provider.recent_events() == ()
    assert con.execute("SELECT 1").fetchone() == (1,)
