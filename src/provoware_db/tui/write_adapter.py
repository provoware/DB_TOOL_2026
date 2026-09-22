from __future__ import annotations

from typing import Any, Protocol

from provoware_db.domain.models import Category, Entry, FieldDefinition, FieldType, ScalarValue

from .view_models import NavItem


class CategoryCreateService(Protocol):
    def create_category(self, name: str, *, description: str | None = None, sort_order: int = 0) -> Category: ...


class EntryCreateService(Protocol):
    def create_entry(self, category_id: str, title: str, *, sort_order: int = 0) -> Entry: ...


class EntryFieldCreateService(Protocol):
    def create_entry_field(self, entry_id: str, name: str, field_type: FieldType) -> FieldDefinition: ...


class EntryScalarValueWriteService(Protocol):
    def set_scalar_value(self, entry_id: str, field_id: str, value: Any) -> ScalarValue: ...


class CategoryWriteAdapter:
    """Thin TUI write boundary for the frozen CatalogService contract."""

    def __init__(self, service: CategoryCreateService) -> None:
        self._service = service

    def create_category(self, name: str) -> NavItem:
        category = self._service.create_category(name)
        return NavItem(category.id, category.name)


class EntryWriteAdapter:
    """Thin TUI write boundary for the frozen CatalogService entry contract."""

    def __init__(self, service: EntryCreateService) -> None:
        self._service = service

    def create_entry(self, category_id: str, title: str) -> NavItem:
        entry = self._service.create_entry(category_id, title)
        return NavItem(entry.id, entry.title)


class EntryFieldWriteAdapter:
    """Thin TUI write boundary for the frozen CatalogService entry-field contract."""

    def __init__(self, service: EntryFieldCreateService) -> None:
        self._service = service

    def create_entry_field(self, entry_id: str, name: str, field_type: FieldType) -> FieldDefinition:
        return self._service.create_entry_field(entry_id, name, field_type)


class EntryScalarValueWriteAdapter:
    """Thin TUI write boundary for the existing scalar-value service contract."""

    def __init__(self, service: EntryScalarValueWriteService) -> None:
        self._service = service

    def set_scalar_value(self, entry_id: str, field_id: str, value: Any) -> ScalarValue:
        return self._service.set_scalar_value(entry_id, field_id, value)
