from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'const temporaryGridLayout = new Map();',
        'function validateTemporaryGridPosition(row, column, width)',
        'function setTemporaryGridPosition(id, row, column, width)',
        'function temporaryGridPosition(item, fallbackRow)',
        'function syncTemporaryRowsToDraftOrder()',
        'temporaryGridLayout.set(id, { row, column });',
        'temporaryGridLayout.delete(id);',
        'const position = temporaryGridPosition(item, index + 1);',
        'card.dataset.gridRow = String(position.row);',
        'card.dataset.gridColumn = String(position.column);',
        'card.style.gridColumn = String(position.column + 1) + " / span " + String(item.width);',
        'card.style.gridRow = String(position.row);',
        'setTemporaryGridPosition(created.id, draftElements.length, column, created.width);',
        'setTemporaryGridPosition(duplicate.id, draftElements.length, duplicate.column, duplicate.width);',
        'syncTemporaryRowsToDraftOrder();',
        'setTemporaryGridPosition(moving.id, movingPosition.row, column, moving.width);',
        'row: position.row,',
        'column: position.column,',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I145 TEMP GRID LAYOUT: ROT · missing " + ", ".join(missing))

    if 'data-grid-row' in html or 'data-grid-column' in html:
        pass

    forbidden_apply = ("Rastervorschlag übernehmen", "Vorschlag anwenden")
    present = [token for token in forbidden_apply if token in html]
    if present:
        raise SystemExit("I145 TEMP GRID LAYOUT: ROT · apply action introduced early " + ", ".join(present))

    forbidden_persistence = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden_persistence if token in html]
    if present:
        raise SystemExit("I145 TEMP GRID LAYOUT: ROT · persistence token " + ", ".join(present))

    if "temporaryGridLayout" not in html or "new Map()" not in html:
        raise SystemExit("I145 TEMP GRID LAYOUT: ROT · layout state is not browser-local")

    print("I145 TEMP GRID LAYOUT: GRÜN · explicit transient row+column contract renders without persistence")


if __name__ == "__main__":
    main()
