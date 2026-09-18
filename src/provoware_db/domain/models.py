from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any

from .errors import ValidationError
from .normalization import clean_text, make_key


class FieldScope(StrEnum):
    CATEGORY = "category"
    ENTRY = "entry"


class FieldType(StrEnum):
    TEXT = "text"
    LONG_TEXT = "long_text"
    INTEGER = "integer"
    DECIMAL = "decimal"
    MONEY = "money"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"


@dataclass(frozen=True)
class Category:
    id: str
    name: str
    name_key: str
    description: str | None = None
    sort_order: int = 0
    revision: int = 1

    @classmethod
    def new(cls, id: str, name: str, description: str | None = None, sort_order: int = 0) -> "Category":
        cleaned = clean_text(name)
        if not 1 <= len(cleaned) <= 120:
            raise ValidationError("VAL-401: Kategoriename muss 1 bis 120 Zeichen enthalten.")
        if sort_order < 0:
            raise ValidationError("VAL-402: Sortierreihenfolge darf nicht negativ sein.")
        return cls(id=id, name=cleaned, name_key=make_key(cleaned), description=description, sort_order=sort_order)


@dataclass(frozen=True)
class Entry:
    id: str
    category_id: str
    title: str
    title_key: str
    is_favorite: bool = False
    sort_order: int = 0
    revision: int = 1

    @classmethod
    def new(cls, id: str, category_id: str, title: str, sort_order: int = 0) -> "Entry":
        cleaned = clean_text(title)
        if not 1 <= len(cleaned) <= 240:
            raise ValidationError("VAL-410: Eintragstitel muss 1 bis 240 Zeichen enthalten.")
        if sort_order < 0:
            raise ValidationError("VAL-411: Sortierreihenfolge darf nicht negativ sein.")
        return cls(id=id, category_id=category_id, title=cleaned, title_key=make_key(cleaned), sort_order=sort_order)


@dataclass(frozen=True)
class FieldDefinition:
    id: str
    scope: FieldScope
    name: str
    name_key: str
    field_type: FieldType
    category_id: str | None = None
    entry_id: str | None = None
    is_required: bool = False
    sort_order: int = 0
    help_text: str | None = None
    placeholder: str | None = None
    unit_label: str | None = None
    currency_code: str | None = None
    revision: int = 1

    @classmethod
    def new(
        cls,
        *,
        id: str,
        scope: FieldScope,
        name: str,
        field_type: FieldType,
        category_id: str | None = None,
        entry_id: str | None = None,
        is_required: bool = False,
        sort_order: int = 0,
        help_text: str | None = None,
        placeholder: str | None = None,
        unit_label: str | None = None,
        currency_code: str | None = None,
    ) -> "FieldDefinition":
        cleaned = clean_text(name)
        if not 1 <= len(cleaned) <= 120:
            raise ValidationError("VAL-420: Feldname muss 1 bis 120 Zeichen enthalten.")
        if sort_order < 0:
            raise ValidationError("VAL-421: Sortierreihenfolge darf nicht negativ sein.")
        if scope is FieldScope.CATEGORY and (not category_id or entry_id is not None):
            raise ValidationError("VAL-422: Kategorie-Feld benötigt genau eine category_id.")
        if scope is FieldScope.ENTRY and (not entry_id or category_id is not None):
            raise ValidationError("VAL-423: Eintrags-Feld benötigt genau eine entry_id.")
        normalized_currency = currency_code.upper() if currency_code else None
        if field_type is FieldType.MONEY:
            if normalized_currency is None or len(normalized_currency) != 3:
                raise ValidationError("VAL-424: Geldfelder benötigen einen dreistelligen Währungscode.")
        elif normalized_currency is not None:
            raise ValidationError("VAL-425: Währungscode ist nur für Geldfelder erlaubt.")
        return cls(
            id=id, scope=scope, name=cleaned, name_key=make_key(cleaned), field_type=field_type,
            category_id=category_id, entry_id=entry_id, is_required=is_required, sort_order=sort_order,
            help_text=help_text, placeholder=placeholder, unit_label=unit_label, currency_code=normalized_currency,
        )


@dataclass(frozen=True)
class ScalarValue:
    value_kind: str
    value_text: str | None = None
    value_integer: int | None = None
    value_real: float | None = None

    @classmethod
    def from_input(cls, field_type: FieldType, value: Any) -> "ScalarValue":
        if field_type in (FieldType.SINGLE_CHOICE, FieldType.MULTI_CHOICE):
            raise ValidationError("VAL-430: Auswahlfelder benötigen das Auswahl-Repository.")
        if field_type in (FieldType.TEXT, FieldType.LONG_TEXT):
            if not isinstance(value, str):
                raise ValidationError("VAL-431: Textfeld erwartet Text.")
            return cls("text", value_text=value)
        if field_type is FieldType.INTEGER:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValidationError("VAL-432: Ganzzahlfeld erwartet eine Ganzzahl.")
            return cls("integer", value_integer=value)
        if field_type is FieldType.DECIMAL:
            try:
                dec = Decimal(str(value))
            except (InvalidOperation, ValueError) as exc:
                raise ValidationError("VAL-433: Dezimalfeld enthält keine gültige Zahl.") from exc
            if not dec.is_finite():
                raise ValidationError("VAL-434: Dezimalwert muss endlich sein.")
            return cls("decimal_text", value_text=format(dec.normalize(), "f"))
        if field_type is FieldType.MONEY:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValidationError("VAL-435: Geld wird intern als ganze kleinste Währungseinheit gespeichert.")
            return cls("money_minor", value_integer=value)
        if field_type is FieldType.DATE:
            if not isinstance(value, str):
                raise ValidationError("VAL-436: Datum muss ISO-Text YYYY-MM-DD sein.")
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise ValidationError("VAL-436: Datum muss ISO-Text YYYY-MM-DD sein.") from exc
            return cls("date", value_text=value)
        if field_type is FieldType.DATETIME:
            if not isinstance(value, str):
                raise ValidationError("VAL-437: Datum/Zeit muss gültiger ISO-Text sein.")
            try:
                datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValidationError("VAL-437: Datum/Zeit muss gültiger ISO-Text sein.") from exc
            return cls("datetime", value_text=value)
        if field_type is FieldType.BOOLEAN:
            if not isinstance(value, bool):
                raise ValidationError("VAL-438: Ja/Nein-Feld erwartet True oder False.")
            return cls("boolean", value_integer=int(value))
        raise ValidationError(f"VAL-439: Nicht unterstützter Feldtyp {field_type}.")


@dataclass(frozen=True)
class FieldOption:
    id: str
    field_definition_id: str
    label: str
    option_key: str
    sort_order: int = 0

    @classmethod
    def new(cls, id: str, field_definition_id: str, label: str, sort_order: int = 0) -> "FieldOption":
        cleaned = clean_text(label)
        if not 1 <= len(cleaned) <= 120:
            raise ValidationError("VAL-450: Auswahlbezeichnung muss 1 bis 120 Zeichen enthalten.")
        if sort_order < 0:
            raise ValidationError("VAL-451: Sortierreihenfolge darf nicht negativ sein.")
        return cls(id=id, field_definition_id=field_definition_id, label=cleaned, option_key=make_key(cleaned), sort_order=sort_order)


@dataclass(frozen=True)
class SearchHit:
    entity_type: str
    entity_id: str
    label: str
    category_id: str | None = None
    entry_id: str | None = None
