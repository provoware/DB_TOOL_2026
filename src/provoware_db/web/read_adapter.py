from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


class CatalogReadPort(Protocol):
    def list_categories(self) -> Sequence[object]: ...
    def list_entries(self, category_id: str) -> Sequence[object]: ...
    def list_fields(self, entry_id: str) -> Sequence[object]: ...


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
        for item in self._catalog.list_fields(entry_id):
            raw_type = item.field_type
            field_type = str(getattr(raw_type, "value", raw_type))
            rows.append(
                WebFieldItem(
                    id=str(item.id),
                    label=str(item.name),
                    field_type=field_type,
                    required=bool(item.is_required),
                )
            )
        return tuple(rows)
