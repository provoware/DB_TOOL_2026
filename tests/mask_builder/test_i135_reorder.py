from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'function moveDraftOrder(id, direction)',
        'const index = draftElements.findIndex((item) => item.id === id);',
        'const targetIndex = index + direction;',
        'const [item] = draftElements.splice(index, 1);',
        'draftElements.splice(targetIndex, 0, item);',
        'focusDraftOrderControl(id, direction);',
        'moveUpButton.className = "move-draft-up";',
        'moveDownButton.className = "move-draft-down";',
        'moveUpButton.disabled = index === 0;',
        'moveDownButton.disabled = index === draftElements.length - 1;',
        'moveUpButton.addEventListener("click", () => moveDraftOrder(item.id, -1));',
        'moveDownButton.addEventListener("click", () => moveDraftOrder(item.id, 1));',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I135 REORDER: ROT · missing " + ", ".join(missing))

    block_start = html.index('function moveDraftOrder(id, direction)')
    block_end = html.index('function focusDuplicateControl(id)', block_start)
    block = html[block_start:block_end]

    if 'draftElements.sort(' in block:
        raise SystemExit("I135 REORDER: ROT · global sort would obscure deterministic one-step movement")
    if block.index('draftElements.splice(index, 1)') > block.index('draftElements.splice(targetIndex, 0, item)'):
        raise SystemExit("I135 REORDER: ROT · insertion occurs before removal")
    if 'renderDraft();' not in block:
        raise SystemExit("I135 REORDER: ROT · preview/editor rerender missing")

    forbidden = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I135 REORDER: ROT · persistence token " + ", ".join(present))

    print("I135 REORDER: GRÜN · deterministic browser-local element order controls present")


if __name__ == "__main__":
    main()
