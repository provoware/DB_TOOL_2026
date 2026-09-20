from __future__ import annotations

import asyncio
from typing import Sequence

from textual.widgets import Label, ListView

from provoware_db.tui.runtime import ProvowareDbTui
from provoware_db.tui.view_models import EventItem, FieldRow, HealthItem, NavItem


class RefreshPort:
    def __init__(self) -> None:
        self.category_reads = 0

    def categories(self) -> Sequence[NavItem]:
        self.category_reads += 1
        if self.category_reads == 1:
            return (NavItem("cat-old", "Alt"),)
        if self.category_reads == 2:
            return (
                NavItem("cat-new-a", "Neu A"),
                NavItem("cat-new-b", "Neu B"),
            )
        return ()

    def entries(self, category_id: str) -> Sequence[NavItem]:
        if category_id == "cat-old":
            return (NavItem("entry-old", "Alter Eintrag"),)
        return ()

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        if entry_id == "entry-old":
            return (FieldRow("field-old", "Name", "Alt", "text"),)
        return ()

    def health(self) -> Sequence[HealthItem]:
        return ()

    def recent_events(self, limit: int = 10) -> Sequence[EventItem]:
        return ()


async def _exercise_refresh() -> None:
    port = RefreshPort()
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        category_list = app.query_one("#category-list", ListView)
        entry_list = app.query_one("#entry-list", ListView)
        field_list = app.query_one("#field-list", ListView)

        await pilot.press("enter")
        await pilot.pause()
        await pilot.press("enter")
        await pilot.pause()
        assert len(entry_list.children) == 1
        assert len(field_list.children) == 1

        await pilot.press("r")
        await pilot.pause()

        labels = [item.query_one(Label).render().plain for item in category_list.children]
        assert labels == ["Neu A", "Neu B"]
        assert category_list.index == 0
        assert category_list.has_focus
        assert len(entry_list.children) == 0
        assert len(field_list.children) == 0
        assert app.read_status == "Kategorien neu geladen."

        await pilot.press("r")
        await pilot.pause()

        assert len(category_list.children) == 0
        assert category_list.index is None
        assert category_list.has_focus
        assert len(entry_list.children) == 0
        assert len(field_list.children) == 0
        assert app.read_status == "Keine Kategorien vorhanden."
        assert port.category_reads == 3


def test_category_refresh_reloads_and_clears_dependent_views() -> None:
    asyncio.run(_exercise_refresh())


if __name__ == "__main__":
    test_category_refresh_reloads_and_clears_dependent_views()
