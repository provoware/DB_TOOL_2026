from __future__ import annotations

from provoware_db.mask_builder.browser_shell import render_editor_shell


def main() -> None:
    html = render_editor_shell()

    required = (
        'data-focus-stage="1"',
        'data-focus-stage="2"',
        'data-focus-stage="3"',
        'id="canvas-keyboard-help"',
        'aria-describedby="canvas-keyboard-help"',
        'function setTargetTabStop(index)',
        'button.tabIndex = candidateIndex === index ? 0 : -1;',
        'button.addEventListener("focus", () => setTargetTabStop(index));',
        'setTargetTabStop(next);',
        'setTargetTabStop(0);',
        'tabindex="0"',
        'tabindex="-1"',
    )
    missing = [token for token in required if token not in html]
    if missing:
        raise SystemExit("I138 TAB ORDER: ROT · missing " + ", ".join(missing))

    if "tabindex=\"1\"" in html or "tabindex=\"2\"" in html or "tabindex=\"3\"" in html:
        raise SystemExit("I138 TAB ORDER: ROT · positive tabindex must not be introduced")

    if html.index('data-focus-stage="1"') > html.index('data-focus-stage="2"'):
        raise SystemExit("I138 TAB ORDER: ROT · palette must precede canvas in DOM")
    if html.index('data-focus-stage="2"') > html.index('data-focus-stage="3"'):
        raise SystemExit("I138 TAB ORDER: ROT · canvas must precede preview in DOM")

    forbidden = ("localStorage", "sessionStorage", "indexedDB", "MaskTemplateStore", "sqlite")
    present = [token for token in forbidden if token in html]
    if present:
        raise SystemExit("I138 TAB ORDER: ROT · persistence token " + ", ".join(present))

    print("I138 TAB ORDER: GRÜN · explicit natural focus stages and roving target tab stop present")


if __name__ == "__main__":
    main()
