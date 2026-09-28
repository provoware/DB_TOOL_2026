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
    target = "/?" + urlencode(params)
    if item.field_id and item.entry_id:
        return target + "#field-" + item.field_id
    if item.entry_id:
        return target + "#detail"
    return target


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
        location = escape(item.location_label)
        preview = (
            f'<span class="search-value">Wert: {escape(item.value_preview)}</span>'
            if item.value_preview is not None
            else ""
        )
        meta = f'<span class="search-location">Fundstelle: {location}</span>' + preview
        if target is None:
            rows.append(f'<li><span>{label}</span>{meta}</li>')
        else:
            rows.append(
                f'<li><a href="{escape(target, quote=True)}">{label}</a>{meta}</li>'
            )
    return (
        form
        + f'<p id="search-results" role="status">{len(hits)} Treffer</p>'
        + '<ul aria-label="Suchergebnisse">'
        + "".join(rows)
        + '</ul></section>'
    )


def _entry_filter_markup(
    category_id: str | None,
    value: str | None,
    visible_count: int,
    sort_value: str | None,
) -> str:
    if not category_id:
        return ""
    current = "" if value is None else value
    status = (
        f'<p id="entry-filter-status" role="status">{visible_count} Einträge sichtbar</p>'
        if current.strip()
        else '<p id="entry-filter-status">Titel-Filter ist aus.</p>'
    )
    return (
        '<form method="get" action="/" aria-labelledby="entry-filter-title">'
        '<h3 id="entry-filter-title">Einträge filtern</h3>'
        f'<input type="hidden" name="category_id" value="{escape(category_id, quote=True)}">'
        + (
            f'<input type="hidden" name="sort" value="{escape(sort_value, quote=True)}">'
            if sort_value
            else ""
        )
        + '<label for="entry-filter">Titel enthält</label> '
        f'<input id="entry-filter" name="filter" type="search" value="{escape(current, quote=True)}" '
        'autocomplete="off"> '
        '<button type="submit">Filtern</button></form>'
        + status
    )



def _entry_sort_markup(category_id: str | None, filter_value: str | None, sort_value: str | None) -> str:
    if not category_id:
        return ""
    current = sort_value if sort_value in {"title_asc", "title_desc"} else "default"
    options = (
        ("default", "Standardreihenfolge"),
        ("title_asc", "Titel A–Z"),
        ("title_desc", "Titel Z–A"),
    )
    option_markup = "".join(
        f'<option value="{value}"{" selected" if value == current else ""}>{label}</option>'
        for value, label in options
    )
    return (
        '<form method="get" action="/" aria-labelledby="entry-sort-title">'
        '<h3 id="entry-sort-title">Einträge sortieren</h3>'
        f'<input type="hidden" name="category_id" value="{escape(category_id, quote=True)}">'
        + (
            f'<input type="hidden" name="filter" value="{escape(filter_value, quote=True)}">'
            if filter_value and filter_value.strip()
            else ""
        )
        + '<label for="entry-sort">Reihenfolge</label> '
        f'<select id="entry-sort" name="sort">{option_markup}</select> '
        '<button type="submit">Sortieren</button></form>'
    )


def _field_markup(items: tuple[WebFieldItem, ...]) -> str:
    if not items:
        return '<p class="placeholder" id="detail-empty">Keine sichtbaren Felder vorhanden.</p>'

    rows: list[str] = []
    for item in items:
        required = " · Pflichtfeld" if item.required else ""
        rows.append(
            '<div class="data-row field-row" '
            f'id="field-{escape(item.id, quote=True)}" '
            f'data-id="{escape(item.id, quote=True)}">'
            f'<strong>{escape(item.label)}</strong>'
            f'<span> · {escape(item.field_type + required)}</span>'
            f'<div class="field-value"><span>Wert: </span>'
            f'<strong>{escape(item.value)}</strong></div></div>'
        )
    return "".join(rows)


def _detail_markup(
    category: WebNavItem | None,
    entry: WebNavItem | None,
    fields: tuple[WebFieldItem, ...],
) -> str:
    if entry is None:
        return '<section id="detail" class="panel" aria-labelledby="detail-title"><h2 id="detail-title">Details</h2><p class="placeholder">Bitte zuerst einen Eintrag wählen.</p></section>'
    category_label = "Unbekannte Kategorie" if category is None else category.label
    return (
        '<section id="detail" class="panel" aria-labelledby="detail-title" tabindex="-1">'
        '<h2 id="detail-title">Eintragsdetails</h2>'
        f'<p class="detail-context"><span>Kategorie: </span><strong>{escape(category_label)}</strong></p>'
        f'<h3>{escape(entry.label)}</h3>'
        f'<p id="detail-field-count" role="status">{len(fields)} sichtbare Felder</p>'
        '<div aria-label="Felder des Eintrags">'
        + _field_markup(fields)
        + '</div></section>'
    )


def render_page(
    adapter: WebCatalogReadAdapter,
    *,
    category_id: str | None = None,
    entry_id: str | None = None,
    search_query: str | None = None,
    entry_filter: str | None = None,
    entry_sort: str | None = None,
) -> str:
    """Render the read-only three-stage page without database access."""
    template = _TEMPLATE.read_text(encoding="utf-8")
    categories = adapter.categories()
    entries = adapter.entries(category_id) if category_id else ()
    if entry_filter and entry_filter.strip():
        needle = entry_filter.strip().casefold()
        entries = tuple(item for item in entries if needle in item.label.casefold())
    if entry_sort == "title_asc":
        entries = tuple(sorted(entries, key=lambda item: (item.label.casefold(), item.id)))
    elif entry_sort == "title_desc":
        entries = tuple(sorted(entries, key=lambda item: (item.label.casefold(), item.id), reverse=True))
    fields = adapter.fields(entry_id) if entry_id else ()
    selected_category = next((item for item in categories if item.id == category_id), None)
    selected_entry = next((item for item in entries if item.id == entry_id), None)

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
            _entry_filter_markup(category_id, entry_filter, len(entries), entry_sort)
            + _entry_sort_markup(category_id, entry_filter, entry_sort)
            + _nav_markup(
                entries,
                (
                    "Keine Einträge entsprechen dem Titel-Filter."
                    if category_id and entry_filter and entry_filter.strip()
                    else "Bitte zuerst eine Kategorie wählen."
                ),
                param_name="entry_id",
                category_id=category_id,
                selected_id=entry_id,
            ),
        )
        .replace("<!-- FIELDS -->", _detail_markup(selected_category, selected_entry, fields))
    )
