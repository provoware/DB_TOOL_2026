from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from scripts.control_plane_inspection import (
    validate_draft_plan,
    validate_finding_bundle,
    validate_planner_input,
    validate_request,
)
from scripts.control_plane_shadow import (
    DEFAULT_CONTRACTS as DEFAULT_EXECUTION_CONTRACTS,
    load_json as load_execution_json,
    validate_sealed_plan,
)
from scripts.validate_control_plane import (
    DEFAULT_REGISTRY,
    load_registry,
    require_exact_keys,
    require_string,
    require_string_list,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTROLLER_CONTRACTS = ROOT / ".provoware" / "control" / "controller_contracts.json"
DEFAULT_INSPECTION_CONTRACTS = ROOT / ".provoware" / "control" / "inspection_contracts.json"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")

DECISION_FIELDS = {
    "schema_version",
    "decision_id",
    "plan_id",
    "source_planner_input_id",
    "base_sha",
    "controller_role",
    "state",
    "sealed_plan_sha256",
    "approved_finding_ids",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path}: JSON root must be an object")
    return data


def validate_controller_contracts(data: dict[str, Any]) -> None:
    require_exact_keys(
        data,
        {
            "schema_version",
            "mode",
            "controller_role",
            "draft_state",
            "sealed_state",
            "decision_state",
            "required_decision_fields",
        },
        "controller_contracts",
    )
    if data["schema_version"] != 1:
        fail("controller_contracts.schema_version must be 1")
    if data["mode"] != "SHADOW":
        fail("controller_contracts.mode must remain SHADOW")
    if data["controller_role"] != "CONTROLLER":
        fail("controller_contracts.controller_role must be CONTROLLER")
    if data["draft_state"] != "DRAFT":
        fail("controller_contracts.draft_state must be DRAFT")
    if data["sealed_state"] != "SEALED":
        fail("controller_contracts.sealed_state must be SEALED")
    if data["decision_state"] != "PLAN_SEALED":
        fail("controller_contracts.decision_state must be PLAN_SEALED")
    if set(
        require_string_list(
            data["required_decision_fields"],
            "controller_contracts.required_decision_fields",
        )
    ) != DECISION_FIELDS:
        fail("controller decision fields do not match shadow contract")


def canonical_sha256(data: dict[str, Any]) -> str:
    payload = json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_controller_decision(
    decision: dict[str, Any],
    sealed_plan: dict[str, Any],
    planner_input: dict[str, Any],
    controller_contracts: dict[str, Any] | None = None,
) -> None:
    controller_contracts = (
        load_json(DEFAULT_CONTROLLER_CONTRACTS)
        if controller_contracts is None
        else controller_contracts
    )
    validate_controller_contracts(controller_contracts)
    require_exact_keys(decision, DECISION_FIELDS, "controller_decision")
    if decision["schema_version"] != 1:
        fail("controller_decision.schema_version must be 1")
    if decision["decision_id"] != f"SEAL-{sealed_plan['plan_id']}":
        fail("controller_decision.decision_id must be deterministic from plan_id")
    if decision["plan_id"] != sealed_plan["plan_id"]:
        fail("controller_decision.plan_id does not match sealed plan")
    if decision["source_planner_input_id"] != planner_input["input_id"]:
        fail("controller_decision.source_planner_input_id does not match planner input")
    if decision["base_sha"] != sealed_plan["base_sha"]:
        fail("controller_decision.base_sha does not match sealed plan")
    if decision["controller_role"] != "CONTROLLER":
        fail("controller_decision.controller_role must be CONTROLLER")
    if decision["state"] != "PLAN_SEALED":
        fail("controller_decision.state must be PLAN_SEALED")
    expected_digest = canonical_sha256(sealed_plan)
    if decision["sealed_plan_sha256"] != expected_digest:
        fail("controller_decision.sealed_plan_sha256 does not bind exact sealed plan")
    expected_findings = sorted(item["finding_id"] for item in planner_input["findings"])
    if decision["approved_finding_ids"] != expected_findings:
        fail("controller_decision.approved_finding_ids must exactly match planner findings")


def seal_draft_plan(
    request: dict[str, Any],
    bundle: dict[str, Any],
    planner_input: dict[str, Any],
    draft_plan: dict[str, Any],
    *,
    expected_base_sha: str,
    registry: dict[str, Any] | None = None,
    inspection_contracts: dict[str, Any] | None = None,
    execution_contracts: dict[str, Any] | None = None,
    controller_contracts: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    registry = load_registry(DEFAULT_REGISTRY) if registry is None else registry
    inspection_contracts = (
        load_json(DEFAULT_INSPECTION_CONTRACTS)
        if inspection_contracts is None
        else inspection_contracts
    )
    execution_contracts = (
        load_execution_json(DEFAULT_EXECUTION_CONTRACTS)
        if execution_contracts is None
        else execution_contracts
    )
    controller_contracts = (
        load_json(DEFAULT_CONTROLLER_CONTRACTS)
        if controller_contracts is None
        else controller_contracts
    )

    validate_registry(registry)
    validate_controller_contracts(controller_contracts)
    validate_request(request, contracts=inspection_contracts)
    validate_finding_bundle(bundle, request, contracts=inspection_contracts)
    validate_planner_input(
        planner_input,
        request,
        bundle,
        contracts=inspection_contracts,
    )
    validate_draft_plan(
        draft_plan,
        planner_input,
        contracts=inspection_contracts,
    )

    if not SHA40_RE.fullmatch(expected_base_sha):
        fail("expected_base_sha must be a lowercase 40-character commit SHA")
    if draft_plan["base_sha"] != expected_base_sha:
        fail(
            "draft_plan.base_sha is stale: "
            f"draft={draft_plan['base_sha']}, expected={expected_base_sha}"
        )

    sealed_plan = {
        "plan_schema_version": draft_plan["plan_schema_version"],
        "plan_id": draft_plan["plan_id"],
        "iteration": draft_plan["iteration"],
        "base_sha": draft_plan["base_sha"],
        "state": "SEALED",
        "goal": draft_plan["goal"],
        "creator_role": draft_plan["creator_role"],
        "write_files": list(draft_plan["proposed_write_files"]),
        "read_files": list(draft_plan["proposed_read_files"]),
        "forbidden_files": list(draft_plan["forbidden_files"]),
        "preserve_capabilities": list(draft_plan["preserve_capabilities"]),
        "acceptance_criteria": list(draft_plan["acceptance_criteria"]),
        "tests_required": list(draft_plan["tests_required"]),
        "side_requests": [
            {
                "request_id": item["request_id"],
                "disposition": item["disposition"],
            }
            for item in draft_plan["side_requests"]
        ],
    }

    # Re-use the I121 execution contract as the authoritative shadow sealing guard.
    # This is where path registry, FROZEN/ARCHIVE policy and capability preservation
    # are checked before any Creator lease can exist.
    validate_sealed_plan(
        sealed_plan,
        registry=registry,
        contracts=execution_contracts,
    )

    decision = {
        "schema_version": 1,
        "decision_id": f"SEAL-{sealed_plan['plan_id']}",
        "plan_id": sealed_plan["plan_id"],
        "source_planner_input_id": planner_input["input_id"],
        "base_sha": sealed_plan["base_sha"],
        "controller_role": "CONTROLLER",
        "state": "PLAN_SEALED",
        "sealed_plan_sha256": canonical_sha256(sealed_plan),
        "approved_finding_ids": sorted(
            item["finding_id"] for item in planner_input["findings"]
        ),
    }
    validate_controller_decision(
        decision,
        sealed_plan,
        planner_input,
        controller_contracts=controller_contracts,
    )
    return decision, sealed_plan


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Seal a valid Control Plane V2 SHADOW draft plan deterministically."
    )
    parser.add_argument("request", type=Path)
    parser.add_argument("bundle", type=Path)
    parser.add_argument("planner_input", type=Path)
    parser.add_argument("draft_plan", type=Path)
    parser.add_argument("--expected-base-sha", required=True)
    args = parser.parse_args()

    try:
        decision, sealed = seal_draft_plan(
            load_json(args.request),
            load_json(args.bundle),
            load_json(args.planner_input),
            load_json(args.draft_plan),
            expected_base_sha=args.expected_base_sha,
        )
        print(
            json.dumps(
                {"decision": decision, "sealed_plan": sealed},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        print("CONTROL PLANE SHADOW CONTROLLER: GRÜN")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"CONTROL PLANE SHADOW CONTROLLER: ROT · {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
