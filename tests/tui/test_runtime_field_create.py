from __future__ import annotations

import asyncio
from typing import Sequence

from textual.widgets import Input, Label, ListView

from provoware_db.domain.errors import ConflictError
from provoware_db.domain.models import FieldDefinition, FieldScope, FieldType
from provoware_db.tui.runtime import ProvowareDbTui
from provoware_db.tui.view_models import EventItem, FieldRow, HealthItem, NavItem


class MutableFieldPort:
    def __init__(self) -> None:
        self.entries_data = (
            NavItem("entry-a", "Eintrag A"),
            NavItem("entry-b", "Eintrag B"),
        )
        self.fields_data: dict[str, list[FieldRow]] = {
            "entry-a": [],
            "entry-b": [],
        }
        self.category_reads = 0
        self.entry_reads: list[str] = []
        self.field_reads: list[str] = []

    def categories(self) -> Sequence[NavItem]:
        self.category_reads += 1
        return (NavItem("cat-a", "Kategorie A"),)

    def entries(self, category_id: str) -> Sequence[NavItem]:
        self.entry_reads.append(category_id)
        return self.entries_data

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        self.field_reads.append(entry_id)
        return tuple(self.fields_data[entry_id])

    def health(self) -> Sequence[HealthItem]:
        return ()

    def recent_events(self, limit: int = 10) -> Sequence[EventItem]:
        return ()


class FieldWriter:
    def __init__(self, port: MutableFieldPort, *, fail: bool = False) -> None:
        self.port = port
        self.fail = fail
        self.calls: list[tuple[str, str, FieldType]] = []

    def create_entry_field(
        self,
        entry_id: str,
        name: str,
        field_type: FieldType,
    ) -> FieldDefinition:
        self.calls.append((entry_id, name, field_type))
        if self.fail:
            raise ConflictError("DOM-202: Ein aktives Feld mit diesem Namen existiert hier bereits.")

        field = FieldDefinition.new(
            id=f"fld-{len(self.calls)}",
            scope=FieldScope.ENTRY,
            entry_id=entry_id,
            name=name,
            field_type=field_type,
        )
        self.port.fields_data[entry_id].append(
            FieldRow(field.id, field.name, "Nicht gesetzt", field.field_type.value)
        )
        return field


async def _load_entries(pilot) -> None:
    await pilot.press("enter")
    await pilot.pause()


async def _exercise_unavailable_and_requires_entry_selection() -> None:
    port = MutableFieldPort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(100, 30)) as pilot:
        await _load_entries(pilot)
        await pilot.press("f")
        await pilot.pause()

        assert app.query_one("#field-type-list", ListView).display is False
        assert "nicht verfügbar" in app.read_status

    writer = FieldWriter(port)
    app = ProvowareDbTui(port, field_writer=writer)  # type: ignore[arg-type]
    async with app.run_test(size=(100, 30)) as pilot:
        await _load_entries(pilot)
        entry_list = app.query_one("#entry-list", ListView)
        entry_list.index = None

        await pilot.press("f")
        await pilot.pause()

        assert writer.calls == []
        assert app.query_one("#field-type-list", ListView).display is False
        assert "zuerst einen Eintrag" in app.read_status
        assert entry_list.has_focus


async def _exercise_safe_type_list_and_captured_parent_success() -> None:
    port = MutableFieldPort()
    writer = FieldWriter(port)
    app = ProvowareDbTui(port, field_writer=writer)  # type: ignore[arg-type]

    async with app.run_test(size=(120, 36)) as pilot:
        await _load_entries(pilot)
        entry_list = app.query_one("#entry-list", ListView)
        assert entry_list.index == 0
        assert entry_list.has_focus

        category_reads_before = port.category_reads
        entry_reads_before = len(port.entry_reads)

        await pilot.press("f")
        await pilot.pause()

        type_list = app.query_one("#field-type-list", ListView)
        assert type_list.display is True
        assert type_list.has_focus
        assert app._field_create_entry_id == "entry-a"
        assert app._field_create_type is None

        labels = [
            item.query_one(Label).render().plain
            for item in type_list.children
        ]
        assert labels == [
            "Text",
            "Langer Text",
            "Ganzzahl",
            "Dezimalzahl",
            "Datum",
            "Datum und Uhrzeit",
            "Ja / Nein",
        ]
        assert "Geldbetrag" not in labels
        assert "Einfachauswahl" not in labels
        assert "Mehrfachauswahl" not in labels

        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause()

        field_input = app.query_one("#field-create-input", Input)
        assert type_list.display is False
        assert field_input.display is True
        assert field_input.has_focus
        assert app._field_create_type is FieldType.LONG_TEXT

        # The visible index may change while editing; the captured parent must not.
        entry_list.index = 1
        await pilot.press(*"Notiz")
        await pilot.press("enter")
        await pilot.pause()

        assert writer.calls == [("entry-a", "Notiz", FieldType.LONG_TEXT)]
        assert port.field_reads == ["entry-a"]
        assert port.category_reads == category_reads_before
        assert len(port.entry_reads) == entry_reads_before

        field_list = app.query_one("#field-list", ListView)
        assert len(field_list.children) == 1
        assert field_list.query_one(Label).render().plain == "Notiz: Nicht gesetzt"
        assert field_list.index == 0
        assert field_list.has_focus
        assert entry_list.index == 0

        assert field_input.display is False
        assert app._field_create_entry_id is None
        assert app._field_create_type is None
        assert app.read_status == "Feld „Notiz“ angelegt."


