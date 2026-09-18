from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from uuid import uuid4

from provoware_db.domain.errors import ConflictError, NotFoundError, ValidationError
from provoware_db.domain.models import Category, Entry, FieldDefinition, FieldOption, FieldScope, FieldType, ScalarValue, SearchHit
from provoware_db.domain.rules import assert_field_applies_to_entry
from provoware_db.storage.sqlite.audit import AuditWriter
from provoware_db.storage.sqlite.coordinator import CoordinatedWriter
from provoware_db.storage.sqlite.repositories import CategoryRepository, EntryRepository, FieldRepository


class CatalogService:
    """Application-facing API for category → entry → fields.

    The UI calls this service; it never calls SQL directly.
    """

    def __init__(
        self,
        main_con: sqlite3.Connection,
        state_con: sqlite3.Connection,
        main_db_path: Path,
        *,
        app_session_id: str,
        app_version: str,
    ) -> None:
        self.main_con = main_con
        self.app_version = app_version
        self.categories = CategoryRepository(main_con)
        self.entries = EntryRepository(main_con)
        self.fields = FieldRepository(main_con)
        self.audit = AuditWriter(main_con, app_version=app_version)
        self.writer = CoordinatedWriter(
            main_con,
            state_con,
            main_db_path,
            app_session_id=app_session_id,
            app_version=app_version,
        )

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"

    def list_categories(self) -> list[Category]:
        return self.categories.list_active()

    def list_entries(self, category_id: str) -> list[Entry]:
        if self.categories.get_active(category_id) is None:
            return []
        return self.entries.list_active_by_category(category_id)

    def list_fields(self, entry_id: str) -> list[FieldDefinition]:
        entry = self.entries.get_active(entry_id)
        if entry is None:
            raise NotFoundError("DOM-101: Eintrag wurde nicht gefunden.")
        return self.fields.list_visible_for_entry(entry.id, entry.category_id)

    def create_category(self, name: str, *, description: str | None = None, sort_order: int = 0) -> Category:
        category = Category.new(self._new_id("cat"), name, description, sort_order)

        def action(con: sqlite3.Connection, operation_id: str) -> Category:
            if self.categories.find_active_by_name_key(category.name_key) is not None:
                raise ConflictError("DOM-201: Eine aktive Kategorie mit diesem Namen existiert bereits.")
            self.categories.insert(category)
            self.audit.record(
                operation_id=operation_id,
                action="category.create",
                entity_type="category",
                entity_id=category.id,
                category_id=category.id,
                summary=f"Kategorie „{category.name}“ angelegt.",
                after=category,
            )
            return category

        tx_factory = lambda op: (
            lambda con: self.categories.get_active(category.id) is not None,
            lambda con: self.audit.exists_for_operation(op),
        )
        _, result = self.writer.execute(
            operation_type="category.create",
            entity_type="category",
            entity_id=category.id,
            action=action,
            transactional_postconditions_factory=tx_factory,
            committed_postconditions_factory=tx_factory,
        )
        return result

    def create_entry(self, category_id: str, title: str, *, sort_order: int = 0) -> Entry:
        entry = Entry.new(self._new_id("ent"), category_id, title, sort_order)

        def action(con: sqlite3.Connection, operation_id: str) -> Entry:
            if self.categories.get_active(category_id) is None:
                raise NotFoundError("DOM-102: Kategorie wurde nicht gefunden oder liegt im Papierkorb.")
            self.entries.insert(entry)
            self.audit.record(
                operation_id=operation_id,
                action="entry.create",
                entity_type="entry",
                entity_id=entry.id,
                category_id=entry.category_id,
                entry_id=entry.id,
                summary=f"Eintrag „{entry.title}“ angelegt.",
                after=entry,
            )
            return entry

        tx_factory = lambda op: (
            lambda con: self.entries.get_active(entry.id) is not None,
            lambda con: self.audit.exists_for_operation(op),
        )
        _, result = self.writer.execute(
            operation_type="entry.create",
            entity_type="entry",
            entity_id=entry.id,
            action=action,
            transactional_postconditions_factory=tx_factory,
            committed_postconditions_factory=tx_factory,
        )
        return result

    def create_category_field(
        self,
        category_id: str,
        name: str,
        field_type: FieldType,
        **kwargs: Any,
    ) -> FieldDefinition:
        return self._create_field(
            scope=FieldScope.CATEGORY,
            owner_id=category_id,
            name=name,
            field_type=field_type,
            **kwargs,
        )

    def create_entry_field(
        self,
        entry_id: str,
        name: str,
        field_type: FieldType,
        **kwargs: Any,
    ) -> FieldDefinition:
        return self._create_field(
            scope=FieldScope.ENTRY,
            owner_id=entry_id,
            name=name,
            field_type=field_type,
            **kwargs,
        )

    def _create_field(
        self,
        *,
        scope: FieldScope,
        owner_id: str,
        name: str,
        field_type: FieldType,
        is_required: bool = False,
        sort_order: int = 0,
        help_text: str | None = None,
        placeholder: str | None = None,
        unit_label: str | None = None,
        currency_code: str | None = None,
    ) -> FieldDefinition:
        field = FieldDefinition.new(
            id=self._new_id("fld"),
            scope=scope,
            category_id=owner_id if scope is FieldScope.CATEGORY else None,
            entry_id=owner_id if scope is FieldScope.ENTRY else None,
            name=name,
            field_type=field_type,
            is_required=is_required,
            sort_order=sort_order,
            help_text=help_text,
            placeholder=placeholder,
            unit_label=unit_label,
            currency_code=currency_code,
        )

        def action(con: sqlite3.Connection, operation_id: str) -> FieldDefinition:
            if scope is FieldScope.CATEGORY:
                if self.categories.get_active(owner_id) is None:
                    raise NotFoundError("DOM-103: Feld-Kategorie wurde nicht gefunden.")
            elif self.entries.get_active(owner_id) is None:
                raise NotFoundError("DOM-104: Feld-Eintrag wurde nicht gefunden.")
            duplicate = self.fields.find_active_by_owner_and_name_key(
                scope=scope,
                name_key=field.name_key,
                category_id=field.category_id,
                entry_id=field.entry_id,
            )
            if duplicate is not None:
                raise ConflictError("DOM-202: Ein aktives Feld mit diesem Namen existiert hier bereits.")
            self.fields.insert_definition(field)
            owner_entry = self.entries.get_active(owner_id) if scope is FieldScope.ENTRY else None
            self.audit.record(
                operation_id=operation_id,
                action="field_definition.create",
                entity_type="field_definition",
                entity_id=field.id,
                category_id=field.category_id or (owner_entry.category_id if owner_entry else None),
                entry_id=field.entry_id,
                summary=f"Feld „{field.name}“ angelegt.",
                after=field,
            )
            return field

        tx_factory = lambda op: (
            lambda con: self.fields.get_active_definition(field.id) is not None,
            lambda con: self.audit.exists_for_operation(op),
        )
        _, result = self.writer.execute(
            operation_type="field_definition.create",
            entity_type="field_definition",
            entity_id=field.id,
            action=action,
            transactional_postconditions_factory=tx_factory,
            committed_postconditions_factory=tx_factory,
        )
        return result

    def set_scalar_value(self, entry_id: str, field_id: str, value: Any) -> ScalarValue:
        # Pure input conversion happens before a durable journal entry is opened.
        field_preview = self.fields.get_active_definition(field_id)
        if field_preview is None:
            raise NotFoundError("DOM-105: Feld wurde nicht gefunden.")
        scalar = ScalarValue.from_input(field_preview.field_type, value)
        entity_id = f"{entry_id}:{field_id}"

        def action(con: sqlite3.Connection, operation_id: str) -> ScalarValue:
            entry = self.entries.get_active(entry_id)
            field = self.fields.get_active_definition(field_id)
            if entry is None:
                raise NotFoundError("DOM-101: Eintrag wurde nicht gefunden.")
            if field is None:
                raise NotFoundError("DOM-105: Feld wurde nicht gefunden.")
            assert_field_applies_to_entry(field, entry)
            before = self.fields.get_scalar_value(entry_id, field_id)
            self.fields.upsert_scalar_value(entry_id, field_id, scalar)
            self.audit.record(
                operation_id=operation_id,
                action="field_value.set",
                entity_type="field_value",
                entity_id=entity_id,
                category_id=entry.category_id,
                entry_id=entry.id,
                summary=f"Feldwert „{field.name}“ gespeichert.",
                before=before,
                after=scalar,
            )
            return scalar

        def checks(op: str):
            return (
                lambda con: self.fields.get_scalar_value(entry_id, field_id) == scalar,
                lambda con: self.audit.exists_for_operation(op),
            )

        _, result = self.writer.execute(
            operation_type="field_value.set",
            entity_type="field_value",
            entity_id=entity_id,
            action=action,
            transactional_postconditions_factory=checks,
            committed_postconditions_factory=checks,
        )
        return result

    def get_scalar_value(self, entry_id: str, field_id: str) -> ScalarValue | None:
        return self.fields.get_scalar_value(entry_id, field_id)


    def add_field_option(self, field_id: str, label: str, *, sort_order: int = 0) -> FieldOption:
        field = self.fields.get_active_definition(field_id)
        if field is None:
            raise NotFoundError("DOM-105: Feld wurde nicht gefunden.")
        if field.field_type not in (FieldType.SINGLE_CHOICE, FieldType.MULTI_CHOICE):
            raise ValidationError("VAL-452: Auswahloptionen sind nur für Auswahlfelder erlaubt.")
        option = FieldOption.new(self._new_id("opt"), field_id, label, sort_order)
        def action(con, operation_id):
            if self.fields.find_option_by_key(field_id, option.option_key) is not None:
                raise ConflictError("DOM-203: Diese Auswahloption existiert bereits.")
            self.fields.insert_option(option)
            self.audit.record(operation_id=operation_id, action="field_option.create", entity_type="field_definition", entity_id=field_id, category_id=field.category_id, entry_id=field.entry_id, summary=f"Auswahl „{option.label}“ angelegt.", after=option)
            return option
        def checks(op): return (lambda con: self.fields.get_active_option(option.id) is not None, lambda con: self.audit.exists_for_operation(op))
        _, result = self.writer.execute(operation_type="field_option.create", entity_type="field_definition", entity_id=field_id, action=action, transactional_postconditions_factory=checks, committed_postconditions_factory=checks)
        return result

    def list_field_options(self, field_id: str) -> list[FieldOption]:
        return self.fields.list_active_options(field_id)

    def set_single_choice(self, entry_id: str, field_id: str, option_id: str) -> str:
        return self._set_choice(entry_id, field_id, [option_id], multi=False)[0]

    def set_multi_choice(self, entry_id: str, field_id: str, option_ids: list[str]) -> list[str]:
        return self._set_choice(entry_id, field_id, option_ids, multi=True)

    def _set_choice(self, entry_id: str, field_id: str, option_ids: list[str], *, multi: bool):
        entry = self.entries.get_active(entry_id); field = self.fields.get_active_definition(field_id)
        if entry is None: raise NotFoundError("DOM-101: Eintrag wurde nicht gefunden.")
        if field is None: raise NotFoundError("DOM-105: Feld wurde nicht gefunden.")
        expected = FieldType.MULTI_CHOICE if multi else FieldType.SINGLE_CHOICE
        if field.field_type is not expected: raise ValidationError("VAL-453: Auswahlmodus passt nicht zum Feldtyp.")
        assert_field_applies_to_entry(field, entry)
        unique=list(dict.fromkeys(option_ids))
        if not unique and not multi: raise ValidationError("VAL-454: Single-Choice benötigt genau eine Auswahl.")
        for oid in unique:
            opt=self.fields.get_active_option(oid)
            if opt is None or opt.field_definition_id != field_id: raise ValidationError("VAL-455: Auswahl gehört nicht zu diesem Feld oder ist gelöscht.")
        before=self.fields.get_multi_choice(entry_id,field_id) if multi else self.fields.get_single_choice(entry_id,field_id)
        entity_id=f"{entry_id}:{field_id}"
        def action(con,operation_id):
            if multi:self.fields.set_multi_choice(entry_id,field_id,unique)
            else:self.fields.set_single_choice(entry_id,field_id,unique[0])
            self.audit.record(operation_id=operation_id,action="field_value.choice_set",entity_type="field_value",entity_id=entity_id,category_id=entry.category_id,entry_id=entry.id,summary=f"Auswahlwert „{field.name}“ gespeichert.",before=before,after=unique if multi else unique[0])
            return unique
        def checks(op):
            return (lambda con: (self.fields.get_multi_choice(entry_id,field_id)==sorted(unique) if multi else self.fields.get_single_choice(entry_id,field_id)==unique[0]), lambda con:self.audit.exists_for_operation(op))
        _, result=self.writer.execute(operation_type="field_value.choice_set",entity_type="field_value",entity_id=entity_id,action=action,transactional_postconditions_factory=checks,committed_postconditions_factory=checks)
        return result

    def update_category(self, category_id: str, *, name: str, description: str | None, sort_order: int, expected_revision: int) -> Category:
        before=self.categories.get_active(category_id)
        if before is None: raise NotFoundError("DOM-100: Kategorie wurde nicht gefunden.")
        def action(con,op):
            updated=self.categories.update(category_id,name=name,description=description,sort_order=sort_order,expected_revision=expected_revision)
            self.audit.record(operation_id=op,action="category.update",entity_type="category",entity_id=category_id,category_id=category_id,summary=f"Kategorie „{updated.name}“ bearbeitet.",before=before,after=updated)
            return updated
        def checks(op): return (lambda con:self.categories.get_active(category_id) is not None,lambda con:self.audit.exists_for_operation(op))
        return self.writer.execute(operation_type="category.update",entity_type="category",entity_id=category_id,action=action,transactional_postconditions_factory=checks,committed_postconditions_factory=checks)[1]

    def update_entry(self, entry_id: str, *, title: str, is_favorite: bool, sort_order: int, expected_revision: int) -> Entry:
        before=self.entries.get_active(entry_id)
        if before is None: raise NotFoundError("DOM-101: Eintrag wurde nicht gefunden.")
        def action(con,op):
            updated=self.entries.update(entry_id,title=title,is_favorite=is_favorite,sort_order=sort_order,expected_revision=expected_revision)
            self.audit.record(operation_id=op,action="entry.update",entity_type="entry",entity_id=entry_id,category_id=updated.category_id,entry_id=entry_id,summary=f"Eintrag „{updated.title}“ bearbeitet.",before=before,after=updated)
            return updated
        def checks(op):return (lambda con:self.entries.get_active(entry_id) is not None,lambda con:self.audit.exists_for_operation(op))
        return self.writer.execute(operation_type="entry.update",entity_type="entry",entity_id=entry_id,action=action,transactional_postconditions_factory=checks,committed_postconditions_factory=checks)[1]

    def update_field(self, field_id: str, *, name: str, is_required: bool, sort_order: int, help_text: str | None, placeholder: str | None, unit_label: str | None, expected_revision: int) -> FieldDefinition:
        before=self.fields.get_active_definition(field_id)
        if before is None: raise NotFoundError("DOM-105: Feld wurde nicht gefunden.")
        def action(con,op):
            updated=self.fields.update_definition(field_id,name=name,is_required=is_required,sort_order=sort_order,help_text=help_text,placeholder=placeholder,unit_label=unit_label,expected_revision=expected_revision)
            self.audit.record(operation_id=op,action="field_definition.update",entity_type="field_definition",entity_id=field_id,category_id=updated.category_id,entry_id=updated.entry_id,summary=f"Feld „{updated.name}“ bearbeitet.",before=before,after=updated)
            return updated
        def checks(op):return (lambda con:self.fields.get_active_definition(field_id) is not None,lambda con:self.audit.exists_for_operation(op))
        return self.writer.execute(operation_type="field_definition.update",entity_type="field_definition",entity_id=field_id,action=action,transactional_postconditions_factory=checks,committed_postconditions_factory=checks)[1]

    def _trash_restore(self, kind: str, object_id: str, expected_revision: int, restore: bool):
        if kind=="category": repo=self.categories; before=repo.get_any(object_id); fn=repo.restore if restore else repo.soft_delete; entity_type="category"
        elif kind=="entry": repo=self.entries; before=repo.get_any(object_id); fn=repo.restore if restore else repo.soft_delete; entity_type="entry"
        elif kind=="field": repo=self.fields; before=repo.get_any_definition(object_id); fn=repo.restore_definition if restore else repo.soft_delete_definition; entity_type="field_definition"
        else: raise ValidationError("VAL-460: Unbekannter Papierkorb-Typ.")
        if before is None: raise NotFoundError("DOM-120: Objekt wurde nicht gefunden.")
        action_name=f"{entity_type}.{'restore' if restore else 'delete'}"
        def action(con,op):
            result=fn(object_id,expected_revision)
            self.audit.record(operation_id=op,action=action_name,entity_type=entity_type,entity_id=object_id,summary=("Objekt wiederhergestellt." if restore else "Objekt in den Papierkorb verschoben."),before=dict(before),after=None if not restore else result)
            return result
        def is_state(con):
            row=(self.categories.get_any(object_id) if kind=='category' else self.entries.get_any(object_id) if kind=='entry' else self.fields.get_any_definition(object_id))
            return row is not None and ((row['deleted_at'] is None)==restore)
        def checks(op):return (is_state,lambda con:self.audit.exists_for_operation(op))
        return self.writer.execute(operation_type=action_name,entity_type=entity_type,entity_id=object_id,action=action,transactional_postconditions_factory=checks,committed_postconditions_factory=checks)[1]

    def trash_category(self,id:str,expected_revision:int): return self._trash_restore("category",id,expected_revision,False)
    def restore_category(self,id:str,expected_revision:int): return self._trash_restore("category",id,expected_revision,True)
    def trash_entry(self,id:str,expected_revision:int): return self._trash_restore("entry",id,expected_revision,False)
    def restore_entry(self,id:str,expected_revision:int): return self._trash_restore("entry",id,expected_revision,True)
    def trash_field(self,id:str,expected_revision:int): return self._trash_restore("field",id,expected_revision,False)
    def restore_field(self,id:str,expected_revision:int): return self._trash_restore("field",id,expected_revision,True)

    def search(self, query: str, *, limit: int = 50) -> list[SearchHit]:
        q=query.strip()
        if not q:return []
        hits=[]
        for r in self.categories.search(q,limit): hits.append(SearchHit("category",r['id'],r['name'],category_id=r['id']))
        for r in self.entries.search(q,limit): hits.append(SearchHit("entry",r['id'],r['title'],category_id=r['category_id'],entry_id=r['id']))
        for r in self.fields.search(q,limit): hits.append(SearchHit("field_definition",r['id'],r['name'],category_id=r['category_id'],entry_id=r['entry_id']))
        return hits[:limit]


    def undo_operation(self, operation_id: str) -> str:
        """Undo a supported prior operation by creating a new audited operation.

        Undo never rewrites audit history. It applies an inverse change through the normal
        writer so crash-reconciliation and post-validation remain active.
        """
        import json
        row = self.main_con.execute(
            "SELECT action,entity_type,entity_id,before_json,after_json,is_undoable FROM audit_events "
            "WHERE operation_id=? ORDER BY occurred_at DESC,id DESC LIMIT 1",
            (operation_id,),
        ).fetchone()
        if row is None:
            raise NotFoundError("DOM-130: Zu diesem Vorgang wurde kein Audit-Eintrag gefunden.")
        if not bool(row["is_undoable"]):
            raise ValidationError("VAL-470: Dieser Vorgang ist nicht rückgängig machbar.")
        action = str(row["action"])
        entity_id = row["entity_id"]
        before = json.loads(row["before_json"]) if row["before_json"] else None

        if action == "category.update" and before:
            current = self.categories.get_active(entity_id)
            if current is None: raise NotFoundError("DOM-100: Kategorie wurde nicht gefunden.")
            self.update_category(entity_id, name=before["name"], description=before.get("description"), sort_order=before.get("sort_order",0), expected_revision=current.revision)
        elif action == "entry.update" and before:
            current = self.entries.get_active(entity_id)
            if current is None: raise NotFoundError("DOM-101: Eintrag wurde nicht gefunden.")
            self.update_entry(entity_id, title=before["title"], is_favorite=bool(before.get("is_favorite",False)), sort_order=before.get("sort_order",0), expected_revision=current.revision)
        elif action == "field_definition.update" and before:
            current = self.fields.get_active_definition(entity_id)
            if current is None: raise NotFoundError("DOM-105: Feld wurde nicht gefunden.")
            self.update_field(entity_id, name=before["name"], is_required=bool(before.get("is_required",False)), sort_order=before.get("sort_order",0), help_text=before.get("help_text"), placeholder=before.get("placeholder"), unit_label=before.get("unit_label"), expected_revision=current.revision)
        elif action in ("category.delete","entry.delete","field_definition.delete"):
            kind = "category" if action.startswith("category") else "entry" if action.startswith("entry") else "field"
            raw = self.categories.get_any(entity_id) if kind=="category" else self.entries.get_any(entity_id) if kind=="entry" else self.fields.get_any_definition(entity_id)
            if raw is None: raise NotFoundError("DOM-120: Objekt wurde nicht gefunden.")
            self._trash_restore(kind,entity_id,int(raw["revision"]),True)
        elif action in ("category.restore","entry.restore","field_definition.restore"):
            kind = "category" if action.startswith("category") else "entry" if action.startswith("entry") else "field"
            raw = self.categories.get_any(entity_id) if kind=="category" else self.entries.get_any(entity_id) if kind=="entry" else self.fields.get_any_definition(entity_id)
            if raw is None: raise NotFoundError("DOM-120: Objekt wurde nicht gefunden.")
            self._trash_restore(kind,entity_id,int(raw["revision"]),False)
        elif action == "field_value.set":
            entry_id, field_id = str(entity_id).split(":",1)
            if before is None:
                def inv(con,op):
                    self.main_con.execute("DELETE FROM scalar_field_values WHERE entry_id=? AND field_definition_id=?",(entry_id,field_id))
                    self.audit.record(operation_id=op,action="field_value.undo",entity_type="field_value",entity_id=entity_id,entry_id=entry_id,summary="Feldwert rückgängig gemacht.",before=row["after_json"],after=None,is_undoable=False)
                self.writer.execute(operation_type="field_value.undo",entity_type="field_value",entity_id=entity_id,action=inv)
            else:
                scalar=ScalarValue(**before)
                def inv(con,op):
                    self.fields.upsert_scalar_value(entry_id,field_id,scalar)
                    self.audit.record(operation_id=op,action="field_value.undo",entity_type="field_value",entity_id=entity_id,entry_id=entry_id,summary="Feldwert rückgängig gemacht.",after=scalar,is_undoable=False)
                self.writer.execute(operation_type="field_value.undo",entity_type="field_value",entity_id=entity_id,action=inv)
        else:
            raise ValidationError(f"VAL-471: Undo für {action} ist noch nicht freigegeben.")
        return operation_id
