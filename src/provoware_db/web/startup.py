from __future__ import annotations

import argparse
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from provoware_db.application.catalog_service import CatalogService
from provoware_db.storage.sqlite.connection import open_connection
from provoware_db.storage.sqlite.constants import DatabaseKind
from provoware_db.storage.sqlite.errors import SchemaGuardError
from provoware_db.storage.sqlite.repositories import (
    CategoryRepository,
    EntryRepository,
    FieldRepository,
)
from provoware_db.storage.sqlite.schema_guard import fast_validate

from .http_app import serve


ServeFn = Callable[..., None]


@dataclass
class ReadOnlyWebRuntime:
    catalog: CatalogService
    connection: sqlite3.Connection

    def close(self) -> None:
        self.connection.close()


def build_readonly_runtime(main_db: Path) -> ReadOnlyWebRuntime:
    """Open and validate main.db before exposing any web read path."""
    main_db = Path(main_db)
    if not main_db.is_file():
        raise FileNotFoundError(f"main.db wurde nicht gefunden: {main_db}")

    con = open_connection(main_db, read_only=True)
    try:
        con.execute("PRAGMA query_only = ON")
        fast_validate(con, DatabaseKind.MAIN)

        catalog = CatalogService.__new__(CatalogService)
        catalog.main_con = con
        catalog.app_version = "0.4.0"
        catalog.categories = CategoryRepository(con)
        catalog.entries = EntryRepository(con)
        catalog.fields = FieldRepository(con)
        return ReadOnlyWebRuntime(catalog=catalog, connection=con)
    except Exception:
        con.close()
        raise


def run_local_readonly(
    main_db: Path,
    *,
    port: int = 8765,
    serve_fn: ServeFn = serve,
) -> None:
    """Validate, start on loopback only, and always close the database."""
    if not 1 <= port <= 65535:
        raise ValueError("Port muss zwischen 1 und 65535 liegen.")

    runtime = build_readonly_runtime(main_db)
    try:
        serve_fn(runtime.catalog, host="127.0.0.1", port=port)
    finally:
        runtime.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PROVOWARE DB TOOL 2026 – lokaler Nur-Lese-Webstart"
    )
    parser.add_argument(
        "--main-db",
        type=Path,
        required=True,
        help="Pfad zur bestehenden main.db",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Lokaler Port, Standard 8765",
    )
    args = parser.parse_args(argv)

    print("PROVOWARE DB TOOL 2026")
    print("Modus: NUR LESEN")
    print(f"Datenbank: {args.main_db}")
    print(f"Lokale Adresse: http://127.0.0.1:{args.port}")
    print("Vor dem Start werden Datenbankidentität und Schema geprüft.")

    try:
        run_local_readonly(args.main_db, port=args.port)
    except KeyboardInterrupt:
        print("\nServer beendet.")
        return 0
    except (FileNotFoundError, SchemaGuardError, sqlite3.Error, ValueError) as exc:
        print(f"START BLOCKIERT: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
