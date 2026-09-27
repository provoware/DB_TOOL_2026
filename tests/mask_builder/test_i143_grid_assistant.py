from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'id="grid-assistant-button"',
        'id="grid-assistant-output"',
        'Raster-Assistent · Vorschlag',
        'function gridSuggestionSnapshot(items)',
        'function computeGridSuggestion(items)',
        'function showGridSuggestion()',
        'const before = JSON.stringify(gridSuggestionSnapshot(draftElements));',
        'const after = JSON.stringify(gridSuggestionSnapshot(draftElements));',
        'if (before !== after) {',
        'throw new Error("Raster-Assistent darf den Draft nicht verändern.");',
        'if (column + item.width > gridColumns) {',
        'row += 1;',
        'column = 0;',
        'id: item.id,',
        'label: item.label,',
        'row,',
        'column,',
        'width: item.width,',
        'gridAssistantButton.addEventListener("click", showGridSuggestion);',
        'nur gelesen, nichts übernommen.',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I143 GRID ASSISTANT: ROT · missing " + ", ".join(missing))

    block_start = html.index("function computeGridSuggestion(items)")
    block_end = html.index("function showGridSuggestion()", block_start)
    compute_block = html[block_start:block_end]

    forbidden_mutations = (
        "item.column =",
        "item.width =",
        "draftElements.splice",
        "draftElements.push",
        "draftElements.sort",
        "draftElements.reverse",
    )
    present = [token for token in forbidden_mutations if token in compute_block]
    if present:
        raise SystemExit("I143 GRID ASSISTANT: ROT · mutation in compute block " + ", ".join(present))

    forbidden_persistence = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden_persistence if token in html]
    if present:
        raise SystemExit("I143 GRID ASSISTANT: ROT · persistence token " + ", ".join(present))

    if "Rastervorschlag übernehmen" in html or "Vorschlag anwenden" in html:
        raise SystemExit("I143 GRID ASSISTANT: ROT · apply action introduced early")

    print("I143 GRID ASSISTANT: GRÜN · deterministic read-only proposal without apply path")


if __name__ == "__main__":
    main()
