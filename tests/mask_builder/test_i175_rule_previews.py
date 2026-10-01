from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / "src/provoware_db/mask_builder/browser_shell.py"


def main() -> None:
    source = SHELL.read_text(encoding="utf-8")
    required = (
        'kind: "number_range"',
        'kind: "date_range"',
        'kind: "allowed_file_types"',
        "function evaluateNumberRangeRule",
        "function evaluateDateRangeRule",
        "function evaluateFileTypeRule",
        'className = "number-range-preview"',
        'className = "date-range-preview"',
        'className = "file-type-preview"',
        'setAttribute("aria-live", "polite")',
        'dateRangeFrom: ""',
        'dateRangeTo: ""',
        'allowedFileTypes: ""',
        "Keine Datei wird gelesen oder gespeichert.",
    )
    missing = [token for token in required if token not in source]
    if missing:
        raise SystemExit("I175 RULE PREVIEWS: ROT · missing " + ", ".join(missing))

    preview_code = source[source.index("function dateRangeRuleFor"):source.index("function appendTooltip")]
    forbidden = ("fetch(", "localStorage", "sessionStorage", "FileReader", ".click()")
    violations = [token for token in forbidden if token in preview_code]
    if violations:
        raise SystemExit("I175 RULE PREVIEWS: ROT · boundary violation " + ", ".join(violations))
    print("I175 RULE PREVIEWS: GRÜN · three transient, accessible rule previews present")


if __name__ == "__main__":
    main()
