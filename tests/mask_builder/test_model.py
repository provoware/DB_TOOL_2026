from dataclasses import replace

from provoware_db.domain.models import FieldType
from provoware_db.mask_builder.model import (
    LayoutBox,
    MaskElement,
    MaskElementKind,
    MaskFieldSpec,
    MaskTemplate,
    MaskValidationError,
    build_application_plan,
    template_from_dict,
    template_to_dict,
    validate_template,
)


def _template() -> MaskTemplate:
    return MaskTemplate(
        id="contact_card",
        name="Kontaktkarte",
        version=1,
        fields=(
            MaskFieldSpec("name", "Name", FieldType.TEXT, is_required=True, placeholder="Vor- und Nachname"),
            MaskFieldSpec("rating", "Bewertung", FieldType.INTEGER, unit_label="Punkte"),
        ),
        elements=(
            MaskElement("heading", MaskElementKind.HEADING, LayoutBox(0, 0, 12, 1), title="Kontakt"),
            MaskElement("field-name", MaskElementKind.FIELD, LayoutBox(0, 1, 6, 2), field_key="name"),
            MaskElement("field-rating", MaskElementKind.FIELD, LayoutBox(6, 1, 6, 2), field_key="rating"),
            MaskElement("note", MaskElementKind.NOTE, LayoutBox(0, 3, 12, 1), title="Pflichtfelder zuerst ausfüllen."),
        ),
    )


def test_valid_template_builds_deterministic_plan() -> None:
    template = _template()
    assert validate_template(template) == ()

    plan = build_application_plan(template, "Ada")
    assert plan.template_id == "contact_card"
    assert plan.template_version == 1
    assert plan.entry_title == "Ada"
    assert [(field.key, field.sort_order) for field in plan.fields] == [("name", 0), ("rating", 1)]


def test_overlap_and_duplicate_binding_are_rejected() -> None:
    template = _template()
    duplicate = MaskElement("field-name-2", MaskElementKind.FIELD, LayoutBox(0, 1, 4, 2), field_key="name")
    broken = replace(template, elements=template.elements + (duplicate,))
    codes = {issue.code for issue in validate_template(broken)}
    assert "MASK-126" in codes
    assert "MASK-130" in codes


def test_unbound_and_unknown_fields_are_rejected() -> None:
    template = _template()
    unknown = MaskElement("unknown", MaskElementKind.FIELD, LayoutBox(0, 5, 6, 2), field_key="missing")
    broken = replace(
        template,
        elements=tuple(item for item in template.elements if item.field_key != "rating") + (unknown,),
    )
    codes = {issue.code for issue in validate_template(broken)}
    assert "MASK-125" in codes
    assert "MASK-129" in codes


def test_grid_bounds_are_fail_closed() -> None:
    template = _template()
    outside = replace(template.elements[1], box=LayoutBox(11, 1, 2, 1))
    broken = replace(template, elements=(template.elements[0], outside, *template.elements[2:]))
    assert "MASK-123" in {issue.code for issue in validate_template(broken)}


def test_json_contract_roundtrips_and_rejects_unknown_schema() -> None:
    template = _template()
    payload = template_to_dict(template)
    assert template_from_dict(payload) == template

    payload["schema_version"] = 99
    try:
        template_from_dict(payload)
    except MaskValidationError as exc:
        assert exc.issues[0].code == "MASK-190"
    else:
        raise AssertionError("unknown template schema must fail closed")


if __name__ == "__main__":
    test_valid_template_builds_deterministic_plan()
    test_overlap_and_duplicate_binding_are_rejected()
    test_unbound_and_unknown_fields_are_rejected()
    test_grid_bounds_are_fail_closed()
    test_json_contract_roundtrips_and_rejects_unknown_schema()
