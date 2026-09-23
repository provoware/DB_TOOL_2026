from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Any

from provoware_db.domain.models import FieldType


GRID_COLUMNS = 12
MAX_GRID_ROWS = 1000
_TEMPLATE_SCHEMA_VERSION = 1
_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


class MaskElementKind(StrEnum):
    FIELD = "field"
    HEADING = "heading"
    SECTION = "section"
    NOTE = "note"
    SEPARATOR = "separator"


@dataclass(frozen=True)
class LayoutBox:
    x: int
    y: int
    width: int
    height: int

    def overlaps(self, other: "LayoutBox") -> bool:
        return not (
            self.x + self.width <= other.x
            or other.x + other.width <= self.x
            or self.y + self.height <= other.y
            or other.y + other.height <= self.y
        )


@dataclass(frozen=True)
class MaskFieldSpec:
    key: str
    label: str
    field_type: FieldType
    is_required: bool = False
    help_text: str | None = None
    placeholder: str | None = None
    unit_label: str | None = None
    currency_code: str | None = None
    options: tuple[str, ...] = ()


@dataclass(frozen=True)
class MaskElement:
    id: str
    kind: MaskElementKind
    box: LayoutBox
    title: str = ""
    field_key: str | None = None


@dataclass(frozen=True)
class MaskTemplate:
    id: str
    name: str
    version: int
    fields: tuple[MaskFieldSpec, ...]
    elements: tuple[MaskElement, ...]
    description: str | None = None
    grid_columns: int = GRID_COLUMNS


@dataclass(frozen=True)
class MaskIssue:
    code: str
    message: str
    element_id: str | None = None


class MaskValidationError(ValueError):
    def __init__(self, issues: tuple[MaskIssue, ...]) -> None:
        self.issues = issues
        super().__init__("; ".join(f"{item.code}: {item.message}" for item in issues))


@dataclass(frozen=True)
class ApplicationFieldPlan:
    key: str
    label: str
    field_type: FieldType
    is_required: bool
    sort_order: int
    help_text: str | None = None
    placeholder: str | None = None
    unit_label: str | None = None
    currency_code: str | None = None
    options: tuple[str, ...] = ()


