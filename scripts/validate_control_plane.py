from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / ".provoware" / "control" / "registry.json"

ALLOWED_MODES = {"SHADOW", "ENFORCED"}
ALLOWED_PATH_STATES = {
    "FROZEN",
    "STABLE",
    "ACTIVE",
    "EXPERIMENTAL",
    "GENERATED",
    "ARCHIVE",
}
ALLOWED_GATES = {"scope", "docs", "governance", "product", "ui", "deep"}
PRODUCT_CHANGE_KINDS = {"ui", "product", "frozen_core"}
PROTECTED_PATHS = {
    "src/provoware_db/domain/**",
    "src/provoware_db/storage/**",
    "src/provoware_db/application/catalog_service.py",
}
REQUIRED_PROPERTIES = {
    "label",
    "help_text",
    "required",
    "datatype",
    "scalar_default",
    "choice_options",
    "visibility",
    "width",
    "focus_return",
    "preview_consistency",
}
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise ValueError(message)


def require_exact_keys(data: dict[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(data))
    extra = sorted(set(data) - expected)
    if missing:
        fail(f"{label}: missing keys: {', '.join(missing)}")
    if extra:
        fail(f"{label}: unknown keys: {', '.join(extra)}")


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label}: non-empty string required")
    return value


def require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        fail(f"{label}: boolean required")
    return value


def require_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list):
        fail(f"{label}: array required")
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = require_string(item, f"{label}[]")
        if text in seen:
            fail(f"{label}: duplicate value {text!r}")
        seen.add(text)
        result.append(text)
    return result


