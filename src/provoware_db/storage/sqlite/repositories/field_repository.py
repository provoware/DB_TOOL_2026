from __future__ import annotations
import sqlite3
from provoware_db.domain.errors import ConflictError, NotFoundError, RevisionConflictError, ValidationError
from provoware_db.domain.models import FieldDefinition, FieldOption, FieldScope, FieldType, ScalarValue
from provoware_db.domain.normalization import clean_text, make_key

class FieldRepository:
    def __init__(self, con: sqlite3.Connection)->None:self.con=con
    def insert_definition(self,field:FieldDefinition)->None:
        self.con.execute("INSERT INTO field_definitions(id,scope,category_id,entry_id,name,name_key,field_type,is_required,sort_order,help_text,placeholder,unit_label,currency_code) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(field.id,field.scope.value,field.category_id,field.entry_id,field.name,field.name_key,field.field_type.value,int(field.is_required),field.sort_order,field.help_text,field.placeholder,field.unit_label,field.currency_code))
    def _definition(self,row):
        if row is None:return None
        d=dict(row);d['scope']=FieldScope(d['scope']);d['field_type']=FieldType(d['field_type']);d['is_required']=bool(d['is_required']);return FieldDefinition(**d)
    def get_active_definition(self,field_id:str)->FieldDefinition|None:
        return self._definition(self.con.execute("SELECT id,scope,category_id,entry_id,name,name_key,field_type,is_required,sort_order,help_text,placeholder,unit_label,currency_code,revision FROM field_definitions WHERE id=? AND deleted_at IS NULL",(field_id,)).fetchone())
    def get_any_definition(self,field_id:str): return self.con.execute("SELECT * FROM field_definitions WHERE id=?",(field_id,)).fetchone()
    def find_active_by_owner_and_name_key(self,*,scope:FieldScope,name_key:str,category_id:str|None=None,entry_id:str|None=None)->FieldDefinition|None:
        sql=("SELECT id FROM field_definitions WHERE scope='category' AND category_id=? AND name_key=? AND deleted_at IS NULL" if scope is FieldScope.CATEGORY else "SELECT id FROM field_definitions WHERE scope='entry' AND entry_id=? AND name_key=? AND deleted_at IS NULL")
        row=self.con.execute(sql,((category_id if scope is FieldScope.CATEGORY else entry_id),name_key)).fetchone()
        return None if row is None else self.get_active_definition(str(row[0]))
    def list_visible_for_entry(self,entry_id:str,category_id:str)->list[FieldDefinition]:
        rows=self.con.execute("SELECT id,scope,category_id,entry_id,name,name_key,field_type,is_required,sort_order,help_text,placeholder,unit_label,currency_code,revision FROM field_definitions WHERE deleted_at IS NULL AND ((scope='category' AND category_id=?) OR (scope='entry' AND entry_id=?)) ORDER BY sort_order,name_key,id",(category_id,entry_id)).fetchall()
        return [self._definition(r) for r in rows]
    def update_definition(self,field_id:str,*,name:str,is_required:bool,sort_order:int,help_text:str|None,placeholder:str|None,unit_label:str|None,expected_revision:int)->FieldDefinition:
        n=clean_text(name);key=make_key(n)
        cur=self.con.execute("UPDATE field_definitions SET name=?,name_key=?,is_required=?,sort_order=?,help_text=?,placeholder=?,unit_label=?,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NULL AND revision=?",(n,key,int(is_required),sort_order,help_text,placeholder,unit_label,field_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-321: Feld wurde zwischenzeitlich geändert oder ist nicht mehr aktiv.")
        return self.get_active_definition(field_id)
    def soft_delete_definition(self,field_id:str,expected_revision:int)->None:
        cur=self.con.execute("UPDATE field_definitions SET deleted_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NULL AND revision=?",(field_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-322: Feld konnte wegen Revisionskonflikt nicht gelöscht werden.")
    def restore_definition(self,field_id:str,expected_revision:int)->FieldDefinition:
        cur=self.con.execute("UPDATE field_definitions SET deleted_at=NULL,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=revision+1 WHERE id=? AND deleted_at IS NOT NULL AND revision=?",(field_id,expected_revision))
        if cur.rowcount!=1: raise RevisionConflictError("DOM-323: Feld konnte wegen Revisionskonflikt nicht wiederhergestellt werden.")
        return self.get_active_definition(field_id)
    def insert_option(self,opt:FieldOption)->None:
        self.con.execute("INSERT INTO field_options(id,field_definition_id,label,option_key,sort_order) VALUES(?,?,?,?,?)",(opt.id,opt.field_definition_id,opt.label,opt.option_key,opt.sort_order))
    def get_active_option(self,option_id:str)->FieldOption|None:
        row=self.con.execute("SELECT id,field_definition_id,label,option_key,sort_order FROM field_options WHERE id=? AND deleted_at IS NULL",(option_id,)).fetchone();return None if row is None else FieldOption(**dict(row))
    def list_active_options(self,field_id:str)->list[FieldOption]:
        return [FieldOption(**dict(r)) for r in self.con.execute("SELECT id,field_definition_id,label,option_key,sort_order FROM field_options WHERE field_definition_id=? AND deleted_at IS NULL ORDER BY sort_order,option_key,id",(field_id,)).fetchall()]
    def find_option_by_key(self,field_id:str,key:str)->FieldOption|None:
        row=self.con.execute("SELECT id,field_definition_id,label,option_key,sort_order FROM field_options WHERE field_definition_id=? AND option_key=? AND deleted_at IS NULL",(field_id,key)).fetchone();return None if row is None else FieldOption(**dict(row))
    def get_scalar_value(self,entry_id:str,field_id:str)->ScalarValue|None:
        row=self.con.execute("SELECT value_kind,value_text,value_integer,value_real FROM scalar_field_values WHERE entry_id=? AND field_definition_id=?",(entry_id,field_id)).fetchone();return None if row is None else ScalarValue(**dict(row))
    def upsert_scalar_value(self,entry_id:str,field_id:str,value:ScalarValue)->None:
        self.con.execute("INSERT INTO scalar_field_values(entry_id,field_definition_id,value_kind,value_text,value_integer,value_real) VALUES(?,?,?,?,?,?) ON CONFLICT(entry_id,field_definition_id) DO UPDATE SET value_kind=excluded.value_kind,value_text=excluded.value_text,value_integer=excluded.value_integer,value_real=excluded.value_real,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=scalar_field_values.revision+1",(entry_id,field_id,value.value_kind,value.value_text,value.value_integer,value.value_real))
    def set_single_choice(self,entry_id:str,field_id:str,option_id:str)->None:
        self.con.execute("INSERT INTO single_choice_values(entry_id,field_definition_id,option_id) VALUES(?,?,?) ON CONFLICT(entry_id,field_definition_id) DO UPDATE SET option_id=excluded.option_id,updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'),revision=single_choice_values.revision+1",(entry_id,field_id,option_id))
    def get_single_choice(self,entry_id:str,field_id:str)->str|None:
        r=self.con.execute("SELECT option_id FROM single_choice_values WHERE entry_id=? AND field_definition_id=?",(entry_id,field_id)).fetchone();return None if r is None else str(r[0])
    def set_multi_choice(self,entry_id:str,field_id:str,option_ids:list[str])->None:
        self.con.execute("DELETE FROM multi_choice_values WHERE entry_id=? AND field_definition_id=?",(entry_id,field_id))
        self.con.executemany("INSERT INTO multi_choice_values(entry_id,field_definition_id,option_id) VALUES(?,?,?)",[(entry_id,field_id,x) for x in option_ids])
    def get_multi_choice(self,entry_id:str,field_id:str)->list[str]:
        return [str(r[0]) for r in self.con.execute("SELECT option_id FROM multi_choice_values WHERE entry_id=? AND field_definition_id=? ORDER BY option_id",(entry_id,field_id)).fetchall()]
    def list_values_for_entry(self,entry_id:str)->dict[str,ScalarValue|FieldOption|list[FieldOption]]:
        values:dict[str,ScalarValue|FieldOption|list[FieldOption]]={}
        for r in self.con.execute("SELECT field_definition_id,value_kind,value_text,value_integer,value_real FROM scalar_field_values WHERE entry_id=?",(entry_id,)).fetchall():
            values[str(r["field_definition_id"])]=ScalarValue(value_kind=r["value_kind"],value_text=r["value_text"],value_integer=r["value_integer"],value_real=r["value_real"])
        for r in self.con.execute("SELECT s.field_definition_id,o.id,o.field_definition_id AS option_field_definition_id,o.label,o.option_key,o.sort_order FROM single_choice_values s JOIN field_options o ON o.id=s.option_id WHERE s.entry_id=? AND o.deleted_at IS NULL",(entry_id,)).fetchall():
            values[str(r["field_definition_id"])]=FieldOption(id=r["id"],field_definition_id=r["option_field_definition_id"],label=r["label"],option_key=r["option_key"],sort_order=r["sort_order"])
        for r in self.con.execute("SELECT m.field_definition_id,o.id,o.field_definition_id AS option_field_definition_id,o.label,o.option_key,o.sort_order FROM multi_choice_values m JOIN field_options o ON o.id=m.option_id WHERE m.entry_id=? AND o.deleted_at IS NULL ORDER BY m.field_definition_id,o.sort_order,o.option_key,o.id",(entry_id,)).fetchall():
            field_id=str(r["field_definition_id"])
            option=FieldOption(id=r["id"],field_definition_id=r["option_field_definition_id"],label=r["label"],option_key=r["option_key"],sort_order=r["sort_order"])
            current=values.setdefault(field_id,[])
            if isinstance(current,list): current.append(option)
        return values
    def search(self,q:str,limit:int=50):
        like=f"%{make_key(q)}%";return self.con.execute("SELECT f.id,f.scope,COALESCE(f.category_id,e.category_id) AS category_id,f.entry_id,f.name FROM field_definitions f LEFT JOIN categories c ON f.scope='category' AND c.id=f.category_id LEFT JOIN entries e ON f.scope='entry' AND e.id=f.entry_id LEFT JOIN categories ec ON e.category_id=ec.id WHERE f.deleted_at IS NULL AND f.name_key LIKE ? AND ((f.scope='category' AND c.deleted_at IS NULL) OR (f.scope='entry' AND e.deleted_at IS NULL AND ec.deleted_at IS NULL)) ORDER BY f.name_key,f.id LIMIT ?",(like,limit)).fetchall()

    def search_values(self,q:str,limit:int=50):
        key=make_key(q)
        if not key or limit<=0:return []
        rows=[]

        scalar_sql="""
        SELECT c.id AS category_id,c.name AS category_name,e.id AS entry_id,e.title AS entry_title,
               f.id AS field_id,f.name AS field_name,f.field_type,f.currency_code,
               v.value_text,v.value_integer,v.value_real
        FROM scalar_field_values v
        JOIN entries e ON e.id=v.entry_id AND e.deleted_at IS NULL
        JOIN categories c ON c.id=e.category_id AND c.deleted_at IS NULL
        JOIN field_definitions f ON f.id=v.field_definition_id AND f.deleted_at IS NULL
        WHERE ((f.scope='category' AND f.category_id=e.category_id)
               OR (f.scope='entry' AND f.entry_id=e.id))
        """
        for r in self.con.execute(scalar_sql).fetchall():
            field_type=str(r["field_type"])
            preview=None
            aliases=[]
            if field_type in {"text","long_text"} and r["value_text"] is not None:
                preview=str(r["value_text"])
                aliases=[preview]
            elif field_type=="integer" and r["value_integer"] is not None:
                preview=str(int(r["value_integer"]))
                aliases=[preview]
            elif field_type=="decimal" and r["value_text"] is not None:
                canonical=str(r["value_text"])
                preview=canonical.replace(".",",")
                aliases=[canonical,preview]
            elif field_type=="money" and r["value_integer"] is not None:
                minor=int(r["value_integer"])
                amount=f"{minor/100:.2f}"
                currency="" if r["currency_code"] is None else str(r["currency_code"])
                preview=amount.replace(".",",")+(f" {currency}" if currency else "")
                aliases=[amount,amount.replace(".",","),preview]
            elif field_type=="boolean" and r["value_integer"] is not None:
                preview="Ja" if int(r["value_integer"]) else "Nein"
                aliases=[preview,"true" if int(r["value_integer"]) else "false","1" if int(r["value_integer"]) else "0"]
            elif field_type=="date" and r["value_text"] is not None:
                canonical=str(r["value_text"])
                try:
                    y,m,d=canonical.split("-",2)
                    preview=f"{d}.{m}.{y}"
                except ValueError:
                    preview=canonical
                aliases=[canonical,preview]
            elif field_type=="datetime" and r["value_text"] is not None:
                canonical=str(r["value_text"])
                preview=canonical
                try:
                    date_part,time_part=canonical.split("T",1)
                    y,m,d=date_part.split("-",2)
                    hhmm=time_part[:5]
                    preview=f"{d}.{m}.{y}, {hhmm}"
                except ValueError:
                    pass
                aliases=[canonical,preview]
            if preview is None or not any(key in make_key(alias) for alias in aliases):
                continue
            rows.append({
                "category_id":str(r["category_id"]),
                "category_name":str(r["category_name"]),
                "entry_id":str(r["entry_id"]),
                "entry_title":str(r["entry_title"]),
                "field_id":str(r["field_id"]),
                "field_name":str(r["field_name"]),
                "value_preview":preview,
                "source_kind":"scalar_"+field_type,
            })

        choice_sql="""
        SELECT c.id AS category_id,c.name AS category_name,e.id AS entry_id,e.title AS entry_title,
               f.id AS field_id,f.name AS field_name,o.label AS value_preview,src.source_kind
        FROM (
            SELECT entry_id,field_definition_id,option_id,'single_choice' AS source_kind
            FROM single_choice_values
            UNION ALL
            SELECT entry_id,field_definition_id,option_id,'multi_choice' AS source_kind
            FROM multi_choice_values
        ) src
        JOIN entries e ON e.id=src.entry_id AND e.deleted_at IS NULL
        JOIN categories c ON c.id=e.category_id AND c.deleted_at IS NULL
        JOIN field_definitions f ON f.id=src.field_definition_id AND f.deleted_at IS NULL
        JOIN field_options o ON o.id=src.option_id AND o.deleted_at IS NULL
        WHERE ((f.scope='category' AND f.category_id=e.category_id)
               OR (f.scope='entry' AND f.entry_id=e.id))
        """
        grouped={}
        for r in self.con.execute(choice_sql).fetchall():
            preview=str(r["value_preview"])
            if key not in make_key(preview):continue
            group_key=(str(r["category_id"]),str(r["entry_id"]),str(r["field_id"]))
            item=grouped.setdefault(group_key,{
                "category_id":str(r["category_id"]),
                "category_name":str(r["category_name"]),
                "entry_id":str(r["entry_id"]),
                "entry_title":str(r["entry_title"]),
                "field_id":str(r["field_id"]),
                "field_name":str(r["field_name"]),
                "value_preview":[],
                "source_kind":str(r["source_kind"]),
            })
            item["value_preview"].append(preview)
            if item["source_kind"]!=str(r["source_kind"]):
                item["source_kind"]="choice"

        for item in grouped.values():
            item["value_preview"]=", ".join(sorted(dict.fromkeys(item["value_preview"]),key=make_key))
            rows.append(item)

        rows.sort(key=lambda r:(
            make_key(str(r["category_name"])),
            make_key(str(r["entry_title"])),
            make_key(str(r["field_name"])),
            make_key(str(r["value_preview"])),
            str(r["field_id"]),
        ))
        return rows[:limit]

