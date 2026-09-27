from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'const collapsedSectionIds = new Set();',
        'function togglePreviewSection(id)',
        'item.kind !== "section"',
        'collapsedSectionIds.add(id);',
        'collapsedSectionIds.delete(id);',
        'focusPreviewSectionToggle(id);',
        'toggle.className = "preview-section-toggle";',
        'toggle.setAttribute("aria-expanded", String(!collapsedSectionIds.has(item.id)));',
        'toggle.setAttribute("aria-controls", listId);',
        'activeList.hidden = collapsedSectionIds.has(item.id);',
        'collapsedSectionIds.delete(id);',
        '.preview-section-toggle[aria-expanded="false"]::after',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I137 COLLAPSE: ROT · missing " + ", ".join(missing))

    block_start = html.index('function togglePreviewSection(id)')
    block_end = html.index('function nextDraftElementId()', block_start)
    block = html[block_start:block_end]

    forbidden = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I137 COLLAPSE: ROT · persistence token " + ", ".join(present))

    if 'renderDraft();' not in block:
        raise SystemExit("I137 COLLAPSE: ROT · rerender missing")
    if block.index('renderDraft();') > block.index('focusPreviewSectionToggle(id);'):
        raise SystemExit("I137 COLLAPSE: ROT · focus restoration must happen after rerender")

    print("I137 COLLAPSE: GRÜN · accessible browser-local section toggles present")


if __name__ == "__main__":
    main()
