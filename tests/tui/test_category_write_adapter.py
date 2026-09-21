from __future__ import annotations

from provoware_db.domain.errors import ConflictError
from provoware_db.domain.models import Category
from provoware_db.tui.write_adapter import CategoryWriteAdapter


class FakeCategoryService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None, int]] = []

    def create_category(self, name: str, *, description: str | None = None, sort_order: int = 0) -> Category:
        self.calls.append((name, description, sort_order))
        return Category.new("cat-new", name, description, sort_order)


class ConflictCategoryService(FakeCategoryService):
    def create_category(self, name: str, *, description: str | None = None, sort_order: int = 0) -> Category:
        self.calls.append((name, description, sort_order))
        raise ConflictError("DOM-201: Eine aktive Kategorie mit diesem Namen existiert bereits.")


def test_adapter_delegates_exactly_once_and_maps_result() -> None:
    service = FakeCategoryService()
    adapter = CategoryWriteAdapter(service)

    result = adapter.create_category("Werkstatt")

    assert service.calls == [("Werkstatt", None, 0)]
    assert result.id == "cat-new"
    assert result.label == "Werkstatt"


def test_adapter_preserves_catalog_conflict_contract() -> None:
    service = ConflictCategoryService()
    adapter = CategoryWriteAdapter(service)

    try:
        adapter.create_category("Werkstatt")
    except ConflictError as exc:
        assert str(exc).startswith("DOM-201:")
    else:
        raise AssertionError("ConflictError muss unverändert bis zur UI-Grenze gelangen")

    assert service.calls == [("Werkstatt", None, 0)]


if __name__ == "__main__":
    test_adapter_delegates_exactly_once_and_maps_result()
    test_adapter_preserves_catalog_conflict_contract()
