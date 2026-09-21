from __future__ import annotations

from provoware_db.domain.errors import ConflictError, NotFoundError
from provoware_db.domain.models import FieldDefinition, FieldScope, FieldType
from provoware_db.tui.write_adapter import EntryFieldWriteAdapter


class FakeEntryFieldService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, FieldType]] = []
        self.result = FieldDefinition.new(
            id="fld-new",
            scope=FieldScope.ENTRY,
            entry_id="ent-selected",
            name="Seriennummer",
            field_type=FieldType.TEXT,
        )

    def create_entry_field(
        self,
        entry_id: str,
        name: str,
        field_type: FieldType,
    ) -> FieldDefinition:
        self.calls.append((entry_id, name, field_type))
        return self.result


class MissingEntryService(FakeEntryFieldService):
    def create_entry_field(
        self,
        entry_id: str,
        name: str,
        field_type: FieldType,
    ) -> FieldDefinition:
        self.calls.append((entry_id, name, field_type))
        raise NotFoundError("DOM-104: Feld-Eintrag wurde nicht gefunden.")


class DuplicateFieldService(FakeEntryFieldService):
    def create_entry_field(
        self,
        entry_id: str,
        name: str,
        field_type: FieldType,
    ) -> FieldDefinition:
        self.calls.append((entry_id, name, field_type))
        raise ConflictError("DOM-202: Ein aktives Feld mit diesem Namen existiert hier bereits.")


def test_adapter_delegates_exactly_once_and_returns_same_definition() -> None:
    service = FakeEntryFieldService()
    adapter = EntryFieldWriteAdapter(service)

    result = adapter.create_entry_field(
        "ent-selected",
        "Seriennummer",
        FieldType.TEXT,
    )

    assert service.calls == [
        ("ent-selected", "Seriennummer", FieldType.TEXT),
    ]
    assert result is service.result
    assert result.entry_id == "ent-selected"
    assert result.field_type is FieldType.TEXT


def test_adapter_preserves_missing_parent_contract() -> None:
    service = MissingEntryService()
    adapter = EntryFieldWriteAdapter(service)

    try:
        adapter.create_entry_field("ent-missing", "Seriennummer", FieldType.TEXT)
    except NotFoundError as exc:
        assert str(exc).startswith("DOM-104:")
    else:
        raise AssertionError("NotFoundError muss unverändert bis zur Adapter-Grenze gelangen")

    assert service.calls == [
        ("ent-missing", "Seriennummer", FieldType.TEXT),
    ]


def test_adapter_preserves_duplicate_field_contract() -> None:
    service = DuplicateFieldService()
    adapter = EntryFieldWriteAdapter(service)

    try:
        adapter.create_entry_field("ent-selected", "Seriennummer", FieldType.TEXT)
    except ConflictError as exc:
        assert str(exc).startswith("DOM-202:")
    else:
        raise AssertionError("ConflictError muss unverändert bis zur Adapter-Grenze gelangen")

    assert service.calls == [
        ("ent-selected", "Seriennummer", FieldType.TEXT),
    ]


if __name__ == "__main__":
    test_adapter_delegates_exactly_once_and_returns_same_definition()
    test_adapter_preserves_missing_parent_contract()
    test_adapter_preserves_duplicate_field_contract()
