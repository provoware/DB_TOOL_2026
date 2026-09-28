from __future__ import annotations

import sqlite3

from provoware_db.storage.sqlite.repositories.field_repository import FieldRepository


def _connection() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript(
        """
        CREATE TABLE categories(
          id TEXT PRIMARY KEY, name TEXT NOT NULL, deleted_at TEXT
        );
        CREATE TABLE entries(
          id TEXT PRIMARY KEY, category_id TEXT NOT NULL, title TEXT NOT NULL, deleted_at TEXT
        );
        CREATE TABLE field_definitions(
          id TEXT PRIMARY KEY, scope TEXT NOT NULL, category_id TEXT, entry_id TEXT,
          name TEXT NOT NULL, field_type TEXT NOT NULL, deleted_at TEXT
        );
        CREATE TABLE scalar_field_values(
          entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL,
          value_kind TEXT NOT NULL, value_text TEXT, value_integer INTEGER, value_real REAL
        );
        CREATE TABLE field_options(
          id TEXT PRIMARY KEY, field_definition_id TEXT NOT NULL,
          label TEXT NOT NULL, option_key TEXT NOT NULL,
          sort_order INTEGER NOT NULL DEFAULT 0, deleted_at TEXT
        );
        CREATE TABLE single_choice_values(
          entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL, option_id TEXT NOT NULL
        );
        CREATE TABLE multi_choice_values(
          entry_id TEXT NOT NULL, field_definition_id TEXT NOT NULL, option_id TEXT NOT NULL
        );
        """
    )
    return con


def _seed(con: sqlite3.Connection) -> None:
    con.execute("INSERT INTO categories VALUES('cat-1','Werkzeug',NULL)")
    con.execute("INSERT INTO categories VALUES('cat-dead','Alt','2026-09-28')")
    con.execute("INSERT INTO entries VALUES('ent-1','cat-1','Akkuschrauber',NULL)")
    con.execute("INSERT INTO entries VALUES('ent-dead','cat-dead','Altgerät',NULL)")

    con.execute("INSERT INTO field_definitions VALUES('fld-text','category','cat-1',NULL,'Notiz','text',NULL)")
    con.execute("INSERT INTO field_definitions VALUES('fld-single','category','cat-1',NULL,'Hersteller','single_choice',NULL)")
    con.execute("INSERT INTO field_definitions VALUES('fld-multi','entry',NULL,'ent-1','Merkmale','multi_choice',NULL)")
    con.execute("INSERT INTO field_definitions VALUES('fld-dead','category','cat-dead',NULL,'Altwert','text',NULL)")

    con.execute("INSERT INTO scalar_field_values VALUES('ent-1','fld-text','text','Robustes Profigerät',NULL,NULL)")
    con.execute("INSERT INTO scalar_field_values VALUES('ent-dead','fld-dead','text','Geheimer Treffer',NULL,NULL)")

    con.execute("INSERT INTO field_options VALUES('opt-bosch','fld-single','Bosch','bosch',0,NULL)")
    con.execute("INSERT INTO single_choice_values VALUES('ent-1','fld-single','opt-bosch')")

    con.execute("INSERT INTO field_options VALUES('opt-akku','fld-multi','Akku','akku',0,NULL)")
    con.execute("INSERT INTO field_options VALUES('opt-akku2','fld-multi','Akku-System','akku-system',1,NULL)")
    con.execute("INSERT INTO multi_choice_values VALUES('ent-1','fld-multi','opt-akku')")
    con.execute("INSERT INTO multi_choice_values VALUES('ent-1','fld-multi','opt-akku2')")


def test_i157_lab_finds_text_and_choice_values_without_writes() -> None:
    con = _connection()
    try:
        _seed(con)
        repo = FieldRepository(con)
        changes_before = con.total_changes

        text_hits = repo.search_value_lab("profi")
        assert len(text_hits) == 1
        assert text_hits[0]["category_id"] == "cat-1"
        assert text_hits[0]["entry_id"] == "ent-1"
        assert text_hits[0]["field_id"] == "fld-text"
        assert text_hits[0]["value_preview"] == "Robustes Profigerät"
        assert text_hits[0]["source_kind"] == "scalar_text"

        single_hits = repo.search_value_lab("bosch")
        assert len(single_hits) == 1
        assert single_hits[0]["field_id"] == "fld-single"
        assert single_hits[0]["source_kind"] == "single_choice"

        multi_hits = repo.search_value_lab("akku")
        assert len(multi_hits) == 1
        assert multi_hits[0]["field_id"] == "fld-multi"
        assert multi_hits[0]["value_preview"] == "Akku, Akku-System"

        assert con.total_changes == changes_before
    finally:
        con.close()


def test_i157_lab_excludes_deleted_parents_and_obeys_limit() -> None:
    con = _connection()
    try:
        _seed(con)
        repo = FieldRepository(con)

        assert repo.search_value_lab("geheim") == []
        assert repo.search_value_lab("akku", limit=0) == []
        assert len(repo.search_value_lab("a", limit=1)) == 1
    finally:
        con.close()
