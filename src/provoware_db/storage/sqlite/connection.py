from __future__ import annotations

import sqlite3
from pathlib import Path


def open_connection(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    path = Path(path)
    if read_only:
        uri = f"file:{path.resolve()}?mode=ro"
        con = sqlite3.connect(uri, uri=True, isolation_level=None, timeout=5.0)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path, isolation_level=None, timeout=5.0)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA busy_timeout = 5000")
    return con
