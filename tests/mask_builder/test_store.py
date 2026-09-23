from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from provoware_db.domain.models import FieldType
from provoware_db.mask_builder.model import (
    LayoutBox,
    MaskElement,
    MaskElementKind,
    MaskFieldSpec,
    MaskTemplate,
    MaskValidationError,
)
from provoware_db.mask_builder.store import (
    MaskTemplateStore,
    TemplateStoreConflict,
    TemplateStoreError,
)


def _template(version: int = 1) -> MaskTemplate:
    return MaskTemplate(
        id="contact_card",
        name="Kontaktkarte",
        version=version,
        fields=(MaskFieldSpec("name", "Name", FieldType.TEXT, is_required=True),),
        elements=(
            MaskElement("field-name", MaskElementKind.FIELD, LayoutBox(0, 0, 12, 2), field_key="name"),
        ),
    )


def test_atomic_roundtrip_and_listing() -> None:
    with TemporaryDirectory() as tmp:
        store = MaskTemplateStore(Path(tmp))
        target = store.save(_template())
        assert target.is_file()
        assert store.load("contact_card") == _template()
        assert store.list_templates() == (_template(),)
        assert list(Path(tmp).glob(".*.tmp")) == []


def test_updates_require_known_monotonic_version() -> None:
    with TemporaryDirectory() as tmp:
        store = MaskTemplateStore(Path(tmp))
        store.save(_template(1))

        try:
            store.save(_template(2))
        except TemplateStoreConflict as exc:
            assert str(exc).startswith("STORE-409:")
        else:
            raise AssertionError("overwrite without expected version must fail")

        store.save(_template(2), expected_current_version=1)
        assert store.load("contact_card").version == 2

        try:
            store.save(_template(3), expected_current_version=1)
        except TemplateStoreConflict as exc:
            assert str(exc).startswith("STORE-410:")
        else:
            raise AssertionError("stale expected version must fail")


def test_corrupt_file_is_fail_closed() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        root.mkdir(exist_ok=True)
        (root / "contact_card.json").write_text("{broken", encoding="utf-8")
        store = MaskTemplateStore(root)
        try:
            store.load("contact_card")
        except TemplateStoreError as exc:
            assert str(exc).startswith("STORE-422:")
        else:
            raise AssertionError("corrupt template must fail closed")


def test_invalid_update_never_replaces_last_valid_template() -> None:
    with TemporaryDirectory() as tmp:
        store = MaskTemplateStore(Path(tmp))
        store.save(_template(1))
        invalid = replace(
            _template(2),
            elements=(
                MaskElement("a", MaskElementKind.FIELD, LayoutBox(0, 0, 12, 2), field_key="name"),
                MaskElement("b", MaskElementKind.NOTE, LayoutBox(0, 0, 12, 1), title="Kollision"),
            ),
        )
        try:
            store.save(invalid, expected_current_version=1)
        except MaskValidationError:
            pass
        else:
            raise AssertionError("invalid template must fail before file replacement")
        assert store.load("contact_card").version == 1


def test_filename_identity_is_checked() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        store = MaskTemplateStore(root)
        path = store.save(_template())
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["id"] = "other"
        path.write_text(json.dumps(payload), encoding="utf-8")
        try:
            store.load("contact_card")
        except TemplateStoreError as exc:
            assert str(exc).startswith("STORE-423:")
        else:
            raise AssertionError("file/template id mismatch must fail")


if __name__ == "__main__":
    test_atomic_roundtrip_and_listing()
    test_updates_require_known_monotonic_version()
    test_corrupt_file_is_fail_closed()
    test_invalid_update_never_replaces_last_valid_template()
    test_filename_identity_is_checked()
