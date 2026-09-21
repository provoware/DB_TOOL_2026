from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Protocol, Sequence

from provoware_db.field_type_labels import field_type_label


class CatalogReadPort(Protocol):
    def list_categories(self) -> Sequence[object]: ...
    def list_entries(self, category_id: str) -> Sequence[object]: ...
    def list_fields(self, entry_id: str) -> Sequence[object]: ...
    def list_fields_with_values(self, entry_id: str) -> Sequence[tuple[object, object | Sequence[object] | None]]: ...
    def get_field_value(self, entry_id: str, field_id: str) -> object | Sequence[object] | None: ...
    def search(self, query: str, *, limit: int = 50) -> Sequence[object]: ...


@dataclass(frozen=True)
class WebNavItem:
    id: str
    label: str
    meta: str = ""


@dataclass(frozen=True)
class WebFieldItem:
    id: str
    label: str
    field_type: str
    required: bool
    value: str


@dataclass(frozen=True)
class WebSearchItem:
    entity_type: str
    entity_id: str
    label: str
    kind_label: str
    category_id: str | None
    entry_id: str | None


def _format_scalar(value: object, field: object, raw_type: str) -> str:
    value_text = getattr(value, "value_text", None)
    value_integer = getattr(value, "value_integer", None)
    value_real = getattr(value, "value_real", None)

    if value_text is not None:
        if raw_type == "date":
            rendered = date.fromisoformat(str(value_text)).strftime("%d.%m.%Y")
        elif raw_type == "datetime":
            rendered = datetime.fromisoformat(str(value_text)).strftime("%d.%m.%Y, %H:%M")
        elif raw_type == "decimal":
            rendered = str(value_text).replace(".", ",")
        else:
            rendered = str(value_text)
    elif value_integer is not None:
        if raw_type == "boolean":
            rendered = "Ja" if int(value_integer) else "Nein"
        elif raw_type == "money":
            amount = Decimal(int(value_integer)) / Decimal(100)
            rendered = f"{amount:.2f}".replace(".", ",")
            currency = getattr(field, "currency_code", None)
            if currency:
                rendered += f" {currency}"
        else:
            rendered = str(value_integer)
    elif value_real is not None:
        rendered = f"{float(value_real):g}"
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
        label = getattr(value, "label", None)
        return str(label) if label else "Nicht gesetzt"

    if raw_type == "multi_choice":
        labels = [str(getattr(item, "label", "")) for item in value]
        labels = [label for label in labels if label]
        return ", ".join(labels) if labels else "Nicht gesetzt"

    return _format_scalar(value, field, raw_type)


class WebCatalogReadAdapter:
    """Read-only projection from the application service to web-safe view data."""

    def __init__(self, catalog: CatalogReadPort) -> None:
        self._catalog = catalog

    def categories(self) -> tuple[WebNavItem, ...]:
        return tuple(
            WebNavItem(str(item.id), str(item.name), f"Revision {item.revision}")
            for item in self._catalog.list_categories()
        )

    def entries(self, category_id: str) -> tuple[WebNavItem, ...]:
        return tuple(
            WebNavItem(
                str(item.id),
                f"★ {item.title}" if bool(getattr(item, "is_favorite", False)) else str(item.title),
                f"Revision {item.revision}",
            )
            for item in self._catalog.list_entries(category_id)
        )

    def fields(self, entry_id: str) -> tuple[WebFieldItem, ...]:
        rows: list[WebFieldItem] = []
        for item, value in self._catalog.list_fields_with_values(entry_id):
            raw_type = str(getattr(item.field_type, "value", item.field_type))
            rows.append(
                WebFieldItem(
                    id=str(item.id),
                    label=str(item.name),
                    field_type=field_type_label(raw_type),
                    required=bool(item.is_required),
                    value=_format_value(value, item, raw_type),
                )
            )
        return tuple(rows)

    def search(self, query: str) -> tuple[WebSearchItem, ...]:
        kind_labels = {
            "category": "Kategorie",
            "entry": "Eintrag",
            "field_definition": "Feld",
        }
        return tuple(
            WebSearchItem(
                entity_type=str(item.entity_type),
                entity_id=str(item.entity_id),
                label=str(item.label),
                kind_label=kind_labels.get(str(item.entity_type), str(item.entity_type)),
                category_id=None if item.category_id is None else str(item.category_id),
                entry_id=None if item.entry_id is None else str(item.entry_id),
            )
            for item in self._catalog.search(query)
        )
