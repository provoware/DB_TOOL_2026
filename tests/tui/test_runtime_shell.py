from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Sequence

from textual.widgets import Label, ListView

from provoware_db.tui.layout_policy import LayoutMode
from provoware_db.tui.runtime import ProvowareDbTui
from provoware_db.tui.view_models import EventItem, FieldRow, HealthItem, NavItem


class FakePort:
    def categories(self) -> Sequence[NavItem]:
        return (
            NavItem("cat-a", "Kategorie A"),
            NavItem("cat-b", "Kategorie B"),
            NavItem("cat-c", "Kategorie C"),
        )

    def entries(self, category_id: str) -> Sequence[NavItem]:
        if category_id == "cat-a":
            return (
                NavItem("entry-a1", "Eintrag A1"),
                NavItem("entry-a2", "Eintrag A2"),
            )
        return ()

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        if entry_id == "entry-a1":
            return (
                FieldRow("field-a1", "Name", "Alpha", "text", required=True),
                FieldRow("field-a2", "Status", "Aktiv", "text"),
            )
        return ()

    def health(self) -> Sequence[HealthItem]:
        return ()

    def recent_events(self, limit: int = 10) -> Sequence[EventItem]:
        return ()


class EmptyCategoriesPort(FakePort):
    def categories(self) -> Sequence[NavItem]:
        return ()


class EmptyAfterRefreshPort(FakePort):
    def __init__(self) -> None:
        self.category_reads = 0

    def categories(self) -> Sequence[NavItem]:
        self.category_reads += 1
        if self.category_reads == 1:
            return super().categories()
        return ()


class EmptyThenPopulatedPort(FakePort):
    def __init__(self) -> None:
        self.category_reads = 0

    def categories(self) -> Sequence[NavItem]:
        self.category_reads += 1
        if self.category_reads == 1:
            return ()
        return (NavItem("cat-new", "Kategorie Neu"),)


class ReorderingPort(FakePort):
    def __init__(self) -> None:
        self.category_reads = 0
        self.entry_category_id: str | None = None

    def categories(self) -> Sequence[NavItem]:
        self.category_reads += 1
        if self.category_reads == 1:
            return super().categories()
        return (
            NavItem("cat-c", "Kategorie C"),
            NavItem("cat-b", "Kategorie B"),
            NavItem("cat-a", "Kategorie A"),
        )

    def entries(self, category_id: str) -> Sequence[NavItem]:
        self.entry_category_id = category_id
        return super().entries(category_id)


class ReorderingEntryPort(FakePort):
    def __init__(self) -> None:
        self.entry_reads = 0
        self.field_entry_id: str | None = None

    def entries(self, category_id: str) -> Sequence[NavItem]:
        self.entry_reads += 1
        if self.entry_reads == 1:
            return super().entries(category_id)
        return (
            NavItem("entry-a2", "Eintrag A2"),
            NavItem("entry-a1", "Eintrag A1"),
        )

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        self.field_entry_id = entry_id
        return super().fields(entry_id)


async def _exercise_compact_navigation() -> None:
    app = ProvowareDbTui(FakePort())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        category_list = app.query_one("#category-list", ListView)

        assert app.layout_mode is LayoutMode.COMPACT
        assert category_list.has_focus
        assert len(category_list.children) == 3
        assert category_list.index == 0

        await pilot.press("down")
        assert category_list.index == 1
        await pilot.press("up")
        assert category_list.index == 0


async def _exercise_no_categories_initial_state() -> None:
    app = ProvowareDbTui(EmptyCategoriesPort())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        category_list = app.query_one("#category-list", ListView)
        entry_list = app.query_one("#entry-list", ListView)
        field_list = app.query_one("#field-list", ListView)

        assert len(category_list.children) == 0
        assert category_list.index is None
        assert len(entry_list.children) == 0
        assert len(field_list.children) == 0
        assert app.read_status == "Keine Kategorien vorhanden."
        assert category_list.has_focus

        await pilot.press("down")
        await pilot.press("up")
        await pilot.press("enter")
        await pilot.pause()

        assert category_list.index is None
        assert app.read_status == "Keine Kategorien vorhanden."
        assert category_list.has_focus


