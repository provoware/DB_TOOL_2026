from provoware_db.domain.models import Category, Entry, FieldDefinition, FieldScope, FieldType
from provoware_db.domain.rules import assert_field_applies_to_entry


def test_read_models_preserve_normalized_labels_and_revisions():
    category = Category.new("cat-1", "  Werkzeug  ")
    entry = Entry.new("ent-1", category.id, "  Akkuschrauber  ")
    field = FieldDefinition.new(
        id="fld-1",
        scope=FieldScope.CATEGORY,
        category_id=category.id,
        name=" Hersteller ",
        field_type=FieldType.TEXT,
        is_required=True,
    )

    assert category.name == "Werkzeug"
    assert category.revision == 1
    assert entry.title == "Akkuschrauber"
    assert field.name == "Hersteller"
    assert field.field_type is FieldType.TEXT
    assert_field_applies_to_entry(field, entry)


def test_choice_field_types_are_available_for_web_projection():
    assert FieldType.SINGLE_CHOICE.value == "single_choice"
    assert FieldType.MULTI_CHOICE.value == "multi_choice"
