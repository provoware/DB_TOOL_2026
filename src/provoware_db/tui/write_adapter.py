from __future__ import annotations

from typing import Protocol

from provoware_db.domain.models import Category

from .view_models import NavItem


class CategoryCreateService(Protocol):
    def create_category(self, name: str, *, description: str | None = None, sort_order: int = 0) -> Category: ...


class CategoryWriteAdapter:
    """Thin TUI write boundary for the frozen CatalogService contract."""

    def __init__(self, service: CategoryCreateService) -> None:
        self._service = service

    def create_category(self, name: str) -> NavItem:
        category = self._service.create_category(name)
        return NavItem(category.id, category.name)
