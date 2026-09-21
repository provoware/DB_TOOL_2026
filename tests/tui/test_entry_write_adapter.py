from __future__ import annotations

from provoware_db.domain.errors import NotFoundError
from provoware_db.domain.models import Entry
from provoware_db.tui.write_adapter import EntryWriteAdapter


class FakeEntryService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, int]] = []

    def create_entry(self, category_id: str, title: str, *, sort_order: int = 0) -> Entry:
        self.calls.append((category_id, title, sort_order))
        return Entry.new("ent-new", category_id, title, sort_order)


class MissingCategoryService(FakeEntryService):
    def create_entry(self, category_id: str, title: str, *, sort_order: int = 0) -> Entry:
        self.calls.append((category_id, title, sort_order))
        raise NotFoundError("DOM-102: Kategorie wurde nicht gefunden oder liegt im Papierkorb.")


def test_adapter_delegates_exactly_once_with_explicit_parent_and_maps_result() -> None:
    service = FakeEntryService()
    adapter = EntryWriteAdapter(service)

    result = adapter.create_entry("cat-selected", "Werkbank")

    assert service.calls == [("cat-selected", "Werkbank", 0)]
    assert result.id == "ent-new"
    assert result.label == "Werkbank"


def test_adapter_preserves_missing_parent_contract() -> None:
    service = MissingCategoryService()
    adapter = EntryWriteAdapter(service)

    try:
        adapter.create_entry("cat-missing", "Werkbank")
    except NotFoundError as exc:
        assert str(exc).startswith("DOM-102:")
    else:
        raise AssertionError("NotFoundError muss unverändert bis zur UI-Grenze gelangen")

    assert service.calls == [("cat-missing", "Werkbank", 0)]


if __name__ == "__main__":
    test_adapter_delegates_exactly_once_with_explicit_parent_and_maps_result()
    test_adapter_preserves_missing_parent_contract()
