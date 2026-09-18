from __future__ import annotations
import sqlite3
from provoware_db.domain.models import Category
from provoware_db.domain.errors import RevisionConflictError
from provoware_db.domain.normalization import clean_text, make_key

class CategoryRepository:
    def __init__(self, con: sqlite3.Connection) -> None: self.con = con
    def insert(self, category: Category) -> None:
        self.con.execute("INSERT INTO categories(id,name,name_key,description,sort_order) VALUES(?,?,?,?,?)",(category.id,category.name,category.name_key,category.description,category.sort_order))
    def _from_row(self,row): return None if row is None else Category(**dict(row))
    def get_active(self, category_id: str) -> Category | None:
        return self._from_row(self.con.execute("SELECT id,name,name_key,description,sort_order,revision FROM categories WHERE id=? AND deleted_at IS NULL",(category_id,)).fetchone())
    def get_any(self, category_id: str) -> sqlite3.Row | None:
        return self.con.execute("SELECT * FROM categories WHERE id=?",(category_id,)).fetchone()
    def find_active_by_name_key(self,name_key:str)->Category|None:
        return self._from_row(self.con.execute("SELECT id,name,name_key,description,sort_order,revision FROM categories WHERE name_key=? AND deleted_at IS NULL",(name_key,)).fetchone())
    def list_active(self)->list[Category]:
        return [self._from_row(r) for r in self.con.execute("SELECT id,name,name_key,description,sort_order,revision FROM categories WHERE deleted_at IS NULL ORDER BY sort_order,name_key,id").fetchall()]
    def update(self, category_id:str, *, name:str, description:str|None, sort_order:int, expected_revision:int)->Category:
        n=clean_text(name); key=make_key(n)
        cur=self.con.execute("UPDATE categories SET name=?,name_key=?,description=?,sort_order=?,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NULL AND revision=?",(n,key,description,sort_order,category_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-301: Kategorie wurde zwischenzeitlich geändert oder ist nicht mehr aktiv.")
        return self.get_active(category_id)
    def soft_delete(self,category_id:str,expected_revision:int)->None:
        cur=self.con.execute("UPDATE categories SET deleted_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NULL AND revision=?",(category_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-302: Kategorie konnte wegen Revisionskonflikt nicht gelöscht werden.")
    def restore(self,category_id:str,expected_revision:int)->Category:
        cur=self.con.execute("UPDATE categories SET deleted_at=NULL,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NOT NULL AND revision=?",(category_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-303: Kategorie konnte wegen Revisionskonflikt nicht wiederhergestellt werden.")
        return self.get_active(category_id)
    def search(self,q:str,limit:int=50)->list[sqlite3.Row]:
        like=f"%{make_key(q)}%"
        return self.con.execute("SELECT id,name,description FROM categories WHERE deleted_at IS NULL AND name_key LIKE ? ORDER BY sort_order,name_key LIMIT ?",(like,limit)).fetchall()
