from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_iteration_context import build_context, validate_context
from validate_iteration_manifest import validate as validate_manifest

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_PROFILES = {
    "scope_only": {"scope", "deep"},
    "docs": {"docs", "deep"},
    "governance": {"governance", "deep"},
    "product": {"product", "deep"},
    "ui": {"ui", "deep"},
    "frozen_core": {"deep"},
}

PROTECTED_PREFIXES = (
    "src/provoware_db/domain/",
    "src/provoware_db/storage/",
)
PROTECTED_EXACT = {
    "src/provoware_db/application/catalog_service.py",
}


def latest_manifest(root: Path) -> Path:
    manifests = sorted((root / ".provoware" / "iterations").glob("*.json"))
    if not manifests:
        raise ValueError("no iteration manifest found")
    return manifests[-1]


def resolve_gate_route(data: dict[str, Any]) -> tuple[bool, bool, bool]:
    kind = str(data["change_kind"])
    profile = str(data["gate_profile"])
    if profile not in ALLOWED_PROFILES[kind]:
        raise ValueError(
            f"Gate profile downgrade blocked: kind={kind!r} cannot use profile={profile!r}"
        )

    write_files = tuple(str(path) for path in data["write_files"])
    protected_files = [
        path
        for path in write_files
        if path in PROTECTED_EXACT or path.startswith(PROTECTED_PREFIXES)
    ]
    if protected_files and profile != "deep":
        raise ValueError(
            "Frozen-core path requires gate_profile=deep: "
            + ", ".join(sorted(protected_files))
        )

    ci = data["ci"]
    has_targeted_work = bool(
        data["pip_requirements"] or ci["compile"] or ci["python_tests"]
    )
    return (
        has_targeted_work or profile in {"product", "ui", "deep"},
        profile in {"governance", "deep"},
        profile in {"product", "ui", "deep"},
    )


def run_preflight(root: Path, manifest_path: Path) -> tuple[dict[str, Any], tuple[bool, bool, bool]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    validate_manifest(data)

    context = build_context(root)
    issues = validate_context(context)
    if issues:
        raise ValueError("; ".join(issues))

    expected_latest = latest_manifest(root).resolve()
    if manifest_path.resolve() != expected_latest:
        raise ValueError(
            f"manifest is not latest: selected={manifest_path.name} latest={expected_latest.name}"
        )

    if int(data["iteration"]) != int(context["latest_iteration"]):
        raise ValueError(
            f"iteration mismatch: manifest={data['iteration']} context={context['latest_iteration']}"
        )

    route = resolve_gate_route(data)
    return context, route


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run one fast local/CI preflight for context, manifest and gate routing."
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        help="Manifest to validate; defaults to the latest iteration manifest.",
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    root = args.root.resolve()
    manifest = args.manifest or latest_manifest(root)
    if not manifest.is_absolute():
        manifest = root / manifest

    context, route = run_preflight(root, manifest)
    run_targeted, run_governance, run_foundation = route
    data = json.loads(manifest.read_text(encoding="utf-8"))

    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as handle:
            handle.write(f"profile={data['gate_profile']}\n")
            handle.write(f"run_targeted={str(run_targeted).lower()}\n")
            handle.write(f"run_governance={str(run_governance).lower()}\n")
            handle.write(f"run_foundation={str(run_foundation).lower()}\n")

    result = {
        "iteration": context["latest_iteration"],
        "manifest": str(manifest.relative_to(root)),
        "progress": context["todo"]["calculated_percent"],
        "profile": data["gate_profile"],
        "run_targeted": run_targeted,
        "run_governance": run_governance,
        "run_foundation": run_foundation,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(
            "PREFLIGHT: GRÜN · "
            f"I{result['iteration']} · {result['profile']} · "
            f"targeted={run_targeted} governance={run_governance} foundation={run_foundation}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"PREFLIGHT: ROT · {exc}")
        raise SystemExit(2)
