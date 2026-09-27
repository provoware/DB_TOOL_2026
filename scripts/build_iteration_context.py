from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
TODO_PROGRESS_RE = re.compile(
    r"\*\*Fortschritt A–M:\*\* \*\*(\d+) von (\d+) = ([0-9]+,[0-9]+) %\*\*"
)
README_PROGRESS_RE = re.compile(
    r"Gesamtfortschritt Master-TODO A–M:\*\* \*\*(\d+) / (\d+) = ([0-9]+,[0-9]+) %\*\*"
)
CHECKBOX_DONE_RE = re.compile(r"^- \[x\] ", re.MULTILINE)
CHECKBOX_OPEN_RE = re.compile(r"^- \[ \] ", re.MULTILINE)
STATUS_LINE_RE = re.compile(r"^> \*\*(.+?):\*\* (.+?)\s*$", re.MULTILINE)
PRIORITY_RE = re.compile(r"^\d+\. \[[ x]\] (.+)$", re.MULTILINE)


def _read(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _percent(value: str) -> float:
    return float(value.replace(",", "."))


def _todo_pool(todo: str) -> str:
    try:
        after_a = todo.split("## A.", 1)[1]
        return after_a.split("## N.", 1)[0]
    except IndexError as exc:
        raise ValueError("TODO A–M pool markers missing") from exc


def _next_priorities(todo: str) -> list[str]:
    marker = "## Nächste sichere Prioritäten"
    if marker not in todo:
        return []
    section = todo.split(marker, 1)[1]
    section = section.split("\n## ", 1)[0]
    return PRIORITY_RE.findall(section)


def _roadmap_status(roadmap: str) -> str:
    for line in roadmap.splitlines():
        if line.startswith("Stand:"):
            return line.removeprefix("Stand:").strip()
    return "unbekannt"


def build_context(root: Path) -> dict[str, Any]:
    readme = _read(root, "README.md")
    todo = _read(root, "TODO.md")
    roadmap = _read(root, "docs/PRODUCT_ROADMAP.md")
    agents = _read(root, "AGENTS.md")

    pool = _todo_pool(todo)
    done = len(CHECKBOX_DONE_RE.findall(pool))
    open_items = len(CHECKBOX_OPEN_RE.findall(pool))
    total = done + open_items
    calculated_percent = round((done / total) * 100, 1) if total else 0.0

    todo_match = TODO_PROGRESS_RE.search(todo)
    readme_match = README_PROGRESS_RE.search(readme)
    if todo_match is None:
        raise ValueError("TODO progress declaration missing")
    if readme_match is None:
        raise ValueError("README progress declaration missing")

    manifests = sorted((root / ".provoware" / "iterations").glob("*.json"))
    if not manifests:
        raise ValueError("no iteration manifest found")
    latest_manifest_path = manifests[-1]
    latest_manifest = json.loads(latest_manifest_path.read_text(encoding="utf-8"))

    status = {label: value.strip() for label, value in STATUS_LINE_RE.findall(readme)}

    sources = {
        "AGENTS.md": agents,
        "README.md": readme,
        "TODO.md": todo,
        "docs/PRODUCT_ROADMAP.md": roadmap,
        str(latest_manifest_path.relative_to(root)): latest_manifest_path.read_text(encoding="utf-8"),
    }

    return {
        "schema_version": 1,
        "latest_iteration": int(latest_manifest["iteration"]),
        "latest_manifest": str(latest_manifest_path.relative_to(root)),
        "latest_change_kind": str(latest_manifest["change_kind"]),
        "latest_gate_profile": str(latest_manifest["gate_profile"]),
        "status": status,
        "roadmap_status": _roadmap_status(roadmap),
        "todo": {
            "done": done,
            "open": open_items,
            "total": total,
            "calculated_percent": calculated_percent,
            "declared_todo_done": int(todo_match.group(1)),
            "declared_todo_total": int(todo_match.group(2)),
            "declared_todo_percent": _percent(todo_match.group(3)),
            "declared_readme_done": int(readme_match.group(1)),
            "declared_readme_total": int(readme_match.group(2)),
            "declared_readme_percent": _percent(readme_match.group(3)),
        },
        "next_priorities": _next_priorities(todo),
        "source_hashes": {name: _sha256(text) for name, text in sources.items()},
    }


def validate_context(context: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    todo = context["todo"]
    expected = (todo["done"], todo["total"], todo["calculated_percent"])
    declared_todo = (
        todo["declared_todo_done"],
        todo["declared_todo_total"],
        todo["declared_todo_percent"],
    )
    declared_readme = (
        todo["declared_readme_done"],
        todo["declared_readme_total"],
        todo["declared_readme_percent"],
    )
    if declared_todo != expected:
        issues.append(f"TODO progress drift: declared={declared_todo!r} actual={expected!r}")
    if declared_readme != expected:
        issues.append(f"README progress drift: declared={declared_readme!r} actual={expected!r}")
    if not context["next_priorities"]:
        issues.append("next priorities missing")
    if context["latest_iteration"] < 1:
        issues.append("latest iteration must be positive")
    return issues


def _print_human(context: dict[str, Any]) -> None:
    todo = context["todo"]
    print(
        "PROVOWARE FAST CONTEXT · "
        f"I{context['latest_iteration']} · "
        f"{todo['done']}/{todo['total']} ({todo['calculated_percent']:.1f} %) · "
        f"{context['latest_change_kind']}/{context['latest_gate_profile']}"
    )
    for label in ("Bestätigter Produktstand", "Governance-Stand", "Sicherheitsstatus", "Frozen Core"):
        value = context["status"].get(label)
        if value:
            print(f"{label}: {value}")
    print("Nächste Prioritäten:")
    for index, item in enumerate(context["next_priorities"], start=1):
        print(f"{index}. {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a compact, validated PROVOWARE planning context.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        context = build_context(args.root.resolve())
        issues = validate_context(context) if args.check else []
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAST CONTEXT: ROT · {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(context, ensure_ascii=False, sort_keys=True))
    else:
        _print_human(context)

    if issues:
        for issue in issues:
            print(f"FAST CONTEXT: ROT · {issue}", file=sys.stderr)
        return 2

    if args.check:
        print("FAST CONTEXT: GRÜN", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
