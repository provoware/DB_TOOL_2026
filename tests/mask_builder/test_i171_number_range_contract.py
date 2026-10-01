from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/development/ITERATION_171_NUMBER_RANGE_RULE_CONTRACT.md"


def main() -> None:
    text = CONTRACT.read_text(encoding="utf-8")

    required = (
        "`number_range`",
        "`parameters.min`",
        "`parameters.max`",
        "`min <= max`",
        "kanonischen Dezimalformat",
        "Grenzen sind einschließlich",
        "`satisfied` / `number_in_range`",
        "`violated` / `number_below_min`",
        "`violated` / `number_above_max`",
        "`not_evaluable` / `invalid_number_value`",
        "`not_evaluable` / `invalid_number_range`",
        "genau einer gesetzten Grenze",
        "I170-Testausnahme nicht wiederverwenden",
        "## Laienhilfe-Delta",
    )
    missing = [token for token in required if token not in text]
    if missing:
        raise SystemExit("I171 NUMBER RANGE CONTRACT: ROT · missing " + ", ".join(missing))

    closed = (
        "produktive Aktivierung",
        "zwei gleichzeitig gesetzte Grenzen",
        "`validation_json`, Schema, Repository, Migration und Dependencies",
        "CP-03 und CP-06",
    )
    missing_closed = [token for token in closed if token not in text]
    if missing_closed:
        raise SystemExit(
            "I171 NUMBER RANGE CONTRACT: ROT · boundary missing " + ", ".join(missing_closed)
        )

    print("I171 NUMBER RANGE CONTRACT: GRÜN · semantics, messages and scope boundary present")


if __name__ == "__main__":
    main()