async def _exercise_failure_retains_state_and_cancel_writes_nothing() -> None:
    port = MutableFieldPort()
    writer = FieldWriter(port, fail=True)
    app = ProvowareDbTui(port, field_writer=writer)  # type: ignore[arg-type]

    async with app.run_test(size=(120, 36)) as pilot:
        await _load_entries(pilot)
        entry_list = app.query_one("#entry-list", ListView)

        await pilot.press("f")
        await pilot.press("enter")
        await pilot.pause()

        field_input = app.query_one("#field-create-input", Input)
        assert app._field_create_entry_id == "entry-a"
        assert app._field_create_type is FieldType.TEXT
        assert field_input.has_focus

        reads_before = len(port.field_reads)
        await pilot.press(*"Fehler")
        await pilot.press("enter")
        await pilot.pause()

        assert writer.calls == [("entry-a", "Fehler", FieldType.TEXT)]
        assert len(port.field_reads) == reads_before
        assert app._field_create_entry_id == "entry-a"
        assert app._field_create_type is FieldType.TEXT
        assert field_input.display is True
        assert field_input.has_focus
        assert app.read_status.startswith("DOM-202:")

        entry_list.index = 1
        await pilot.press("escape")
        await pilot.pause()

        assert writer.calls == [("entry-a", "Fehler", FieldType.TEXT)]
        assert field_input.display is False
        assert app.query_one("#field-type-list", ListView).display is False
        assert app._field_create_entry_id is None
        assert app._field_create_type is None
        assert entry_list.index == 0
        assert entry_list.has_focus
        assert app.read_status == "Feld anlegen abgebrochen."


async def _exercise_cancel_from_type_selection_writes_nothing() -> None:
    port = MutableFieldPort()
    writer = FieldWriter(port)
    app = ProvowareDbTui(port, field_writer=writer)  # type: ignore[arg-type]

    async with app.run_test(size=(100, 30)) as pilot:
        await _load_entries(pilot)
        entry_list = app.query_one("#entry-list", ListView)
        await pilot.press("f")
        await pilot.pause()

        assert app.query_one("#field-type-list", ListView).has_focus
        await pilot.press("escape")
        await pilot.pause()

        assert writer.calls == []
        assert app._field_create_entry_id is None
        assert app._field_create_type is None
        assert entry_list.index == 0
        assert entry_list.has_focus


def test_field_create_is_unavailable_without_writer_and_requires_entry() -> None:
    asyncio.run(_exercise_unavailable_and_requires_entry_selection())


def test_field_create_uses_only_safe_types_captured_parent_once_and_read_refresh() -> None:
    asyncio.run(_exercise_safe_type_list_and_captured_parent_success())


def test_field_create_failure_keeps_state_and_cancel_does_not_write() -> None:
    asyncio.run(_exercise_failure_retains_state_and_cancel_writes_nothing())


def test_field_create_cancel_from_type_selection_does_not_write() -> None:
    asyncio.run(_exercise_cancel_from_type_selection_writes_nothing())


if __name__ == "__main__":
    test_field_create_is_unavailable_without_writer_and_requires_entry()
    test_field_create_uses_only_safe_types_captured_parent_once_and_read_refresh()
    test_field_create_failure_keeps_state_and_cancel_does_not_write()
    test_field_create_cancel_from_type_selection_does_not_write()