def safe_repo_path(raw: str, label: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        fail(f"{label}: unsafe repository path {raw!r}")
    return ROOT / path


def latest_product_iteration() -> int:
    iterations = ROOT / ".provoware" / "iterations"
    latest = 0
    for manifest_path in sorted(iterations.glob("*.json")):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(f"cannot read iteration manifest {manifest_path}: {exc}")
        if not isinstance(data, dict):
            fail(f"{manifest_path}: manifest root must be an object")
        if data.get("change_kind") in PRODUCT_CHANGE_KINDS:
            iteration = data.get("iteration")
            if not isinstance(iteration, int) or isinstance(iteration, bool):
                fail(f"{manifest_path}: product iteration must be an integer")
            latest = max(latest, iteration)
    if latest == 0:
        fail("no product iteration manifest found")
    return latest


def validate_registry(data: dict[str, Any]) -> None:
    require_exact_keys(
        data,
        {"schema_version", "mode", "authoritative", "project", "workflow", "paths", "capabilities"},
        "registry",
    )
    if data["schema_version"] != 1:
        fail("schema_version must be 1")
    if data["mode"] not in ALLOWED_MODES:
        fail(f"mode must be one of {sorted(ALLOWED_MODES)}")
    require_bool(data["authoritative"], "authoritative")

    # I120 starts deliberately fail-closed in shadow mode. Authority switching is
    # a later explicit migration and may not happen as an incidental registry edit.
    if data["mode"] != "SHADOW" or data["authoritative"] is not False:
        fail("I120 registry foundation must remain SHADOW and non-authoritative")

    project = data["project"]
    if not isinstance(project, dict):
        fail("project: object required")
    require_exact_keys(
        project,
        {
            "latest_product_iteration",
            "baseline_product_sha",
            "product_stage",
            "persistence",
            "frozen_checkpoints",
        },
        "project",
    )
    latest = project["latest_product_iteration"]
    if not isinstance(latest, int) or isinstance(latest, bool) or latest < 1:
        fail("project.latest_product_iteration must be a positive integer")
    actual_latest = latest_product_iteration()
    if latest != actual_latest:
        fail(
            "project.latest_product_iteration is stale: "
            f"registry={latest}, manifests={actual_latest}"
        )
    baseline_sha = require_string(project["baseline_product_sha"], "project.baseline_product_sha")
    if not SHA40_RE.fullmatch(baseline_sha):
        fail("project.baseline_product_sha must be a lowercase 40-character commit SHA")
    require_string(project["product_stage"], "project.product_stage")
    if project["persistence"] != "CLOSED":
        fail("project.persistence must remain CLOSED in the I120 shadow foundation")
    checkpoints = set(require_string_list(project["frozen_checkpoints"], "project.frozen_checkpoints"))
    if not {"CP-03", "CP-06"}.issubset(checkpoints):
        fail("project.frozen_checkpoints must contain CP-03 and CP-06")

    workflow = data["workflow"]
    if not isinstance(workflow, dict):
        fail("workflow: object required")
    require_exact_keys(
        workflow,
        {
            "single_product_writer",
            "inspectors_read_only",
            "planner_read_only",
            "validator_read_only",
            "side_requests_default",
        },
        "workflow",
    )
    for flag in (
        "single_product_writer",
        "inspectors_read_only",
        "planner_read_only",
        "validator_read_only",
    ):
        if require_bool(workflow[flag], f"workflow.{flag}") is not True:
            fail(f"workflow.{flag} must be true")
    if workflow["side_requests_default"] != "DEFER":
        fail("workflow.side_requests_default must be DEFER")

    paths = data["paths"]
    if not isinstance(paths, list) or not paths:
        fail("paths: non-empty array required")
    path_rules: dict[str, dict[str, Any]] = {}
    for index, rule in enumerate(paths):
        label = f"paths[{index}]"
        if not isinstance(rule, dict):
            fail(f"{label}: object required")
        allowed = {
            "pattern",
            "state",
            "checkpoints",
            "automatic_write",
            "required_gate",
            "preserve_capabilities",
        }
        extra = sorted(set(rule) - allowed)
        if extra:
            fail(f"{label}: unknown keys: {', '.join(extra)}")
        for required in ("pattern", "state", "automatic_write", "required_gate"):
            if required not in rule:
                fail(f"{label}: missing key {required}")
        pattern = require_string(rule["pattern"], f"{label}.pattern")
        if pattern in path_rules:
            fail(f"paths: duplicate pattern {pattern!r}")
        state = rule["state"]
        if state not in ALLOWED_PATH_STATES:
            fail(f"{label}.state must be one of {sorted(ALLOWED_PATH_STATES)}")
        automatic_write = require_bool(rule["automatic_write"], f"{label}.automatic_write")
        gate = rule["required_gate"]
        if gate not in ALLOWED_GATES:
            fail(f"{label}.required_gate must be one of {sorted(ALLOWED_GATES)}")
        if state in {"FROZEN", "ARCHIVE"} and automatic_write:
            fail(f"{label}: {state} path may not allow automatic writes")
        if "checkpoints" in rule:
            require_string_list(rule["checkpoints"], f"{label}.checkpoints")
        if "preserve_capabilities" in rule:
            require_string_list(rule["preserve_capabilities"], f"{label}.preserve_capabilities")
        path_rules[pattern] = rule

    missing_protected = sorted(PROTECTED_PATHS - set(path_rules))
    if missing_protected:
        fail("legacy protected paths missing from control registry: " + ", ".join(missing_protected))
    for protected in sorted(PROTECTED_PATHS):
        rule = path_rules[protected]
        if rule["state"] != "FROZEN":
            fail(f"legacy protected path must remain FROZEN: {protected}")
        if rule["automatic_write"] is not False:
            fail(f"legacy protected path may not allow automatic writes: {protected}")
        if rule["required_gate"] != "deep":
            fail(f"legacy protected path must require deep gate: {protected}")

    capabilities = data["capabilities"]
    if not isinstance(capabilities, dict):
        fail("capabilities: object required")
    properties = capabilities.get("MASK_PROPERTIES_V1")
    if not isinstance(properties, dict):
        fail("MASK_PROPERTIES_V1 capability is required")
    require_exact_keys(
        properties,
        {"state", "baseline_iteration", "evidence", "properties", "reopen_required"},
        "capabilities.MASK_PROPERTIES_V1",
    )
    if properties["state"] != "STABLE":
        fail("MASK_PROPERTIES_V1 must be STABLE")
    if properties["baseline_iteration"] != 119:
        fail("MASK_PROPERTIES_V1 baseline_iteration must be 119")
    if require_bool(properties["reopen_required"], "MASK_PROPERTIES_V1.reopen_required") is not True:
        fail("MASK_PROPERTIES_V1.reopen_required must be true")
    property_names = set(
        require_string_list(properties["properties"], "MASK_PROPERTIES_V1.properties")
    )
    if property_names != REQUIRED_PROPERTIES:
        missing = sorted(REQUIRED_PROPERTIES - property_names)
        extra = sorted(property_names - REQUIRED_PROPERTIES)
        fail(f"MASK_PROPERTIES_V1 properties mismatch: missing={missing}, extra={extra}")

    evidence_paths = require_string_list(properties["evidence"], "MASK_PROPERTIES_V1.evidence")
    if len(evidence_paths) < 2:
        fail("MASK_PROPERTIES_V1 requires both I119 evidence records")
    for raw in evidence_paths:
        evidence_path = safe_repo_path(raw, "MASK_PROPERTIES_V1.evidence")
        if not evidence_path.is_file():
            fail(f"MASK_PROPERTIES_V1 evidence file missing: {raw}")
        try:
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(f"cannot read MASK_PROPERTIES_V1 evidence {raw}: {exc}")
        if not isinstance(evidence, dict):
            fail(f"MASK_PROPERTIES_V1 evidence must be an object: {raw}")
        if evidence.get("iteration") != 119:
            fail(f"MASK_PROPERTIES_V1 evidence has wrong iteration: {raw}")
        if evidence.get("overall_status") != "GREEN":
            fail(f"MASK_PROPERTIES_V1 evidence is not GREEN: {raw}")


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("registry root must be an object")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the PROVOWARE Control Plane V2 registry.")
    parser.add_argument("registry", nargs="?", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()

    try:
        data = load_registry(args.registry)
        validate_registry(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"CONTROL PLANE V1: ROT · {exc}")
        return 2

    print(
        "CONTROL PLANE V1: GRÜN · "
        "SHADOW · single writer · frozen paths · MASK_PROPERTIES_V1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
