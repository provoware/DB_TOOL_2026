from __future__ import annotations

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Footer, Input, Label, ListItem, ListView, Static

from .layout_policy import LayoutMode, classify_layout
from .view_models import HealthLevel, NavItem, TuiDataPort
from .write_adapter import CategoryWriteAdapter


class ProvowareDbTui(App[None]):
    """CP-07T shell with one optional, narrowly reopened category write path."""

    BINDINGS = [
        ("q", "quit", "Beenden"),
        ("r", "refresh_categories", "Neu laden"),
        ("c", "create_category", "Kategorie anlegen"),
        ("escape", "cancel_category_create", "Abbrechen"),
    ]

    def __init__(
        self,
        data_port: TuiDataPort,
        category_writer: CategoryWriteAdapter | None = None,
    ) -> None:
        super().__init__()
        self._data_port = data_port
        self._category_writer = category_writer
        self._categories = tuple(data_port.categories())
        self._health = tuple(data_port.health())
        event_reader = getattr(data_port, "recent_events")
        self._recent_events = tuple(event_reader(limit=10))[:10]
        self._entries: tuple[NavItem, ...] = ()
        self.read_status = ""
        self.layout_mode = LayoutMode.COMPACT

    def compose(self) -> ComposeResult:
        yield Static("PROVOWARE Datenbank · Nur Lesen", id="title")
        yield Input(placeholder="Kategoriename · Enter bestätigt", id="category-create-input")
        yield ListView(
            *(ListItem(Label(item.label)) for item in self._categories),
            id="category-list",
        )
        yield ListView(id="entry-list")
        yield ListView(id="field-list")
        yield Static(self._health_summary(), id="health-status")
        yield Static(self._event_summary(), id="event-status")
        yield Static(id="read-status")
        yield Static(id="layout-status")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#category-create-input", Input).display = False
        category_list = self.query_one("#category-list", ListView)
        if category_list.children:
            category_list.index = 0
        else:
            self._set_read_status("Keine Kategorien vorhanden.")
        category_list.focus()
        self._sync_layout(self.size.width)

    async def action_create_category(self) -> None:
        if self._category_writer is None:
            self._set_read_status("Kategorie anlegen ist in diesem Modus nicht verfügbar.")
            return
        category_input = self.query_one("#category-create-input", Input)
        category_input.value = ""
        category_input.display = True
        category_input.focus()
        self._set_read_status("Kategoriename eingeben und mit Enter bestätigen. Esc bricht ab.")

    def action_cancel_category_create(self) -> None:
        category_input = self.query_one("#category-create-input", Input)
        if not category_input.display:
            return
        category_input.value = ""
        category_input.display = False
        self._set_read_status("Kategorie anlegen abgebrochen.")
        self.query_one("#category-list", ListView).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "category-create-input" or not event.input.display:
            return
        name = event.value.strip()
        if not name:
            self._set_read_status("Kategoriename darf nicht leer sein.")
            event.input.focus()
            return
        writer = self._category_writer
        if writer is None:
            self.action_cancel_category_create()
            return
        try:
            writer.create_category(name)
        except Exception as exc:
            self._set_read_status(str(exc))
            event.input.focus()
            return

        event.input.value = ""
        event.input.display = False
        await self.action_refresh_categories()
        self._set_read_status(f"Kategorie „{name}“ angelegt.")

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

    def _health_summary(self) -> str:
        if not self._health:
            return "Systemstatus: keine Statusdaten"

        ok_count = sum(item.level is HealthLevel.OK for item in self._health)
        warning_count = sum(item.level is HealthLevel.WARNING for item in self._health)
        error_count = sum(item.level is HealthLevel.ERROR for item in self._health)

        if error_count:
            overall = "ROT"
        elif warning_count:
            overall = "GELB"
        else:
            overall = "GRÜN"

        return (
            f"Systemstatus: {overall}"
            f" · {ok_count} OK"
            f" · {warning_count} Warnung"
            f" · {error_count} Fehler"
        )

    def _event_summary(self) -> str:
        if not self._recent_events:
            return "Letzte Ereignisse: keine Ereignisse vorhanden"
        lines = ["Letzte Ereignisse:"]
        lines.extend(
            f"{item.time_label} · {item.symbol} · {item.text}"
            for item in self._recent_events
        )
        return "\n".join(lines)

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