@dataclass(frozen=True)
class TemplateApplicationPlan:
    template_id: str
    template_version: int
    entry_title: str
    fields: tuple[ApplicationFieldPlan, ...]


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def validate_template(template: MaskTemplate) -> tuple[MaskIssue, ...]:
    issues: list[MaskIssue] = []

    if not _ID_RE.fullmatch(template.id):
        issues.append(MaskIssue("MASK-101", "Vorlagen-ID enthält unzulässige Zeichen."))
    if not 1 <= len(template.name.strip()) <= 120:
        issues.append(MaskIssue("MASK-102", "Vorlagenname muss 1 bis 120 Zeichen enthalten."))
    if template.version < 1:
        issues.append(MaskIssue("MASK-103", "Vorlagenversion muss mindestens 1 sein."))
    if template.grid_columns != GRID_COLUMNS:
        issues.append(MaskIssue("MASK-104", "Das Layout muss das feste 12-Spalten-Raster verwenden."))
    if not template.fields:
        issues.append(MaskIssue("MASK-105", "Eine Datenbankmaske benötigt mindestens ein Eingabefeld."))

    field_by_key: dict[str, MaskFieldSpec] = {}
    for field in template.fields:
        if not _KEY_RE.fullmatch(field.key):
            issues.append(MaskIssue("MASK-110", f"Feldschlüssel '{field.key}' ist ungültig."))
        if field.key in field_by_key:
            issues.append(MaskIssue("MASK-111", f"Feldschlüssel '{field.key}' ist doppelt vorhanden."))
        else:
            field_by_key[field.key] = field

        if not 1 <= len(field.label.strip()) <= 120:
            issues.append(MaskIssue("MASK-112", f"Feld '{field.key}' benötigt einen Titel mit 1 bis 120 Zeichen."))

        currency = _clean_optional(field.currency_code)
        if field.field_type is FieldType.MONEY:
            if currency is None or len(currency) != 3 or not currency.isalpha():
                issues.append(MaskIssue("MASK-113", f"Geldfeld '{field.key}' benötigt einen dreistelligen Währungscode."))
        elif currency is not None:
            issues.append(MaskIssue("MASK-114", f"Nur Geldfelder dürfen einen Währungscode besitzen: '{field.key}'."))

        if field.field_type in (FieldType.SINGLE_CHOICE, FieldType.MULTI_CHOICE):
            normalized = [item.strip() for item in field.options]
            if not normalized or any(not item for item in normalized):
                issues.append(MaskIssue("MASK-115", f"Auswahlfeld '{field.key}' benötigt ausschließlich nicht-leere Optionen."))
            if len({item.casefold() for item in normalized}) != len(normalized):
                issues.append(MaskIssue("MASK-116", f"Auswahlfeld '{field.key}' enthält doppelte Optionen."))
        elif field.options:
            issues.append(MaskIssue("MASK-117", f"Nur Auswahlfelder dürfen Optionen besitzen: '{field.key}'."))

    element_ids: set[str] = set()
    field_bindings: dict[str, str] = {}
    for element in template.elements:
        if not _ID_RE.fullmatch(element.id):
            issues.append(MaskIssue("MASK-120", "Element-ID enthält unzulässige Zeichen.", element.id))
        if element.id in element_ids:
            issues.append(MaskIssue("MASK-121", "Element-ID ist doppelt vorhanden.", element.id))
        element_ids.add(element.id)

        box = element.box
        if min(box.x, box.y) < 0 or min(box.width, box.height) < 1:
            issues.append(MaskIssue("MASK-122", "Position und Größe müssen positive Rasterwerte besitzen.", element.id))
        elif box.x + box.width > GRID_COLUMNS or box.y + box.height > MAX_GRID_ROWS:
            issues.append(MaskIssue("MASK-123", "Element liegt außerhalb des zulässigen Rasters.", element.id))

        if element.kind is MaskElementKind.FIELD:
            if not element.field_key:
                issues.append(MaskIssue("MASK-124", "Eingabefeld benötigt eine Feldbindung.", element.id))
            elif element.field_key not in field_by_key:
                issues.append(MaskIssue("MASK-125", f"Feldbindung '{element.field_key}' existiert nicht.", element.id))
            elif element.field_key in field_bindings:
                issues.append(MaskIssue("MASK-126", f"Feld '{element.field_key}' ist mehrfach im Layout gebunden.", element.id))
            else:
                field_bindings[element.field_key] = element.id
        elif element.field_key is not None:
            issues.append(MaskIssue("MASK-127", "Nur Eingabefelder dürfen eine Feldbindung besitzen.", element.id))

        if element.kind in (MaskElementKind.HEADING, MaskElementKind.SECTION, MaskElementKind.NOTE):
            if not element.title.strip():
                issues.append(MaskIssue("MASK-128", "Dieses Hilfselement benötigt sichtbaren Text.", element.id))

    for field_key in field_by_key:
        if field_key not in field_bindings:
            issues.append(MaskIssue("MASK-129", f"Feld '{field_key}' ist noch nicht im Layout platziert."))

    for index, left in enumerate(template.elements):
        for right in template.elements[index + 1 :]:
            if left.box.overlaps(right.box):
                issues.append(MaskIssue("MASK-130", f"Elemente '{left.id}' und '{right.id}' überlappen sich.", left.id))

    return tuple(issues)


def require_valid_template(template: MaskTemplate) -> None:
    issues = validate_template(template)
    if issues:
        raise MaskValidationError(issues)


