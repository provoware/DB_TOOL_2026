from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'function requiredRuleFor(item)',
        'kind: "required"',
        'parameters: {}',
        'function evaluateRequiredRule(rule, item, value)',
        'state: "not_evaluable"',
        'state: "violated"',
        'state: "satisfied"',
        'value.trim().length === 0',
        'requiredPreviewValue: ""',
        'className = "required-preview-input"',
        'className = "required-preview-result"',
        'setAttribute("aria-live", "polite")',
        'function appendTooltip(container, id, label, text)',
        'tooltip.setAttribute("role", "tooltip")',
        'Schaltet nur die temporäre Pflichtwert-Preview ein oder aus.',
        'Leer und nur Leerzeichen verletzen die Pflichtwertregel.',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I167 REQUIRED PREVIEW: ROT · missing " + ", ".join(missing))

    forbidden = (
        "fetch(",
        "XMLHttpRequest",
        "localStorage",
        "sessionStorage",
        "indexedDB",
        'method="post"',
        "validation_json",
    )
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I167 REQUIRED PREVIEW: ROT · persistence/network token " + ", ".join(present))

    evaluator = html[html.index("function evaluateRequiredRule"):html.index("function updateRequiredPreview")]
    for message in (
        "Pflichtwertregel oder Zielfeld ist ungültig.",
        "Der Testwert ist ungültig.",
        "Dieses Feld ist ein Pflichtfeld. Gib einen Wert ein.",
        "Pflichtwert vorhanden.",
    ):
        if message not in evaluator:
            raise SystemExit("I167 REQUIRED PREVIEW: ROT · missing state message " + message)

    print("I167 REQUIRED PREVIEW: GRÜN · states, accessibility, tooltips and boundary present")


if __name__ == "__main__":
    main()
