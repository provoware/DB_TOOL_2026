from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'if (item.kind === "section") {',
        'section.className = "preview-section";',
        'section.dataset.draftId = item.id;',
        'heading.id = "preview-section-" + item.id;',
        'section.setAttribute("aria-labelledby", heading.id);',
        'activeList = document.createElement("ol");',
        'activeList.className = "preview-section-items";',
        'activeList.className = "preview-unsectioned-items";',
        'appendPreviewRow(activeList, item);',
        '.preview-section { margin:0 0 1rem;',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I136 SECTIONS: ROT · missing " + ", ".join(missing))

    block_start = html.index('function appendPreviewRow(list, item)')
    block_end = html.index('function selectKind(button)', block_start)
    block = html[block_start:block_end]

    if 'localStorage' in block or 'sessionStorage' in block or 'indexedDB' in block:
        raise SystemExit("I136 SECTIONS: ROT · browser persistence introduced")
    if 'item.kind === "section"' not in block:
        raise SystemExit("I136 SECTIONS: ROT · section boundary missing")
    if block.index('section.appendChild(heading);') > block.index('section.appendChild(activeList);'):
        raise SystemExit("I136 SECTIONS: ROT · heading must precede section list")
    if 'return;' not in block:
        raise SystemExit("I136 SECTIONS: ROT · section item would also be rendered as a normal row")

    print("I136 SECTIONS: GRÜN · semantic browser-local preview sections present")


if __name__ == "__main__":
    main()
