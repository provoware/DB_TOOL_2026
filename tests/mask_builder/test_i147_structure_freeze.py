from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / ".provoware" / "freezes" / "mask-builder-structure-i146.json"
TODO = ROOT / "TODO.md"
README = ROOT / "README.md"


def _section(text: str, start: str, end: str) -> str:
    left = text.index(start)
    right = text.index(end, left)
    return text[left:right]


def main() -> None:
    data = json.loads(FREEZE.read_text(encoding="utf-8"))
    todo = TODO.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    if data["source_main_sha"] != "e875670d10716e9330f09e5fc4456903c2ea8edd":
        raise SystemExit("I147 STRUCTURE FREEZE: ROT · unexpected source SHA")
    if data["confirmed_through_iteration"] != 146:
        raise SystemExit("I147 STRUCTURE FREEZE: ROT · iteration boundary changed")

    structure = _section(todo, "## B. Masken-Baukasten – Struktur", "## C. Datenarbeit")
    open_items = [line for line in structure.splitlines() if line.startswith("- [ ]")]
    if open_items:
        raise SystemExit("I147 STRUCTURE FREEZE: ROT · open structure item: " + " | ".join(open_items))

    if "**30 von 132 = 22,7 %**" not in todo:
        raise SystemExit("I147 STRUCTURE FREEZE: ROT · product progress drift")
    if "I147" not in readme or "Struktur-Freeze" not in readme:
        raise SystemExit("I147 STRUCTURE FREEZE: ROT · README freeze marker missing")

    selected = data["next_area_inventory"]
    if selected["selected_area"] != "C · Datenarbeit" or selected["selected_candidate"] != "Suche":
        raise SystemExit("I147 STRUCTURE FREEZE: ROT · next slice inventory drift")
    if "I148" not in selected["next_iteration"]:
        raise SystemExit("I147 STRUCTURE FREEZE: ROT · next iteration missing")

    print("I147 STRUCTURE FREEZE: GRÜN · structure block frozen; next candidate is search acceptance")


if __name__ == "__main__":
    main()
