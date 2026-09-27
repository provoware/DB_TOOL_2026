from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build_iteration_context.py"


def run_context(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--check", "--json"],
        text=True,
        capture_output=True,
    )


def write_fixture(root: Path, *, readme_progress: str, todo_progress: str) -> None:
    (root / ".provoware" / "iterations").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "AGENTS.md").write_text("agents\n", encoding="utf-8")
    (root / "README.md").write_text(
        "# X\n\n> **Gesamtfortschritt Master-TODO A–M:** **" + readme_progress + "**\n",
        encoding="utf-8",
    )
    (root / "TODO.md").write_text(
        "# TODO\n\n**Fortschritt A–M:** **" + todo_progress + "**\n\n"
        "## Nächste sichere Prioritäten\n\n1. [ ] Eins\n\n"
        "## A. Test\n\n- [x] fertig\n- [ ] offen\n\n## N. Dauerregeln\n",
        encoding="utf-8",
    )
    (root / "docs" / "PRODUCT_ROADMAP.md").write_text("Stand: Test\n", encoding="utf-8")
    (root / ".provoware" / "iterations" / "0001-test.json").write_text(
        json.dumps({"iteration": 1, "change_kind": "docs", "gate_profile": "docs"}),
        encoding="utf-8",
    )


def main() -> None:
    current = run_context(ROOT)
    if current.returncode != 0:
        raise SystemExit("I131 FAST CONTEXT: current repository failed\n" + current.stderr)
    payload = json.loads(current.stdout)
    todo = payload["todo"]
    if todo["done"] != todo["declared_todo_done"]:
        raise SystemExit("I131 FAST CONTEXT: TODO done count mismatch")
    if todo["total"] != todo["declared_readme_total"]:
        raise SystemExit("I131 FAST CONTEXT: README total mismatch")
    if len(payload["source_hashes"]) != 5:
        raise SystemExit("I131 FAST CONTEXT: expected five compact source hashes")
    if not payload["next_priorities"]:
        raise SystemExit("I131 FAST CONTEXT: priorities missing")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_fixture(root, readme_progress="1 / 2 = 50,0 %", todo_progress="2 von 2 = 100,0 %")
        drift = run_context(root)
        if drift.returncode == 0:
            raise SystemExit("I131 FAST CONTEXT: drift was not rejected")
        if "TODO progress drift" not in drift.stderr:
            raise SystemExit("I131 FAST CONTEXT: expected TODO drift evidence")

    print("I131 FAST CONTEXT: GRÜN · compact context + drift gate")


if __name__ == "__main__":
    main()
