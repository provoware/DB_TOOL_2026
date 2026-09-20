from __future__ import annotations

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Footer, Label, ListItem, ListView, Static

from .layout_policy import LayoutMode, classify_layout
from .view_models import NavItem, TuiDataPort


class ProvowareDbTui(App[None]):
    """Minimal read-only CP-07T shell.

    The shell depends only on the injected TuiDataPort. It deliberately does
    not import storage, repositories, SQL helpers, or mutation services.
    """

    BINDINGS = [("q", "quit", "Beenden"), ("r", "refresh_categories", "Neu laden")]

    def __init__(self, data_port: TuiDataPort) -> None:
        super().__init__()
        self._data_port = data_port
        self._categories = tuple(data_port.categories())
        self._entries: tuple[NavItem, ...] = ()
        self.read_status = ""
        self.layout_mode = LayoutMode.COMPACT

    def compose(self) -> ComposeResult:
        yield Static("PROVOWARE Datenbank · Nur Lesen", id="title")
        yield ListView(
            *(ListItem(Label(item.label)) for item in self._categories),
            id="category-list",
        )
        yield ListView(id="entry-list")
        yield ListView(id="field-list")
        yield Static(id="read-status")
        yield Static(id="layout-status")
        yield Footer()

    def on_mount(self) -> None:
        category_list = self.query_one("#category-list", ListView)
        if category_list.children:
            category_list.index = 0
        else:
            self._set_read_status("Keine Kategorien vorhanden.")
        category_list.focus()
        self._sync_layout(self.size.width)

    async def action_refresh_categories(self) -> None:
        category_list = self.query_one("#category-list", ListView)
        entry_list = self.query_one("#entry-list", ListView)
        field_list = self.query_one("#field-list", ListView)

        selected_category_id: str | None = None
        selected_index = category_list.index
        if selected_index is not None and selected_index < len(self._categories):
            selected_category_id = self._categories[selected_index].id

        self._categories = tuple(self._data_port.categories())
        self._entries = ()

        await category_list.clear()
        await entry_list.clear()
        await field_list.clear()
        category_list.index = None
        entry_list.index = None
        field_list.index = None

        if self._categories:
            await category_list.extend(
                ListItem(Label(item.label))
                for item in self._categories
            )
            category_list.index = next(
                (
                    index
                    for index, item in enumerate(self._categories)
                    if item.id == selected_category_id
                ),
                0,
            )
            self._set_read_status("Kategorien neu geladen.")
        else:
            self._set_read_status("Keine Kategorien vorhanden.")

        category_list.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "category-list":
            self._select_category(event.list_view)
            return
        if event.list_view.id == "entry-list":
            self._select_entry(event.list_view)

    def _select_category(self, category_list: ListView) -> None:
        index = category_list.index
        if index is None or index >= len(self._categories):
            return

        self._entries = tuple(
            self._data_port.entries(self._categories[index].id)
        )
        entry_list = self.query_one("#entry-list", ListView)
        field_list = self.query_one("#field-list", ListView)
        entry_list.clear()
        field_list.clear()
        entry_list.extend(
            ListItem(Label(item.label))
            for item in self._entries
        )

        if not entry_list.children:
            self._set_read_status("Keine Einträge in dieser Kategorie.")
            category_list.focus()
            return

        self._set_read_status("")
        entry_list.index = 0
        entry_list.focus()

    def _select_entry(self, entry_list: ListView) -> None:
        index = entry_list.index
        if index is None or index >= len(self._entries):
            return

        fields = tuple(self._data_port.fields(self._entries[index].id))
        field_list = self.query_one("#field-list", ListView)
        field_list.clear()
        field_list.extend(
            ListItem(Label(f"{item.label}: {item.value}"))
            for item in fields
        )

        if not field_list.children:
            self._set_read_status("Keine Felder in diesem Eintrag.")
            entry_list.focus()
            return

        self._set_read_status("")
        field_list.index = 0
        field_list.focus()

    def _set_read_status(self, message: str) -> None:
        self.read_status = message
        self.query_one("#read-status", Static).update(message)

    def on_resize(self, event: events.Resize) -> None:
        self._sync_layout(event.size.width)

    def _sync_layout(self, width: int) -> None:
        self.layout_mode = classify_layout(width)
        self.query_one("#layout-status", Static).update(
            f"Layout: {self.layout_mode.value} · Nur-Lese"
        )
