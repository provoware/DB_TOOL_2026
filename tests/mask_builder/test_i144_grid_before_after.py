from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'Raster-Assistent · Vorher/Nachher',
        'function currentGridLayout(items)',
        'function compareGridLayouts(current, suggestion)',
        'const current = currentGridLayout(draftElements);',
        'const comparison = compareGridLayouts(current, suggestion);',
        'rowChanged,',
        'columnChanged,',
        'changed: rowChanged || columnChanged,',
        '"Vorher", "Nachher", "Geplante Änderung"',
        'Vorher/Nachher-Vorschau des Rastervorschlags',
        'Zeile " + String(item.before.row) + " → " + String(item.after.row)',
        'Spalte " + String(item.before.column + 1) + " → " + String(item.after.column + 1)',
        'Übernahme gesperrt: Zeile und Spalte besitzen jetzt einen getrennten temporären Browservertrag.',
        'Erst ein späterer Mutations-Slice darf die vorgeschlagenen Positionen dort gezielt einsetzen.',
        'noch nichts übernommen.',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I144 GRID BEFORE/AFTER: ROT · missing " + ", ".join(missing))

    compare_start = html.index("function compareGridLayouts(current, suggestion)")
    compare_end = html.index("function showGridSuggestion()", compare_start)
    compare_block = html[compare_start:compare_end]

    forbidden_mutations = (
        "item.column =",
        "item.width =",
        "draftElements.splice",
        "draftElements.push",
        "draftElements.sort",
        "draftElements.reverse",
    )
    present = [token for token in forbidden_mutations if token in compare_block]
    if present:
        raise SystemExit("I144 GRID BEFORE/AFTER: ROT · mutation in comparison block " + ", ".join(present))

    if "Rastervorschlag übernehmen" in html or "Vorschlag anwenden" in html:
        raise SystemExit("I144 GRID BEFORE/AFTER: ROT · apply action introduced before contract approval")

    forbidden_persistence = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden_persistence if token in html]
    if present:
        raise SystemExit("I144 GRID BEFORE/AFTER: ROT · persistence token " + ", ".join(present))

    print("I144 GRID BEFORE/AFTER: GRÜN · explicit comparison contract without mutation or apply path")


if __name__ == "__main__":
    main()
