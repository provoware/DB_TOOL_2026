from types import SimpleNamespace

from provoware_db.domain.models import FieldType, ScalarValue
from provoware_db.tui.read_adapter import TuiCatalogReadAdapter
from provoware_db.tui.view_models import EventItem, HealthItem, HealthLevel


class CatalogFake:
    def list_categories(self):
        return [SimpleNamespace(id="cat-1", name="Musik", revision=2)]

    def list_entries(self, category_id):
        assert category_id == "cat-1"
        return [SimpleNamespace(id="ent-1", title="Track", is_favorite=True, revision=3)]

    def list_fields_with_values(self, entry_id):
        assert entry_id == "ent-1"
        field = SimpleNamespace(id="fld-1", name="BPM", field_type=FieldType.INTEGER, is_required=True, help_text="Tempo", unit_label="BPM", currency_code=None)
        return [(field, ScalarValue("integer", value_integer=180))]


class HealthFake:
    item = HealthItem("Datenbank", HealthLevel.OK, "bereit")

    def health(self):
        return [self.item]


class EventFake:
    item = EventItem("12:00", "+", "Eintrag gelesen")

    def __init__(self):
        self.limit = None

    def recent_events(self, limit=10):
        self.limit = limit
        return [self.item]


def test_projects_catalog_navigation_and_field_values():
    adapter = TuiCatalogReadAdapter(CatalogFake(), HealthFake(), EventFake())
    assert adapter.categories()[0].label == "Musik"
    assert adapter.entries("cat-1")[0].label == "★ Track"
    field = adapter.fields("ent-1")[0]
    assert (field.label, field.value, field.field_type, field.required, field.help_text) == ("BPM", "180 BPM", "Ganzzahl", True, "Tempo")


def test_health_and_events_are_delegated_without_new_semantics():
    health = HealthFake()
    events = EventFake()
    adapter = TuiCatalogReadAdapter(CatalogFake(), health, events)
    assert adapter.health() == (health.item,)
    assert adapter.recent_events(4) == (events.item,)
    assert events.limit == 4
