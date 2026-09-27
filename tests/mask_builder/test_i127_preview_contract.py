from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    preview_start = html.index('const visibleDraftElements = draftElements.filter((item) => item.isVisible);')
    preview_end = html.index('preview.appendChild(list);', preview_start)
    preview = html[preview_start:preview_end]

    required_tokens = (
        'draftElements.filter((item) => item.isVisible)',
        'row.dataset.draftId = item.id;',
        'item.label',
        '" · Spalten "',
        'item.helpText',
        '" · Pflichtfeld"',
        '" · Datentyp: " + item.dataType',
        '" · Auswahloptionen: noch nicht konfiguriert"',
        'item.options.map((option) => option.label).join(" | ")',
        '" · Standard: " + defaultValuePreview(item)',
    )
    missing = [token for token in required_tokens if token not in preview]
    if missing:
        raise SystemExit("I127 PREVIEW CONTRACT: ROT · missing " + ", ".join(missing))

    if 'defaultSelection' in html:
        raise SystemExit("I127 PREVIEW CONTRACT: ROT · defaultSelection opened too early")

    forbidden = ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "indexedDB", 'method="post"')
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I127 PREVIEW CONTRACT: ROT · persistence/network token " + ", ".join(present))

    print("I127 PREVIEW CONTRACT: GRÜN · gemeinsame Eigenschaften-/Preview-Matrix geschlossen")


if __name__ == "__main__":
    main()
