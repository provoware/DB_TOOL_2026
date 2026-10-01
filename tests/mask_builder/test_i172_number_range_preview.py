from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SHELL = ROOT / "src/provoware_db/mask_builder/browser_shell.py"


def main() -> None:
    source = SHELL.read_text(encoding="utf-8")
    required = (
        "function parseCanonicalNumber(value)",
        "function numberRangeRuleFor(item)",
        'kind: "number_range"',
        "function evaluateNumberRangeRule(rule, item, value)",
        'reason: "invalid_number_range"',
        'reason: "invalid_number_value"',
        'reason: "number_below_min"',
        'reason: "number_above_max"',
        'reason: "number_in_range"',
        'item.dataType === "number"',
        'className = "number-range-preview"',
        'className = "number-range-bound"',
        'className = "number-range-boundary"',
        'className = "number-range-value"',
        'className = "number-range-result"',
        'setAttribute("aria-live", "polite")',
        "Prüft genau eine Unter- oder Obergrenze.",
        'numberRangeBoundType: "min"',
        'numberRangeBoundaryValue: ""',
        'numberRangePreviewValue: ""',
    )
    missing = [token for token in required if token not in source]
    if missing:
        raise SystemExit("I172 NUMBER RANGE PREVIEW: ROT · missing " + ", ".join(missing))

    evaluator = source[source.index("function evaluateNumberRangeRule"):source.index("function updateNumberRangePreview")]
    if "fetch(" in evaluator or "localStorage" in evaluator or "sessionStorage" in evaluator:
        raise SystemExit("I172 NUMBER RANGE PREVIEW: ROT · persistence or network boundary violated")
    print("I172 NUMBER RANGE PREVIEW: GRÜN · states, accessibility and transient boundary present")


if __name__ == "__main__":
    main()
