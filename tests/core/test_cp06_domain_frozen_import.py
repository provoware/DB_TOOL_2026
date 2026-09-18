from __future__ import annotations

import hashlib
from pathlib import Path

from provoware_db.domain.models import Category, Entry, FieldDefinition, FieldScope, FieldType
from provoware_db.domain.rules import assert_field_applies_to_entry


ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    "src/provoware_db/domain/errors.py": "c06c0b021d2dbe984cbc31478ec6123c7bfdfaefd78558f44a5acbf52e6bf60e",
    "src/provoware_db/domain/models.py": "bd55a189c0db1f8944e28bbeff1709e9044e06dd56962cddc8b951a0bcfeffa4",
    "src/provoware_db/domain/normalization.py": "771aecdedfad390be06da2bd4c34628ae65ce3764b88269f64fb11ab0c4bce47",
    "src/provoware_db/domain/rules.py": "7f4c3142e5b70df6058e3fdcbe507b82f1e4ddfe4fdb8eb25cfd7418e62f6022",
}


def test_imported_cp06_domain_files_are_byte_exact():
    for relative, expected in EXPECTED.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected, relative


def test_read_domain_objects_and_scope_rule_work():
    category = Category.new("cat_1", "  Werkzeug  ")
    entry = Entry.new("ent_1", category.id, "Akkuschrauber")
    field = FieldDefinition.new(
        id="fld_1",
        scope=FieldScope.CATEGORY,
        category_id=category.id,
        name="Hersteller",
        field_type=FieldType.TEXT,
    )

    assert category.name == "Werkzeug"
    assert category.name_key == "werkzeug"
    assert entry.title == "Akkuschrauber"
    assert_field_applies_to_entry(field, entry)
