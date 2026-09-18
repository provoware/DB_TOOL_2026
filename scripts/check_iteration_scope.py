from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def git_changed(base: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        check=True,
        text=True,
        capture_output=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Vergleicht geplante Schreibdateien mit tatsächlich geänderten Dateien."
    )
    parser.add_argument("plan", help="JSON-Iterationsplan")
    parser.add_argument("--base", default="main", help="Git-Basisbranch")
    parser.add_argument(
        "--changed-file",
        action="append",
        default=[],
        help="Optional: geänderte Datei explizit angeben (für deterministische Selbsttests).",
    )
    args = parser.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    planned = {str(p) for p in plan.get("write_files", [])}
    changed = set(args.changed_file) if args.changed_file else git_changed(args.base)

    allowed_meta_prefixes = (
        ".provoware/",
        ".github/",
        "docs/",
    )
    allowed_meta_files = {"AGENTS.md", "CONTRIBUTING.md", "README.md"}

    unexpected = {
        p
        for p in changed
        if p not in planned
        and p not in allowed_meta_files
        and not p.startswith(allowed_meta_prefixes)
    }

    print(f"Geplant: {len(planned)} Datei(en)")
    print(f"Tatsächlich geändert: {len(changed)} Datei(en)")

    if unexpected:
        print("GESAMTSTATUS: ROT – ungeplante Dateiänderung(en)")
        for path in sorted(unexpected):
            print(f"ROT: {path}")
        return 2

    print("GESAMTSTATUS: GRÜN – Scope eingehalten")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
