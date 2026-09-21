from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REQUIRED = (
    "schema_version",
    "iteration",
    "agent",
    "size",
    "goal",
    "change_kind",
    "gate_profile",
    "guide_delta",
    "write_files",
    "read_files",
    "direct_dependencies",
    "tests_required",
    "tests_explicitly_not_run",
    "pip_requirements",
    "ci",
    "risks",
    "non_changes",
    "expected_side_effects",
    "screenshot_required",
    "status",
)

ARRAY_FIELDS = (
    "write_files",
    "read_files",
    "direct_dependencies",
    "tests_required",
    "tests_explicitly_not_run",
    "pip_requirements",
    "risks",
    "non_changes",
    "expected_side_effects",
)

SIZES = {"S", "M", "L", "XL"}
CHANGE_KINDS = {"scope_only", "docs", "governance", "product", "ui", "frozen_core"}
GATE_PROFILES = {"scope", "docs", "governance", "product", "ui", "deep"}
GUIDE_MODES = {"explain_change", "optimize_existing", "no_user_change"}
STATUS_RE = re.compile(r"^[A-Z0-9_]+$")


def fail(message: str) -> None:
    raise ValueError(message)


def require_string(value: Any, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label}: non-empty string required")


def require_string_array(value: Any, label: str) -> None:
    if not isinstance(value, list):
        fail(f"{label}: array required")
    seen: set[str] = set()
    for item in value:
        require_string(item, f"{label}[]")
        if item in seen:
            fail(f"{label}: duplicate value {item!r}")
        seen.add(item)


def require_safe_relative_paths(values: list[str], label: str) -> None:
    for raw in values:
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts:
            fail(f"{label}: unsafe path {raw!r}")


def validate(data: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED if key not in data]
    if missing:
        fail("missing required fields: " + ", ".join(missing))

    extra = sorted(set(data) - set(REQUIRED))
    if extra:
        fail("unknown top-level fields: " + ", ".join(extra))

    if data["schema_version"] != 2:
        fail("schema_version must be 2")
    if not isinstance(data["iteration"], int) or isinstance(data["iteration"], bool) or data["iteration"] < 1:
        fail("iteration must be a positive integer")

    require_string(data["agent"], "agent")
    require_string(data["goal"], "goal")
    if data["size"] not in SIZES:
        fail(f"size must be one of {sorted(SIZES)}")
    if data["change_kind"] not in CHANGE_KINDS:
        fail(f"change_kind must be one of {sorted(CHANGE_KINDS)}")
    if data["gate_profile"] not in GATE_PROFILES:
        fail(f"gate_profile must be one of {sorted(GATE_PROFILES)}")

    for key in ARRAY_FIELDS:
        require_string_array(data[key], key)

    require_safe_relative_paths(data["write_files"], "write_files")
    require_safe_relative_paths(data["read_files"], "read_files")
    require_safe_relative_paths(data["pip_requirements"], "pip_requirements")

    guide = data["guide_delta"]
    if not isinstance(guide, dict):
        fail("guide_delta: object required")
    allowed_guide = {"mode", "topic", "summary", "target_doc"}
    missing_guide = [key for key in ("mode", "topic", "summary") if key not in guide]
    if missing_guide:
        fail("guide_delta missing: " + ", ".join(missing_guide))
    extra_guide = sorted(set(guide) - allowed_guide)
    if extra_guide:
        fail("guide_delta unknown fields: " + ", ".join(extra_guide))
    if guide["mode"] not in GUIDE_MODES:
        fail(f"guide_delta.mode must be one of {sorted(GUIDE_MODES)}")
    require_string(guide["topic"], "guide_delta.topic")
    require_string(guide["summary"], "guide_delta.summary")
    target_doc = guide.get("target_doc")
    if target_doc is not None:
        require_string(target_doc, "guide_delta.target_doc")
        require_safe_relative_paths([target_doc], "guide_delta.target_doc")

    ci = data["ci"]
    if not isinstance(ci, dict) or set(ci) != {"compile", "python_tests"}:
        fail("ci must contain exactly compile and python_tests")
    require_string_array(ci["compile"], "ci.compile")
    require_string_array(ci["python_tests"], "ci.python_tests")
    require_safe_relative_paths(ci["compile"], "ci.compile")
    require_safe_relative_paths(ci["python_tests"], "ci.python_tests")

    if not isinstance(data["screenshot_required"], bool):
        fail("screenshot_required must be boolean")
    require_string(data["status"], "status")
    if not STATUS_RE.fullmatch(data["status"]):
        fail("status must contain only A-Z, 0-9 and underscore")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a PROVOWARE iteration manifest V2.")
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("manifest root must be an object")

    validate(data)
    print(f"MANIFEST V2: GRÜN · {args.manifest}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"MANIFEST V2: ROT · {exc}")
        raise SystemExit(2)