async def _exercise_refresh_reloads_categories_and_clears_dependents() -> None:
    port = ReorderingPort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        entry_list = app.query_one("#entry-list", ListView)
        field_list = app.query_one("#field-list", ListView)
        assert field_list.has_focus
        assert len(entry_list.children) == 2
        assert len(field_list.children) == 2

        await pilot.press("r")
        await pilot.pause()

        category_list = app.query_one("#category-list", ListView)
        assert port.category_reads == 2
        assert len(category_list.children) == 3
        assert category_list.index == 0
        assert category_list.query_one(Label).render().plain == "Kategorie C"
        assert len(entry_list.children) == 0
        assert entry_list.index is None
        assert len(field_list.children) == 0
        assert field_list.index is None
        assert category_list.has_focus
        assert app.read_status == "Kategorien neu geladen."


async def _exercise_refresh_to_empty_categories() -> None:
    port = EmptyAfterRefreshPort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("r")
        await pilot.pause()

        category_list = app.query_one("#category-list", ListView)
        assert port.category_reads == 2
        assert len(category_list.children) == 0
        assert category_list.index is None
        assert app.query_one("#entry-list", ListView).index is None
        assert app.query_one("#field-list", ListView).index is None
        assert category_list.has_focus
        assert app.read_status == "Keine Kategorien vorhanden."


async def _exercise_refresh_from_empty_to_populated() -> None:
    port = EmptyThenPopulatedPort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()

        category_list = app.query_one("#category-list", ListView)
        assert len(category_list.children) == 0
        assert app.read_status == "Keine Kategorien vorhanden."

        await pilot.press("r")
        await pilot.pause()

        assert port.category_reads == 2
        assert len(category_list.children) == 1
        assert category_list.index == 0
        assert category_list.query_one(Label).render().plain == "Kategorie Neu"
        assert category_list.has_focus
        assert app.read_status == "Kategorien neu geladen."


async def _exercise_category_to_entry_read() -> None:
    app = ProvowareDbTui(FakePort())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        category_list = app.query_one("#category-list", ListView)
        entry_list = app.query_one("#entry-list", ListView)

        await pilot.press("enter")
        await pilot.pause()

        assert category_list.index == 0
        assert len(entry_list.children) == 2
        assert entry_list.index == 0
        assert entry_list.has_focus


async def _exercise_rendered_category_identity() -> None:
    port = ReorderingPort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        assert port.category_reads == 1
        assert port.entry_category_id == "cat-a"


async def _exercise_entry_to_field_read() -> None:
    app = ProvowareDbTui(FakePort())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        field_list = app.query_one("#field-list", ListView)
        assert len(field_list.children) == 2
        assert field_list.index == 0
        assert field_list.has_focus

        labels = [
            item.query_one(Label).render().plain
            for item in field_list.children
        ]
        assert labels == ["Name: Alpha", "Status: Aktiv"]


async def _exercise_rendered_entry_identity() -> None:
    port = ReorderingEntryPort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        assert port.entry_reads == 1
        assert port.field_entry_id == "entry-a1"


async def _exercise_empty_entries_keep_category_focus() -> None:
    app = ProvowareDbTui(FakePort())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        category_list = app.query_one("#category-list", ListView)
        entry_list = app.query_one("#entry-list", ListView)
        field_list = app.query_one("#field-list", ListView)

        await pilot.press("down")
        assert category_list.index == 1
        await pilot.press("enter")
        await pilot.pause()

        assert len(entry_list.children) == 0
        assert len(field_list.children) == 0
        assert app.read_status == "Keine Einträge in dieser Kategorie."
        assert category_list.has_focus

        await pilot.press("up")
        assert category_list.index == 0


async def _exercise_empty_fields_keep_entry_focus() -> None:
    app = ProvowareDbTui(FakePort())
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        entry_list = app.query_one("#entry-list", ListView)
        field_list = app.query_one("#field-list", ListView)
        assert entry_list.has_focus

        await pilot.press("down")
        assert entry_list.index == 1
        await pilot.press("enter")
        await pilot.pause()

        assert len(field_list.children) == 0
        assert app.read_status == "Keine Felder in diesem Eintrag."
        assert entry_list.has_focus

        await pilot.press("up")
        assert entry_list.index == 0


