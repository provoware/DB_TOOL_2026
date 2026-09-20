from __future__ import annotations

import asyncio
from typing import Sequence

from textual.widgets import ListView, Static

from provoware_db.tui.runtime import ProvowareDbTui
from provoware_db.tui.view_models import EventItem, FieldRow, HealthItem, NavItem


class EventPort:
    def __init__(self, events: Sequence[EventItem]) -> None:
        self.events = tuple(events)
        self.event_reads = 0
        self.event_limit: int | None = None
        self.health_reads = 0

    def categories(self) -> Sequence[NavItem]:
        return (NavItem("cat-a", "Kategorie A"),)

    def entries(self, category_id: str) -> Sequence[NavItem]:
        return ()

    def fields(self, entry_id: str) -> Sequence[FieldRow]:
        return ()

    def health(self) -> Sequence[HealthItem]:
        self.health_reads += 1
        return ()

    def recent_events(self, limit: int = 10) -> Sequence[EventItem]:
        self.event_reads += 1
        self.event_limit = limit
        return self.events


async def _exercise_event_surface() -> None:
    events = tuple(
        EventItem(f"12:{index:02d}", "·", f"Ereignis {index}")
        for index in range(12)
    )
    port = EventPort(events)
    app = ProvowareDbTui(port)
    async with app.run_test(size=(160, 40)) as pilot:
        await pilot.pause()
        surface = app.query_one("#event-status", Static)
        rendered = surface.render().plain
        category_list = app.query_one("#category-list", ListView)

        assert port.event_reads == 1
        assert port.event_limit == 10
        assert port.health_reads == 1
        assert surface.can_focus is False
        assert category_list.has_focus
        assert rendered.startswith("Letzte Ereignisse:\n")
        assert "Ereignis 0" in rendered
        assert "Ereignis 9" in rendered
        assert "Ereignis 10" not in rendered

        await pilot.press("r")
        await pilot.pause()
        assert port.event_reads == 1
        assert port.health_reads == 1
        assert category_list.has_focus


async def _exercise_empty_event_surface() -> None:
    port = EventPort(())
    app = ProvowareDbTui(port)
    async with app.run_test(size=(80, 24)) as pilot:
        await pilot.pause()
        surface = app.query_one("#event-status", Static)
        category_list = app.query_one("#category-list", ListView)

        assert port.event_reads == 1
        assert port.event_limit == 10
        assert surface.render().plain == "Letzte Ereignisse: keine Ereignisse vorhanden"
        assert surface.can_focus is False
        assert category_list.has_focus


def test_recent_events_are_single_read_limited_and_non_focusable() -> None:
    asyncio.run(_exercise_event_surface())


def test_empty_recent_events_state_is_clear_and_keyboard_stable() -> None:
    asyncio.run(_exercise_empty_event_surface())
