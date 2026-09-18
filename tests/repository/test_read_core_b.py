import sqlite3
from provoware_db.domain.models import FieldDefinition, FieldOption, FieldScope, FieldType
from provoware_db.storage.sqlite.repositories.field_repository import FieldRepository


def connection():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE field_definitions(
      id TEXT PRIMARY KEY, scope TEXT NOT NULL, category_id TEXT, entry_id TEXT,
      name TEXT NOT NULL, name_key TEXT NOT NULL, field_type TEXT NOT NULL,
      is_required INTEGER NOT NULL DEFAULT 0, sort_order INTEGER NOT NULL DEFAULT 0,
      help_text TEXT, placeholder TEXT, unit_label TEXT, currency_code TEXT,
      created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', deleted_at TEXT,
      revision INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE field_options(
      id TEXT PRIMARY KEY, field_definition_id TEXT NOT NULL, label TEXT NOT NULL,
      option_key TEXT NOT NULL, sort_order INTEGER NOT NULL DEFAULT 0,
      created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', deleted_at TEXT
    );
    CREATE TABLE scalar_field_values(
      entry_id TEXT, field_definition_id TEXT, value_kind TEXT,
      value_text TEXT, value_integer INTEGER, value_real REAL,
      created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', revision INTEGER NOT NULL DEFAULT 1,
      PRIMARY KEY(entry_id, field_definition_id)
    );
    CREATE TABLE single_choice_values(
      entry_id TEXT, field_definition_id TEXT, option_id TEXT,
      created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', revision INTEGER NOT NULL DEFAULT 1,
      PRIMARY KEY(entry_id, field_definition_id)
    );
    CREATE TABLE multi_choice_values(
      entry_id TEXT, field_definition_id TEXT, option_id TEXT,
      created_at TEXT DEFAULT '', PRIMARY KEY(entry_id, field_definition_id, option_id)
    );
    CREATE TABLE categories(id TEXT PRIMARY KEY, deleted_at TEXT);
    CREATE TABLE entries(id TEXT PRIMARY KEY, category_id TEXT, deleted_at TEXT);
    """)
    return con


def test_field_repository_lists_category_and_entry_fields_for_entry():
    con = connection()
    repo = FieldRepository(con)
    repo.insert_definition(FieldDefinition.new(
        id="fld-cat", scope=FieldScope.CATEGORY, category_id="cat-1",
        name="Hersteller", field_type=FieldType.TEXT, sort_order=1,
    ))
    repo.insert_definition(FieldDefinition.new(
        id="fld-ent", scope=FieldScope.ENTRY, entry_id="ent-1",
        name="Seriennummer", field_type=FieldType.TEXT, sort_order=2,
    ))
    fields = repo.list_visible_for_entry("ent-1", "cat-1")
    assert [f.id for f in fields] == ["fld-cat", "fld-ent"]
    assert [f.name for f in fields] == ["Hersteller", "Seriennummer"]
    con.close()


def test_field_repository_read_option_path():
    con = connection()
    repo = FieldRepository(con)
    field = FieldDefinition.new(
        id="fld-1", scope=FieldScope.ENTRY, entry_id="ent-1",
        name="Zustand", field_type=FieldType.SINGLE_CHOICE,
    )
    repo.insert_definition(field)
    option = FieldOption.new("opt-1", field.id, "Gut")
    repo.insert_option(option)
    assert repo.get_active_option("opt-1").label == "Gut"
    assert [x.label for x in repo.list_active_options(field.id)] == ["Gut"]
    con.close()
