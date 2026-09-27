from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'data-preview-mode="desktop" aria-pressed="true">Desktop</button>',
        'data-preview-mode="tablet" aria-pressed="false">Tablet</button>',
        'data-preview-mode="narrow" aria-pressed="false">Schmal</button>',
        'desktop: { width: "1152", label: "Desktop · 1152 px" }',
        'tablet: { width: "768", label: "Tablet · 768 px" }',
        'narrow: { width: "360", label: "Schmal · 360 px" }',
        '.preview-card[data-preview-mode="desktop"] { width:72rem;',
        '.preview-card[data-preview-mode="tablet"] { width:48rem;',
        '.preview-card[data-preview-mode="narrow"] { width:22.5rem;',
        'preview.dataset.previewMode = mode;',
        'preview.dataset.previewWidth = config.width;',
        'previewModeLabel.textContent = config.label;',
        'button.setAttribute("aria-pressed", String(button.dataset.previewMode === mode));',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I141 NARROW PREVIEW: ROT · missing " + ", ".join(missing))

    if 'data-preview-mode="desktop" data-preview-width="1152"' not in html:
        raise SystemExit("I141 NARROW PREVIEW: ROT · desktop default changed")
    if 'Desktop · 1152 px' not in html or 'Tablet · 768 px' not in html or 'Schmal · 360 px' not in html:
        raise SystemExit("I141 NARROW PREVIEW: ROT · viewport labels incomplete")

    forbidden = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I141 NARROW PREVIEW: ROT · persistence token " + ", ".join(present))

    print("I141 NARROW PREVIEW: GRÜN · third browser-local viewport added, desktop/tablet preserved")


if __name__ == "__main__":
    main()
