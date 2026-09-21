from __future__ import annotations

import asyncio
from typing import Sequence

from textual.widgets import Input, ListView

from provoware_db.tui.runtime import ProvowareDbTui
from provoware_db.tui.view_models import EventItem, FieldRow, HealthItem, NavItem


class MutablePort:
    def __init__(self) -> None:
        self.categories_data = [NavItem("cat-a", "Kategorie A"), NavItem("cat-b", "Kategorie B")]
        self.entries_data = {"cat-a": [NavItem("entry-a", "Alt")], "cat-b": []}
        self.entry_reads: list[str] = []

    def categories(self) -> Sequence[NavItem]:
        return tuple(self.categories_data)

    def entries(self, category_id: str) -> Sequence[NavItem]:
        self.entry_reads.append(category_id)
        return tuple(self.entries_data[category_id])

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        return ()

    def health(self) -> Sequence[HealthItem]:
        return ()

    def recent_events(self, limit: int = 10) -> Sequence[EventItem]:
        return ()


class EntryWriter:
    def __init__(self, port: MutablePort, *, fail: bool = False) -> None:
        self.port = port
        self.fail = fail
        self.calls: list[tuple[str, str]] = []

    def create_entry(self, category_id: str, title: str) -> NavItem:
        self.calls.append((category_id, title))
        if self.fail:
            raise RuntimeError("DOM-102: Kategorie nicht gefunden.")
        item = NavItem(f"entry-{len(self.calls)}", title)
        self.port.entries_data[category_id].append(item)
        return item


async def _exercise_readonly_and_no_selection() -> None:
    port = MutablePort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("e")
        await pilot.pause()
        assert app.query_one("#entry-create-input", Input).display is False
        assert "nicht verfügbar" in app.read_status

    writer = EntryWriter(port)
    app = ProvowareDbTui(port, entry_writer=writer)  # type: ignore[arg-type]
    async with app.run_test(size=(80, 24)) as pilot:
        category_list = app.query_one("#category-list", ListView)
        category_list.index = None
        await pilot.press("e")
        await pilot.pause()
        assert writer.calls == []
        assert app.query_one("#entry-create-input", Input).display is False
        assert "zuerst eine Kategorie" in app.read_status
        assert category_list.has_focus


async def _exercise_success_with_captured_parent() -> None:
    port = MutablePort()
    writer = EntryWriter(port)
    app = ProvowareDbTui(port, entry_writer=writer)  # type: ignore[arg-type]
    async with app.run_test(size=(100, 30)) as pilot:
        category_list = app.query_one("#category-list", ListView)
        category_list.index = 0
        await pilot.press("e")
        await pilot.pause()
        entry_input = app.query_one("#entry-create-input", Input)
        assert entry_input.display is True
        assert entry_input.has_focus
        assert app._entry_create_category_id == "cat-a"

        # Prove the write uses the parent captured when the command started.
        category_list.index = 1
        await pilot.press(*"Neu")
        await pilot.press("enter")
        await pilot.pause()

        assert writer.calls == [("cat-a", "Neu")]
        assert port.entry_reads[-1] == "cat-a"
        assert [item.label for item in app._entries] == ["Alt", "Neu"]
        assert category_list.index == 0
        assert category_list.has_focus
        assert entry_input.display is False
        assert app._entry_create_category_id is None
        assert app.read_status == "Eintrag „Neu“ angelegt."


async def _exercise_failure_and_cancel() -> None:
    port = MutablePort()
    writer = EntryWriter(port, fail=True)
    app = ProvowareDbTui(port, entry_writer=writer)  # type: ignore[arg-type]
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.press("e")
        await pilot.press(*"Fehler")
        reads_before = len(port.entry_reads)
        await pilot.press("enter")
        await pilot.pause()

        entry_input = app.query_one("#entry-create-input", Input)
        assert writer.calls == [("cat-a", "Fehler")]
        assert len(port.entry_reads) == reads_before
        assert entry_input.display is True
        assert entry_input.has_focus
        assert app._entry_create_category_id == "cat-a"
        assert app.read_status.startswith("DOM-102:")

        await pilot.press("escape")
        await pilot.pause()
        assert writer.calls == [("cat-a", "Fehler")]
        assert entry_input.display is False
        assert app._entry_create_category_id is None
        assert app.query_one("#category-list", ListView).has_focus
        assert app.read_status == "Eintrag anlegen abgebrochen."


def test_entry_create_is_unavailable_without_writer_and_requires_selection() -> None:
    asyncio.run(_exercise_readonly_and_no_selection())


def test_entry_create_uses_captured_parent_once_and_refreshes_same_category() -> None:
    asyncio.run(_exercise_success_with_captured_parent())


def test_entry_failure_does_not_refresh_and_cancel_does_not_write() -> None:
    asyncio.run(_exercise_failure_and_cancel())


if __name__ == "__main__":
    test_entry_create_is_unavailable_without_writer_and_requires_selection()
    test_entry_create_uses_captured_parent_once_and_refreshes_same_category()
    test_entry_failure_does_not_refresh_and_cancel_does_not_write()