def build_application_plan(template: MaskTemplate, entry_title: str) -> TemplateApplicationPlan:
    require_valid_template(template)
    cleaned_title = entry_title.strip()
    if not 1 <= len(cleaned_title) <= 240:
        raise MaskValidationError((MaskIssue("MASK-201", "Eintragstitel muss 1 bis 240 Zeichen enthalten."),))

    fields = {field.key: field for field in template.fields}
    field_elements = sorted(
        (element for element in template.elements if element.kind is MaskElementKind.FIELD),
        key=lambda item: (item.box.y, item.box.x, item.id),
    )
    planned = tuple(
        ApplicationFieldPlan(
            key=fields[element.field_key].key,
            label=fields[element.field_key].label,
            field_type=fields[element.field_key].field_type,
            is_required=fields[element.field_key].is_required,
            sort_order=index,
            help_text=fields[element.field_key].help_text,
            placeholder=fields[element.field_key].placeholder,
            unit_label=fields[element.field_key].unit_label,
            currency_code=fields[element.field_key].currency_code,
            options=fields[element.field_key].options,
        )
        for index, element in enumerate(field_elements)
        if element.field_key is not None
    )
    return TemplateApplicationPlan(template.id, template.version, cleaned_title, planned)


def template_to_dict(template: MaskTemplate) -> dict[str, Any]:
    require_valid_template(template)
    return {
        "schema_version": _TEMPLATE_SCHEMA_VERSION,
        "id": template.id,
        "name": template.name.strip(),
        "description": _clean_optional(template.description),
        "version": template.version,
        "grid_columns": template.grid_columns,
        "fields": [
            {
                "key": field.key,
                "label": field.label.strip(),
                "field_type": field.field_type.value,
                "is_required": field.is_required,
                "help_text": _clean_optional(field.help_text),
                "placeholder": _clean_optional(field.placeholder),
                "unit_label": _clean_optional(field.unit_label),
                "currency_code": _clean_optional(field.currency_code.upper() if field.currency_code else None),
                "options": list(field.options),
            }
            for field in template.fields
        ],
        "elements": [
            {
                "id": element.id,
                "kind": element.kind.value,
                "title": element.title.strip(),
                "field_key": element.field_key,
                "box": {
                    "x": element.box.x,
                    "y": element.box.y,
                    "width": element.box.width,
                    "height": element.box.height,
                },
            }
            for element in template.elements
        ],
    }


def template_from_dict(data: dict[str, Any]) -> MaskTemplate:
    try:
        if data.get("schema_version") != _TEMPLATE_SCHEMA_VERSION:
            raise ValueError("unbekannte schema_version")
        raw_fields = data["fields"]
        for item in raw_fields:
            raw_required = item.get("is_required", False)
            if type(raw_required) is not bool:
                raise ValueError("is_required muss ein JSON-Boolean sein")
        fields = tuple(
            MaskFieldSpec(
                key=str(item["key"]),
                label=str(item["label"]),
                field_type=FieldType(str(item["field_type"])),
                is_required=item.get("is_required", False),
                help_text=item.get("help_text"),
                placeholder=item.get("placeholder"),
                unit_label=item.get("unit_label"),
                currency_code=item.get("currency_code"),
                options=tuple(str(option) for option in item.get("options", [])),
            )
            for item in raw_fields
        )
        elements = tuple(
            MaskElement(
                id=str(item["id"]),
                kind=MaskElementKind(str(item["kind"])),
                title=str(item.get("title", "")),
                field_key=item.get("field_key"),
                box=LayoutBox(
                    x=int(item["box"]["x"]),
                    y=int(item["box"]["y"]),
                    width=int(item["box"]["width"]),
                    height=int(item["box"]["height"]),
                ),
            )
            for item in data["elements"]
        )
        template = MaskTemplate(
            id=str(data["id"]),
            name=str(data["name"]),
            description=data.get("description"),
            version=int(data["version"]),
            grid_columns=int(data.get("grid_columns", GRID_COLUMNS)),
            fields=fields,
            elements=elements,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise MaskValidationError((MaskIssue("MASK-190", f"Vorlagendatei ist unvollständig oder inkompatibel: {exc}"),)) from exc

    require_valid_template(template)
    return template
