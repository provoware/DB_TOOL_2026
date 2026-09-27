from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'let pendingGridSuggestion = null;',
        'function applyPendingGridSuggestion()',
        'const currentFingerprint = JSON.stringify(gridSuggestionSnapshot(draftElements));',
        'currentFingerprint !== pendingGridSuggestion.sourceFingerprint',
        'const draftBefore = JSON.stringify(draftElements);',
        'const nextLayout = new Map(temporaryGridLayout);',
        'pendingGridSuggestion.positions.forEach((position) => {',
        '!validateTemporaryGridPosition(position.row, position.column, position.width)',
        'nextLayout.set(position.id, { row: position.row, column: position.column });',
        'if (JSON.stringify(draftElements) !== draftBefore) {',
        'throw new Error("Rasterübernahme darf Draftdaten nicht verändern.");',
        'temporaryGridLayout.clear();',
        'nextLayout.forEach((position, id) => temporaryGridLayout.set(id, position));',
        'renderDraft();',
        'showGridSuggestion();',
        'gridAssistantButton.focus();',
        'applyButton.textContent = "Rastervorschlag übernehmen";',
        'applyButton.addEventListener("click", applyPendingGridSuggestion);',
        'sourceFingerprint: before,',
        'positions: suggestion.map((item) => ({',
        'Raster-Assistent · Vorschlag browserlokal übernommen · Draftdaten und Breiten unverändert.',
        'const position = temporaryGridPosition(item, itemIndex + 1);',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I146 GRID APPLY: ROT · missing " + ", ".join(missing))

    apply_start = html.index("function applyPendingGridSuggestion()")
    apply_end = html.index("function showGridSuggestion()", apply_start)
    apply_block = html[apply_start:apply_end]

    forbidden_draft_mutations = (
        "item.column =",
        "item.width =",
        "draftElements.splice",
        "draftElements.push",
        "draftElements.sort",
        "draftElements.reverse",
    )
    present = [token for token in forbidden_draft_mutations if token in apply_block]
    if present:
        raise SystemExit("I146 GRID APPLY: ROT · draft mutation in apply block " + ", ".join(present))

    forbidden_persistence = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden_persistence if token in html]
    if present:
        raise SystemExit("I146 GRID APPLY: ROT · persistence token " + ", ".join(present))

    print("I146 GRID APPLY: GRÜN · atomic temporary-layout application without draft mutation")


if __name__ == "__main__":
    main()
