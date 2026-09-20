from __future__ import annotations

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView, Static

from .layout_policy import LayoutMode, classify_layout
from .view_models import TuiDataPort


class ProvowareDbTui(App[None]):
    """Minimal read-only CP-07T shell.

    The shell depends only on the injected TuiDataPort. It deliberately does
    not import storage, repositories, SQL helpers, or mutation services.
    """

    BINDINGS = [("q", "quit", "Beenden")]

    def __init__(self, data_port: TuiDataPort) -> None:
        super().__init__()
        self._data_port = data_port
        self._categories = tuple(data_port.categories())
        self.layout_mode = LayoutMode.COMPACT

    def compose(self) -> ComposeResult:
        yield Static("PROVOWARE Datenbank · Nur Lesen", id="title")
        yield ListView(
            *(ListItem(Label(item.label)) for item in self._categories),
            id="category-list",
        )
        yield ListView(id="entry-list")
        yield Static(id="layout-status")
        yield Footer()

    def on_mount(self) -> None:
        category_list = self.query_one("#category-list", ListView)
        if category_list.children:
            category_list.index = 0
        category_list.focus()
        self._sync_layout(self.size.width)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id != "category-list":
            return

        index = event.list_view.index
        if index is None or index >= len(self._categories):
            return

        entry_list = self.query_one("#entry-list", ListView)
        entry_list.clear()
        entry_list.extend(
            ListItem(Label(item.label))
            for item in self._data_port.entries(self._categories[index].id)
        )
        if entry_list.children:
            entry_list.index = 0
            entry_list.focus()

    def on_resize(self, event: events.Resize) -> None:
        self._sync_layout(event.size.width)

    def _sync_layout(self, width: int) -> None:
        self.layout_mode = classify_layout(width)
        self.query_one("#layout-status", Static).update(
            f"Layout: {self.layout_mode.value} · Nur-Lese"
        )
