from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Protocol, Sequence

from provoware_db.field_type_labels import field_type_label
from provoware_db.tui.view_models import EventItem, FieldRow, HealthItem, NavItem


class CatalogReadPort(Protocol):
    def list_categories(self) -> Sequence[object]: ...
    def list_entries(self, category_id: str) -> Sequence[object]: ...
    def list_fields_with_values(self, entry_id: str) -> Sequence[tuple[object, object | Sequence[object] | None]]: ...


class HealthReadPort(Protocol):
    def health(self) -> Sequence[HealthItem]: ...


class EventReadPort(Protocol):
    def recent_events(self, limit: int = 10) -> Sequence[EventItem]: ...


def _format_scalar(value: object, field: object, raw_type: str) -> str:
    text = getattr(value, "value_text", None)
    integer = getattr(value, "value_integer", None)
    real = getattr(value, "value_real", None)
    if text is not None:
        if raw_type == "date":
            rendered = date.fromisoformat(str(text)).strftime("%d.%m.%Y")
        elif raw_type == "datetime":
            rendered = datetime.fromisoformat(str(text)).strftime("%d.%m.%Y, %H:%M")
        elif raw_type == "decimal":
            rendered = str(text).replace(".", ",")
        else:
            rendered = str(text)
    elif integer is not None:
        if raw_type == "boolean":
            rendered = "Ja" if int(integer) else "Nein"
        elif raw_type == "money":
            rendered = f"{Decimal(int(integer)) / Decimal(100):.2f}".replace(".", ",")
            currency = getattr(field, "currency_code", None)
            if currency:
                rendered += f" {currency}"
        else:
            rendered = str(integer)
    elif real is not None:
        rendered = f"{float(real):g}"
    else:
        return "Nicht gesetzt"
    unit = getattr(field, "unit_label", None)
    if unit and raw_type != "money":
        rendered += f" {unit}"
    return rendered


def _format_value(value: object | Sequence[object] | None, field: object, raw_type: str) -> str:
    if value is None:
        return "Nicht gesetzt"
    if raw_type == "single_choice":
        return str(getattr(value, "label", None) or "Nicht gesetzt")
    if raw_type == "multi_choice":
        labels = [str(getattr(item, "label", "")) for item in value]
        return ", ".join(label for label in labels if label) or "Nicht gesetzt"
    return _format_scalar(value, field, raw_type)


class TuiCatalogReadAdapter:
    """Read-only projection from application reads to TUI view models."""

    def __init__(self, catalog: CatalogReadPort, health: HealthReadPort, events: EventReadPort) -> None:
        self._catalog = catalog
        self._health = health
        self._events = events

    def categories(self) -> tuple[NavItem, ...]:
        return tuple(NavItem(str(item.id), str(item.name), f"Revision {item.revision}") for item in self._catalog.list_categories())

    def entries(self, category_id: str) -> tuple[NavItem, ...]:
        return tuple(
            NavItem(str(item.id), f"★ {item.title}" if bool(getattr(item, "is_favorite", False)) else str(item.title), f"Revision {item.revision}")
            for item in self._catalog.list_entries(category_id)
        )

    def fields(self, entry_id: str) -> tuple[FieldRow, ...]:
        rows: list[FieldRow] = []
        for field, value in self._catalog.list_fields_with_values(entry_id):
            raw_type = str(getattr(field.field_type, "value", field.field_type))
            rows.append(FieldRow(str(field.id), str(field.name), _format_value(value, field, raw_type), field_type_label(raw_type), bool(field.is_required), getattr(field, "help_text", None)))
        return tuple(rows)

    def health(self) -> tuple[HealthItem, ...]:
        return tuple(self._health.health())

    def recent_events(self, limit: int = 10) -> tuple[EventItem, ...]:
        return tuple(self._events.recent_events(limit))
