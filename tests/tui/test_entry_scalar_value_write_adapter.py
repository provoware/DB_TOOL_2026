from __future__ import annotations

from provoware_db.domain.errors import ValidationError
from provoware_db.domain.models import ScalarValue
from provoware_db.tui.write_adapter import EntryScalarValueWriteAdapter


class FakeScalarValueService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, object]] = []
        self.result = ScalarValue("text", value_text="Inventarnummer 42")

    def set_scalar_value(self, entry_id: str, field_id: str, value: object) -> ScalarValue:
        self.calls.append((entry_id, field_id, value))
        return self.result


class RejectingScalarValueService(FakeScalarValueService):
    def set_scalar_value(self, entry_id: str, field_id: str, value: object) -> ScalarValue:
        self.calls.append((entry_id, field_id, value))
        raise ValidationError("VAL-432: Ganzzahlfeld erwartet eine Ganzzahl.")


def test_adapter_delegates_once_without_changing_inputs_and_returns_same_value() -> None:
    service = FakeScalarValueService()
    adapter = EntryScalarValueWriteAdapter(service)
    raw_value = {"domain": "opaque"}

    result = adapter.set_scalar_value("ent-selected", "fld-selected", raw_value)

    assert len(service.calls) == 1
    entry_id, field_id, forwarded_value = service.calls[0]
    assert entry_id == "ent-selected"
    assert field_id == "fld-selected"
    assert forwarded_value is raw_value
    assert result is service.result


def test_adapter_preserves_validation_error_contract() -> None:
    service = RejectingScalarValueService()
    adapter = EntryScalarValueWriteAdapter(service)

    try:
        adapter.set_scalar_value("ent-selected", "fld-integer", "kein integer")
    except ValidationError as exc:
        assert str(exc).startswith("VAL-432:")
    else:
        raise AssertionError("ValidationError muss unverändert bis zur Adapter-Grenze gelangen")

    assert service.calls == [
        ("ent-selected", "fld-integer", "kein integer"),
    ]


if __name__ == "__main__":
    test_adapter_delegates_once_without_changing_inputs_and_returns_same_value()
    test_adapter_preserves_validation_error_contract()
