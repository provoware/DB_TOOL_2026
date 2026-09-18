from __future__ import annotations
import sqlite3
from provoware_db.domain.models import Entry
from provoware_db.domain.errors import RevisionConflictError
from provoware_db.domain.normalization import clean_text, make_key

class EntryRepository:
    def __init__(self, con: sqlite3.Connection)->None: self.con=con
    def insert(self,entry:Entry)->None:
        self.con.execute("INSERT INTO entries(id,category_id,title,title_key,is_favorite,sort_order) VALUES(?,?,?,?,?,?)",(entry.id,entry.category_id,entry.title,entry.title_key,int(entry.is_favorite),entry.sort_order))
    def _from_row(self,row):
        if row is None:return None
        d=dict(row);d['is_favorite']=bool(d['is_favorite']);return Entry(**d)
    def get_active(self,entry_id:str)->Entry|None:
        return self._from_row(self.con.execute("SELECT id,category_id,title,title_key,is_favorite,sort_order,revision FROM entries WHERE id=? AND deleted_at IS NULL",(entry_id,)).fetchone())
    def get_any(self,entry_id:str): return self.con.execute("SELECT * FROM entries WHERE id=?",(entry_id,)).fetchone()
    def list_active_by_category(self,category_id:str)->list[Entry]:
        return [self._from_row(r) for r in self.con.execute("SELECT id,category_id,title,title_key,is_favorite,sort_order,revision FROM entries WHERE category_id=? AND deleted_at IS NULL ORDER BY sort_order,title_key,id",(category_id,)).fetchall()]
    def update(self,entry_id:str,*,title:str,is_favorite:bool,sort_order:int,expected_revision:int)->Entry:
        t=clean_text(title);key=make_key(t)
        cur=self.con.execute("UPDATE entries SET title=?,title_key=?,is_favorite=?,sort_order=?,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NULL AND revision=?",(t,key,int(is_favorite),sort_order,entry_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-311: Eintrag wurde zwischenzeitlich geändert oder ist nicht mehr aktiv.")
        return self.get_active(entry_id)
    def soft_delete(self,entry_id:str,expected_revision:int)->None:
        cur=self.con.execute("UPDATE entries SET deleted_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NULL AND revision=?",(entry_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-312: Eintrag konnte wegen Revisionskonflikt nicht gelöscht werden.")
    def restore(self,entry_id:str,expected_revision:int)->Entry:
        cur=self.con.execute("UPDATE entries SET deleted_at=NULL,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NOT NULL AND revision=?",(entry_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-313: Eintrag konnte wegen Revisionskonflikt nicht wiederhergestellt werden.")
        return self.get_active(entry_id)
    def search(self,q:str,limit:int=50):
        like=f"%{make_key(q)}%"
        return self.con.execute("SELECT e.id,e.category_id,e.title FROM entries e JOIN categories c ON c.id=e.category_id WHERE e.deleted_at IS NULL AND c.deleted_at IS NULL AND e.title_key LIKE ? ORDER BY e.title_key,e.id LIMIT ?",(like,limit)).fetchall()
