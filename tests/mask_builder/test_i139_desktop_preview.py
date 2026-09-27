from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'class="preview-mode-label" id="preview-mode-label">Desktop · 1152 px</p>',
        'class="preview-viewport-shell"',
        'aria-label="Desktop-Vorschau, 1152 Pixel breit"',
        'aria-describedby="preview-mode-label"',
        'class="preview-card" id="preview" data-preview-mode="desktop" data-preview-width="1152"',
        '.preview-card[data-preview-mode="desktop"] { width:72rem;',
        '.preview-viewport-shell { max-width:100%; overflow-x:auto;',
        '.preview-card[data-preview-mode="desktop"]',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I139 DESKTOP PREVIEW: ROT · missing " + ", ".join(missing))

    forbidden = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I139 DESKTOP PREVIEW: ROT · persistence token " + ", ".join(present))

    print("I139 DESKTOP PREVIEW: GRÜN · desktop 1152px contract preserved")


if __name__ == "__main__":
    main()
