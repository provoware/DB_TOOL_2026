import sqlite3
from provoware_db.domain.models import Category, Entry
from provoware_db.storage.sqlite.repositories.category_repository import CategoryRepository
from provoware_db.storage.sqlite.repositories.entry_repository import EntryRepository


def connection():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE categories(
      id TEXT PRIMARY KEY, name TEXT NOT NULL, name_key TEXT NOT NULL,
      description TEXT, sort_order INTEGER NOT NULL DEFAULT 0,
      created_at TEXT DEFAULT '', updated_at TEXT DEFAULT '', deleted_at TEXT,
      revision INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE entries(
      id TEXT PRIMARY KEY, category_id TEXT NOT NULL, title TEXT NOT NULL,
      title_key TEXT NOT NULL, is_favorite INTEGER NOT NULL DEFAULT 0,
      sort_order INTEGER NOT NULL DEFAULT 0, created_at TEXT DEFAULT '',
      updated_at TEXT DEFAULT '', deleted_at TEXT, revision INTEGER NOT NULL DEFAULT 1
    );
    """)
    return con


def test_category_repository_read_path():
    con = connection()
    repo = CategoryRepository(con)
    repo.insert(Category.new("cat-1", "Werkzeug"))
    repo.insert(Category.new("cat-2", "Fahrzeuge", sort_order=2))
    assert [x.name for x in repo.list_active()] == ["Werkzeug", "Fahrzeuge"]
    assert repo.get_active("cat-1").revision == 1
    assert repo.find_active_by_name_key("werkzeug").id == "cat-1"
    con.close()


def test_entry_repository_read_path_and_hidden_deleted_category():
    con = connection()
    categories = CategoryRepository(con)
    entries = EntryRepository(con)
    categories.insert(Category.new("cat-1", "Werkzeug"))
    entries.insert(Entry.new("ent-1", "cat-1", "Akkuschrauber"))
    assert [x.title for x in entries.list_active_by_category("cat-1")] == ["Akkuschrauber"]
    assert entries.get_active("ent-1").category_id == "cat-1"
    assert [r["title"] for r in entries.search("akku")] == ["Akkuschrauber"]
    con.execute("UPDATE categories SET deleted_at='x' WHERE id='cat-1'")
    assert entries.search("akku") == []
    con.close()
