from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Sequence

from textual.widgets import ListView

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
        return ()

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        return ()

    def health(self) -> Sequence[HealthItem]:
        return ()

    def recent_events(self, limit: int = 10) -> Sequence[EventItem]:
        return ()


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


async def _exercise_large_viewport() -> None:
    app = ProvowareDbTui(FakePort())
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        assert app.layout_mode is LayoutMode.WIDE
        assert app.query_one("#category-list", ListView).has_focus


def test_compact_viewport_navigation_and_focus() -> None:
    asyncio.run(_exercise_compact_navigation())


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
    test_large_viewport_layout_and_focus()
    test_runtime_has_no_storage_or_sql_imports()