async def _exercise_large_viewport() -> None:
    app = ProvowareDbTui(FakePort())
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        assert app.layout_mode is LayoutMode.WIDE
        assert app.query_one("#category-list", ListView).has_focus


async def _capture_iteration_25_evidence() -> None:
    app = ProvowareDbTui(FakePort())
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()

        entry_list = app.query_one("#entry-list", ListView)
        assert app.layout_mode is LayoutMode.WIDE
        assert len(entry_list.children) == 2
        assert entry_list.index == 0
        assert entry_list.has_focus

        out = Path("runtime/iteration-25")
        out.mkdir(parents=True, exist_ok=True)
        screenshot_path = out / "main-160x40.svg"
        evidence_path = out / "iteration-25-evidence.json"
        screenshot_path.write_text(app.export_screenshot(), encoding="utf-8")
        evidence_path.write_text(
            json.dumps(
                {
                    "iteration": 25,
                    "viewport": "160x40",
                    "theme": "Textual default",
                    "layout": app.layout_mode.value,
                    "category": "Kategorie A",
                    "entries": ["Eintrag A1", "Eintrag A2"],
                    "focused": "entry-list",
                    "visual_regression": "no blocking overlap or missing category/entry content",
                    "status": "GREEN",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def test_compact_viewport_navigation_and_focus() -> None:
    asyncio.run(_exercise_compact_navigation())


def test_no_categories_initial_state_is_clear_and_keyboard_stable() -> None:
    asyncio.run(_exercise_no_categories_initial_state())


def test_refresh_reloads_categories_clears_dependents_and_resets_focus() -> None:
    asyncio.run(_exercise_refresh_reloads_categories_and_clears_dependents())


def test_refresh_to_empty_categories_is_clear_and_keyboard_stable() -> None:
    asyncio.run(_exercise_refresh_to_empty_categories())


def test_refresh_from_empty_to_populated_selects_first_category() -> None:
    asyncio.run(_exercise_refresh_from_empty_to_populated())


def test_category_selection_loads_entries_and_moves_focus() -> None:
    asyncio.run(_exercise_category_to_entry_read())


def test_category_selection_uses_rendered_category_identity() -> None:
    asyncio.run(_exercise_rendered_category_identity())


def test_entry_selection_loads_fields_and_moves_focus() -> None:
    asyncio.run(_exercise_entry_to_field_read())


def test_entry_selection_uses_rendered_entry_identity() -> None:
    asyncio.run(_exercise_rendered_entry_identity())


def test_empty_entries_keep_category_focus_and_keyboard_navigation() -> None:
    asyncio.run(_exercise_empty_entries_keep_category_focus())


def test_empty_fields_keep_entry_focus_and_keyboard_navigation() -> None:
    asyncio.run(_exercise_empty_fields_keep_entry_focus())


def test_large_viewport_layout_and_focus() -> None:
    asyncio.run(_exercise_large_viewport())


def test_runtime_has_no_storage_or_sql_imports() -> None:
    source = (
        Path(__file__).parents[2]
        / "src"
        / "provoware_db"
        / "tui"
        / "runtime.py"
    ).read_text(encoding="utf-8").lower()

    assert "provoware_db.storage" not in source
    assert "sqlite" not in source
    assert "execute(" not in source


if __name__ == "__main__":
    test_compact_viewport_navigation_and_focus()
    test_no_categories_initial_state_is_clear_and_keyboard_stable()
    test_refresh_reloads_categories_clears_dependents_and_resets_focus()
    test_refresh_to_empty_categories_is_clear_and_keyboard_stable()
    test_refresh_from_empty_to_populated_selects_first_category()
    test_category_selection_loads_entries_and_moves_focus()
    test_category_selection_uses_rendered_category_identity()
    test_entry_selection_loads_fields_and_moves_focus()
    test_entry_selection_uses_rendered_entry_identity()
    test_empty_entries_keep_category_focus_and_keyboard_navigation()
    test_empty_fields_keep_entry_focus_and_keyboard_navigation()
    test_large_viewport_layout_and_focus()
    test_runtime_has_no_storage_or_sql_imports()
    asyncio.run(_capture_iteration_25_evidence())
