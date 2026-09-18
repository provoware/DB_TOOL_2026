from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_plan(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: Plan muss ein JSON-Objekt sein")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Prüft Dateikollisionen zwischen Agentenplänen.")
    parser.add_argument("plans", nargs="+", help="JSON-Plan-Dateien")
    args = parser.parse_args()

    owners: dict[str, str] = {}
    conflicts: list[tuple[str, str, str]] = []

    for name in args.plans:
        path = Path(name)
        plan = load_plan(path)
        agent = str(plan.get("agent", path.stem))
        for raw in plan.get("write_files", []):
            file_path = str(raw)
            previous = owners.get(file_path)
            if previous and previous != agent:
                conflicts.append((file_path, previous, agent))
            else:
                owners[file_path] = agent

    if conflicts:
        print("GESAMTSTATUS: ROT – Dateikollision erkannt")
        for file_path, first, second in conflicts:
            print(f"ROT: {file_path}: {first} <-> {second}")
        return 2

    print("GESAMTSTATUS: GRÜN – keine Dateikollision")
    for file_path, owner in sorted(owners.items()):
        print(f"GRÜN: {file_path} -> {owner}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
