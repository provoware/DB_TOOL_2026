from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import urlencode

from .read_adapter import WebCatalogReadAdapter, WebFieldItem, WebNavItem, WebSearchItem


_TEMPLATE = Path(__file__).with_name("templates") / "index.html"


def _nav_markup(
    items: tuple[WebNavItem, ...],
    empty_text: str,
    *,
    param_name: str,
    category_id: str | None = None,
    selected_id: str | None = None,
) -> str:
    if not items:
        return f'<p class="placeholder">{escape(empty_text)}</p>'

    rows: list[str] = []
    for item in items:
        params: dict[str, str] = {}
        if category_id:
            params["category_id"] = category_id
        params[param_name] = item.id
        query = urlencode(params)
        selected = item.id == selected_id
        current = ' aria-current="true"' if selected else ""
        selected_label = '<span>✓ Ausgewählt · </span>' if selected else ""

        rows.append(
            f'<form method="get" action="/?{escape(query, quote=True)}">'
            f'<input type="hidden" name="{escape(param_name, quote=True)}" '
            f'value="{escape(item.id, quote=True)}">'
            + (
                f'<input type="hidden" name="category_id" value="{escape(category_id, quote=True)}">'
                if category_id and param_name != "category_id"
                else ""
            )
            + '<button type="submit" class="data-row" '
            f'data-id="{escape(item.id, quote=True)}"{current}>'
            f'{selected_label}<strong>{escape(item.label)}</strong>'
            f'<span> · {escape(item.meta)}</span></button></form>'
        )
    return "".join(rows)


def _search_target(item: WebSearchItem) -> str | None:
    params: dict[str, str] = {}
    if item.category_id:
        params["category_id"] = item.category_id
    if item.entry_id and item.category_id:
        params["entry_id"] = item.entry_id
    if not params:
        return None
    return "/?" + urlencode(params)


def _search_markup(adapter: WebCatalogReadAdapter, query: str | None) -> str:
    value = "" if query is None else query
    form = (
        '<section class="panel" id="search" aria-labelledby="search-title">'
        '<h2 id="search-title">Suche</h2>'
        '<form method="get" action="/" role="search" aria-labelledby="search-title">'
        '<label for="search-query">Suchbegriff</label> '
        f'<input id="search-query" name="q" type="search" value="{escape(value, quote=True)}" '
        'autocomplete="off"> '
        '<button type="submit">Suchen</button></form>'
    )

    if query is None or not query.strip():
        return form + '<p id="search-results">Suchbegriff eingeben.</p></section>'

    hits = adapter.search(query)
    if not hits:
        return (
            form
            + f'<p id="search-results" role="status">Keine Treffer für „{escape(query.strip())}“.</p>'
            + '</section>'
        )

    rows: list[str] = []
    for item in hits:
        target = _search_target(item)
        label = f'{escape(item.kind_label)} · {escape(item.label)}'
        if target is None:
            rows.append(f'<li><span>{label}</span></li>')
        else:
            rows.append(
                f'<li><a href="{escape(target, quote=True)}">{label}</a></li>'
            )
    return (
        form
        + f'<p id="search-results" role="status">{len(hits)} Treffer</p>'
        + '<ul aria-label="Suchergebnisse">'
        + "".join(rows)
        + '</ul></section>'
    )


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
            f'<span> · {escape(item.field_type + required)}</span>'
            f'<div class="field-value"><span>Wert: </span>'
            f'<strong>{escape(item.value)}</strong></div></div>'
        )
    return "".join(rows)


def render_page(
    adapter: WebCatalogReadAdapter,
    *,
    category_id: str | None = None,
    entry_id: str | None = None,
    search_query: str | None = None,
) -> str:
    """Render the read-only three-stage page without database access."""
    template = _TEMPLATE.read_text(encoding="utf-8")
    categories = adapter.categories()
    entries = adapter.entries(category_id) if category_id else ()
    fields = adapter.fields(entry_id) if entry_id else ()

    return (
        template.replace(
            '<main class="workspace" aria-label="Datenbank-Arbeitsbereich">',
            _search_markup(adapter, search_query)
            + '<main class="workspace" aria-label="Datenbank-Arbeitsbereich">',
        )
        .replace(
            "<!-- CATEGORIES -->",
            _nav_markup(
                categories,
                "Keine Kategorien vorhanden.",
                param_name="category_id",
                selected_id=category_id,
            ),
        )
        .replace(
            "<!-- ENTRIES -->",
            _nav_markup(
                entries,
                "Bitte zuerst eine Kategorie wählen.",
                param_name="entry_id",
                category_id=category_id,
                selected_id=entry_id,
            ),
        )
        .replace("<!-- FIELDS -->", _field_markup(fields))
    )
