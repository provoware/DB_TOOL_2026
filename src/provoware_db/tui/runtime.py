from __future__ import annotations

from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Footer, Input, Label, ListItem, ListView, Static

from .layout_policy import LayoutMode, classify_layout
from provoware_db.domain.models import FieldType

from .view_models import HealthLevel, NavItem, TuiDataPort
from .write_adapter import CategoryWriteAdapter, EntryFieldWriteAdapter, EntryWriteAdapter


_FIELD_CREATE_TYPES = (
    (FieldType.TEXT, "Text"),
    (FieldType.LONG_TEXT, "Langer Text"),
    (FieldType.INTEGER, "Ganzzahl"),
    (FieldType.DECIMAL, "Dezimalzahl"),
    (FieldType.DATE, "Datum"),
    (FieldType.DATETIME, "Datum und Uhrzeit"),
    (FieldType.BOOLEAN, "Ja / Nein"),
)


class ProvowareDbTui(App[None]):
    """CP-07T shell with narrowly reopened category, entry and field-create paths."""

    BINDINGS = [
        ("q", "quit", "Beenden"),
        ("r", "refresh_categories", "Neu laden"),
        ("c", "create_category", "Kategorie anlegen"),
        ("e", "create_entry", "Eintrag anlegen"),
        ("f", "create_field", "Feld anlegen"),
        ("escape", "cancel_create", "Abbrechen"),
    ]

    def __init__(
        self,
        data_port: TuiDataPort,
        category_writer: CategoryWriteAdapter | None = None,
        entry_writer: EntryWriteAdapter | None = None,
        field_writer: EntryFieldWriteAdapter | None = None,
    ) -> None:
        super().__init__()
        self._data_port = data_port
        self._category_writer = category_writer
        self._entry_writer = entry_writer
        self._field_writer = field_writer
        self._entry_create_category_id: str | None = None
        self._field_create_entry_id: str | None = None
        self._field_create_type: FieldType | None = None
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
        yield Input(placeholder="Eintragsname · Enter bestätigt", id="entry-create-input")
        yield ListView(
            *(ListItem(Label(label)) for _, label in _FIELD_CREATE_TYPES),
            id="field-type-list",
        )
        yield Input(placeholder="Feldname · Enter bestätigt", id="field-create-input")
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
        self.query_one("#entry-create-input", Input).display = False
        self.query_one("#field-type-list", ListView).display = False
        self.query_one("#field-create-input", Input).display = False
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

    async def action_create_entry(self) -> None:
        if self._entry_writer is None:
            self._set_read_status("Eintrag anlegen ist in diesem Modus nicht verfügbar.")
            return
        category_list = self.query_one("#category-list", ListView)
        index = category_list.index
        if index is None or index >= len(self._categories):
            self._set_read_status("Bitte zuerst eine Kategorie auswählen.")
            category_list.focus()
            return
        self._entry_create_category_id = self._categories[index].id
        entry_input = self.query_one("#entry-create-input", Input)
        entry_input.value = ""
        entry_input.display = True
        entry_input.focus()
        self._set_read_status("Eintragsname eingeben und mit Enter bestätigen. Esc bricht ab.")

    async def action_create_field(self) -> None:
        if self._field_writer is None:
            self._set_read_status("Feld anlegen ist in diesem Modus nicht verfügbar.")
            return
        entry_list = self.query_one("#entry-list", ListView)
        index = entry_list.index
        if index is None or index >= len(self._entries):
            self._set_read_status("Bitte zuerst einen Eintrag auswählen.")
            entry_list.focus()
            return

        self._field_create_entry_id = self._entries[index].id
        self._field_create_type = None

        type_list = self.query_one("#field-type-list", ListView)
        type_list.index = 0
        type_list.display = True
        type_list.focus()

        field_input = self.query_one("#field-create-input", Input)
        field_input.value = ""
        field_input.display = False
        self._set_read_status("Feldtyp auswählen und mit Enter bestätigen. Esc bricht ab.")

    def action_cancel_create(self) -> None:
        category_input = self.query_one("#category-create-input", Input)
        entry_input = self.query_one("#entry-create-input", Input)
        field_type_list = self.query_one("#field-type-list", ListView)
        field_input = self.query_one("#field-create-input", Input)
        if category_input.display:
            category_input.value = ""
            category_input.display = False
            self._set_read_status("Kategorie anlegen abgebrochen.")
            self.query_one("#category-list", ListView).focus()
            return
        if entry_input.display:
            entry_input.value = ""
            entry_input.display = False
            self._entry_create_category_id = None
            self._set_read_status("Eintrag anlegen abgebrochen.")
            self.query_one("#category-list", ListView).focus()
            return
        if field_type_list.display or field_input.display:
            entry_id = self._field_create_entry_id
            field_type_list.display = False
            field_input.value = ""
            field_input.display = False
            self._field_create_entry_id = None
            self._field_create_type = None
            self._set_read_status("Feld anlegen abgebrochen.")
            self._focus_entry(entry_id)

    def action_cancel_category_create(self) -> None:
        """Compatibility action retained for the frozen I42 contract."""
        self.action_cancel_create()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "category-create-input" and event.input.display:
            await self._submit_category(event)
            return
        if event.input.id == "entry-create-input" and event.input.display:
            await self._submit_entry(event)
            return
        if event.input.id == "field-create-input" and event.input.display:
            await self._submit_field(event)

    async def _submit_category(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        if not name:
            self._set_read_status("Kategoriename darf nicht leer sein.")
            event.input.focus()
            return
        writer = self._category_writer
        if writer is None:
            self.action_cancel_create()
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

    async def _submit_entry(self, event: Input.Submitted) -> None:
        title = event.value.strip()
        if not title:
            self._set_read_status("Eintragsname darf nicht leer sein.")
            event.input.focus()
            return
        writer = self._entry_writer
        category_id = self._entry_create_category_id
        if writer is None or category_id is None:
            self.action_cancel_create()
            return
        try:
            writer.create_entry(category_id, title)
        except Exception as exc:
            self._set_read_status(str(exc))
            event.input.focus()
            return

        event.input.value = ""
        event.input.display = False
        self._entry_create_category_id = None
        await self._refresh_entries_for_category(category_id)
        self._set_read_status(f"Eintrag „{title}“ angelegt.")

    async def _submit_field(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        if not name:
            self._set_read_status("Feldname darf nicht leer sein.")
            event.input.focus()
            return

        writer = self._field_writer
        entry_id = self._field_create_entry_id
        field_type = self._field_create_type
        if writer is None or entry_id is None or field_type is None:
            self.action_cancel_create()
            return

        try:
            writer.create_entry_field(entry_id, name, field_type)
        except Exception as exc:
            self._set_read_status(str(exc))
            event.input.focus()
            return

        event.input.value = ""
        event.input.display = False
        self._field_create_entry_id = None
        self._field_create_type = None
        await self._refresh_fields_for_entry(entry_id)
        self._set_read_status(f"Feld „{name}“ angelegt.")

    async def _refresh_fields_for_entry(self, entry_id: str) -> None:
        entry_list = self.query_one("#entry-list", ListView)
        field_list = self.query_one("#field-list", ListView)
        entry_index = next(
            (index for index, item in enumerate(self._entries) if item.id == entry_id),
            None,
        )
        fields = tuple(self._data_port.fields(entry_id))

        await field_list.clear()
        field_list.index = None
        await field_list.extend(
            ListItem(Label(f"{item.label}: {item.value}"))
            for item in fields
        )

        if entry_index is not None:
            entry_list.index = entry_index

        if field_list.children:
            field_list.index = 0
            field_list.focus()
        else:
            entry_list.focus()

    def _focus_entry(self, entry_id: str | None) -> None:
        entry_list = self.query_one("#entry-list", ListView)
        if entry_id is not None:
            entry_index = next(
                (index for index, item in enumerate(self._entries) if item.id == entry_id),
                None,
            )
            if entry_index is not None:
                entry_list.index = entry_index
        entry_list.focus()

    async def _refresh_entries_for_category(self, category_id: str) -> None:
        category_list = self.query_one("#category-list", ListView)
        entry_list = self.query_one("#entry-list", ListView)
        field_list = self.query_one("#field-list", ListView)
        category_index = next(
            (index for index, item in enumerate(self._categories) if item.id == category_id),
            None,
        )
        self._entries = tuple(self._data_port.entries(category_id))
        await entry_list.clear()
        await field_list.clear()
        entry_list.index = None
        field_list.index = None
        await entry_list.extend(ListItem(Label(item.label)) for item in self._entries)
        if category_index is not None:
            category_list.index = category_index
        category_list.focus()

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
        if event.list_view.id == "field-type-list":
            index = event.list_view.index
            if index is None or index >= len(_FIELD_CREATE_TYPES):
                return
            self._field_create_type = _FIELD_CREATE_TYPES[index][0]
            event.list_view.display = False
            field_input = self.query_one("#field-create-input", Input)
            field_input.value = ""
            field_input.display = True
            field_input.focus()
            self._set_read_status("Feldname eingeben und mit Enter bestätigen. Esc bricht ab.")
            return
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
