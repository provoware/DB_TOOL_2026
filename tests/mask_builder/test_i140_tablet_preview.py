from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'class="preview-mode-controls" role="group" aria-label="Vorschaugröße"',
        'data-preview-mode="desktop" aria-pressed="true">Desktop</button>',
        'data-preview-mode="tablet" aria-pressed="false">Tablet</button>',
        'data-preview-mode="desktop" data-preview-width="1152"',
        '.preview-card[data-preview-mode="desktop"] { width:72rem;',
        '.preview-card[data-preview-mode="tablet"] { width:48rem;',
        'function setPreviewMode(mode)',
        'if (!["desktop", "tablet"].includes(mode)) {',
        'const width = isDesktop ? "1152" : "768";',
        'const label = isDesktop ? "Desktop · 1152 px" : "Tablet · 768 px";',
        'preview.dataset.previewMode = mode;',
        'preview.dataset.previewWidth = width;',
        'button.setAttribute("aria-pressed", String(button.dataset.previewMode === mode));',
        'button.addEventListener("click", () => setPreviewMode(button.dataset.previewMode));',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I140 TABLET PREVIEW: ROT · missing " + ", ".join(missing))

    if 'data-preview-mode="narrow"' in html:
        raise SystemExit("I140 TABLET PREVIEW: ROT · narrow preview introduced early")

    if 'Desktop · 1152 px' not in html or 'Desktop-Vorschau, 1152 Pixel breit' not in html:
        raise SystemExit("I140 TABLET PREVIEW: ROT · I139 desktop default changed")

    forbidden = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I140 TABLET PREVIEW: ROT · persistence token " + ", ".join(present))

    print("I140 TABLET PREVIEW: GRÜN · browser-local tablet mode added without changing desktop default")


if __name__ == "__main__":
    main()
