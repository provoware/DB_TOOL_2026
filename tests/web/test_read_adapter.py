from dataclasses import dataclass
from enum import StrEnum

from provoware_db.web.read_adapter import WebCatalogReadAdapter
from provoware_db.web.render import render_page


class Kind(StrEnum):
    TEXT = "text"


@dataclass
class Category:
    id: str
    name: str
    revision: int


@dataclass
class Entry:
    id: str
    title: str
    revision: int
    is_favorite: bool = False


@dataclass
class Field:
    id: str
    name: str
    field_type: Kind
    is_required: bool


class FakeCatalogService:
    def __init__(self):
        self.calls = []

    def list_categories(self):
        self.calls.append(("categories",))
        return [Category("cat-1", "Werkzeug <Pro>", 2)]

    def list_entries(self, category_id):
        self.calls.append(("entries", category_id))
        return [Entry("ent-1", "Akkuschrauber", 3, True)]

    def list_fields(self, entry_id):
        self.calls.append(("fields", entry_id))
        return [Field("fld-1", "Hersteller", Kind.TEXT, True)]


def test_adapter_reads_category_entry_field_chain_from_service():
    service = FakeCatalogService()
    adapter = WebCatalogReadAdapter(service)

    assert adapter.categories()[0].label == "Werkzeug <Pro>"
    assert adapter.entries("cat-1")[0].label == "★ Akkuschrauber"
    assert adapter.fields("ent-1")[0].field_type == "text"
    assert service.calls == [
        ("categories",),
        ("entries", "cat-1"),
        ("fields", "ent-1"),
    ]


def test_render_page_projects_service_data_and_escapes_html():
    service = FakeCatalogService()
    page = render_page(
        WebCatalogReadAdapter(service),
        category_id="cat-1",
        entry_id="ent-1",
    )

    assert "Werkzeug &lt;Pro&gt;" in page
    assert "★ Akkuschrauber" in page
    assert "Hersteller" in page
    assert "text · Pflichtfeld" in page
    assert "Werkzeug <Pro>" not in page


def test_web_adapter_has_no_write_api():
    adapter = WebCatalogReadAdapter(FakeCatalogService())
    for forbidden in (
        "create_category",
        "update_category",
        "trash_category",
        "restore_category",
    ):
        assert not hasattr(adapter, forbidden)
