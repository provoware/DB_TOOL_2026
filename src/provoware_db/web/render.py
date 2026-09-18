from __future__ import annotations

from html import escape
from pathlib import Path

from .read_adapter import WebCatalogReadAdapter, WebFieldItem, WebNavItem


_TEMPLATE = Path(__file__).with_name("templates") / "index.html"


def _nav_markup(items: tuple[WebNavItem, ...], empty_text: str) -> str:
    if not items:
        return f'<p class="placeholder">{escape(empty_text)}</p>'
    rows: list[str] = []
    for item in items:
        rows.append(
            '<button type="button" class="data-row" '
            f'data-id="{escape(item.id, quote=True)}">'
            f'<strong>{escape(item.label)}</strong>'
            f'<span>{escape(item.meta)}</span></button>'
        )
    return "".join(rows)


def _field_markup(items: tuple[WebFieldItem, ...]) -> str:
    if not items:
        return '<p class="placeholder">Keine Felder vorhanden.</p>'
    rows: list[str] = []
    for item in items:
        required = " · Pflichtfeld" if item.required else ""
        rows.append(
            '<div class="data-row field-row" '
            f'data-id="{escape(item.id, quote=True)}">'
            f'<strong>{escape(item.label)}</strong>'
            f'<span>{escape(item.field_type + required)}</span></div>'
        )
    return "".join(rows)


def render_page(
    adapter: WebCatalogReadAdapter,
    *,
    category_id: str | None = None,
    entry_id: str | None = None,
) -> str:
    """Render the read-only three-stage page without database access."""
    template = _TEMPLATE.read_text(encoding="utf-8")
    categories = adapter.categories()
    entries = adapter.entries(category_id) if category_id else ()
    fields = adapter.fields(entry_id) if entry_id else ()

    return (
        template.replace(
            "<!-- CATEGORIES -->",
            _nav_markup(categories, "Keine Kategorien vorhanden."),
        )
        .replace(
            "<!-- ENTRIES -->",
            _nav_markup(entries, "Bitte zuerst eine Kategorie wählen."),
        )
        .replace("<!-- FIELDS -->", _field_markup(fields))
    )
