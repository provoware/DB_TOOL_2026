from __future__ import annotations

import asyncio
from typing import Sequence

from textual.widgets import Input, ListView

from provoware_db.tui.runtime import ProvowareDbTui
from provoware_db.tui.view_models import EventItem, FieldRow, HealthItem, NavItem


class MutablePort:
    def __init__(self) -> None:
        self.items = [NavItem("cat-a", "Kategorie A")]
        self.category_reads = 0

    def categories(self) -> Sequence[NavItem]:
        self.category_reads += 1
        return tuple(self.items)

    def entries(self, category_id: str) -> Sequence[NavItem]:
        return ()

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        return ()

    def health(self) -> Sequence[HealthItem]:
        return ()

    def recent_events(self, limit: int = 10) -> Sequence[EventItem]:
        return ()


class Writer:
    def __init__(self, port: MutablePort, *, fail: bool = False) -> None:
        self.port = port
        self.fail = fail
        self.calls: list[str] = []

    def create_category(self, name: str) -> NavItem:
        self.calls.append(name)
        if self.fail:
            raise RuntimeError("DOM-201: Kategorie existiert bereits.")
        item = NavItem(f"cat-{len(self.port.items) + 1}", name)
        self.port.items.append(item)
        return item


async def _exercise_readonly_mode() -> None:
    port = MutablePort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.press("c")
        await pilot.pause()
        category_input = app.query_one("#category-create-input", Input)
        assert category_input.display is False
        assert "nicht verfügbar" in app.read_status
        assert app.query_one("#category-list", ListView).has_focus


async def _exercise_success() -> None:
    port = MutablePort()
    writer = Writer(port)
    app = ProvowareDbTui(port, writer)  # type: ignore[arg-type]
    async with app.run_test(size=(80, 24)) as pilot:
        assert port.category_reads == 1
        await pilot.press("c")
        await pilot.pause()
        category_input = app.query_one("#category-create-input", Input)
        assert category_input.display is True
        assert category_input.has_focus

        await pilot.press(*"Werkstatt")
        await pilot.press("enter")
        await pilot.pause()

        assert writer.calls == ["Werkstatt"]
        assert port.category_reads == 2
        assert category_input.display is False
        assert [item.label for item in app._categories] == ["Kategorie A", "Werkstatt"]
        assert app.query_one("#category-list", ListView).has_focus
        assert app.read_status == "Kategorie „Werkstatt“ angelegt."


async def _exercise_conflict_and_cancel() -> None:
    port = MutablePort()
    writer = Writer(port, fail=True)
    app = ProvowareDbTui(port, writer)  # type: ignore[arg-type]
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.press("c")
        await pilot.press(*"Kategorie A")
        await pilot.press("enter")
        await pilot.pause()

        category_input = app.query_one("#category-create-input", Input)
        assert writer.calls == ["Kategorie A"]
        assert port.category_reads == 1
        assert category_input.display is True
        assert category_input.has_focus
        assert app.read_status.startswith("DOM-201:")

        await pilot.press("escape")
        await pilot.pause()
        assert writer.calls == ["Kategorie A"]
        assert category_input.display is False
        assert app.query_one("#category-list", ListView).has_focus
        assert app.read_status == "Kategorie anlegen abgebrochen."


def test_readonly_construction_keeps_write_capability_unavailable() -> None:
    asyncio.run(_exercise_readonly_mode())


def test_confirmed_category_calls_writer_once_and_reuses_refresh() -> None:
    asyncio.run(_exercise_success())


def test_conflict_does_not_refresh_and_cancel_does_not_write() -> None:
    asyncio.run(_exercise_conflict_and_cancel())


if __name__ == "__main__":
    test_readonly_construction_keeps_write_capability_unavailable()
    test_confirmed_category_calls_writer_once_and_reuses_refresh()
    test_conflict_does_not_refresh_and_cancel_does_not_write()
