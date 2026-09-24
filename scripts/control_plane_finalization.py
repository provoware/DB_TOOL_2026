from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.control_plane_controller import canonical_sha256
from scripts.control_plane_events import append_event, validate_event_log
from scripts.control_plane_shadow import (
    authorize_write_lease,
    validate_sealed_plan,
    validate_validation_report,
    validate_write_lease,
)
from scripts.validate_control_plane import require_exact_keys, require_string, require_string_list


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FINALIZATION_CONTRACTS = ROOT / ".provoware" / "control" / "finalization_contracts.json"

RELEASE_FIELDS = {
    "schema_version",
    "release_id",
    "lease_id",
    "plan_id",
    "base_sha",
    "validation_report_id",
    "finalizer_role",
    "state",
    "sealed_plan_sha256",
}
OUTCOME_FIELDS = {
    "schema_version",
    "outcome_id",
    "request_id",
    "iteration",
    "plan_id",
    "lease_id",
    "release_id",
    "validation_report_id",
    "finalizer_role",
    "state",
    "base_sha",
    "sealed_plan_sha256",
    "final_event_sha256",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path}: JSON root must be an object")
    return data


def validate_finalization_contracts(data: dict[str, Any]) -> None:
    require_exact_keys(
        data,
        {
            "schema_version",
            "mode",
            "finalizer_role",
            "lease_release_state",
            "outcome_state",
            "lease_release_required_fields",
            "outcome_required_fields",
        },
        "finalization_contracts",
    )
    if data["schema_version"] != 1:
        fail("finalization_contracts.schema_version must be 1")
    if data["mode"] != "SHADOW":
        fail("finalization_contracts.mode must remain SHADOW")
    if data["finalizer_role"] != "FINALIZER":
        fail("finalization_contracts.finalizer_role must be FINALIZER")
    if data["lease_release_state"] != "RELEASED":
        fail("finalization_contracts.lease_release_state must be RELEASED")
    if data["outcome_state"] != "DONE":
        fail("finalization_contracts.outcome_state must be DONE")
    if set(
        require_string_list(
            data["lease_release_required_fields"],
            "finalization_contracts.lease_release_required_fields",
        )
    ) != RELEASE_FIELDS:
        fail("lease release fields do not match shadow finalization contract")
    if set(
        require_string_list(
            data["outcome_required_fields"],
            "finalization_contracts.outcome_required_fields",
        )
    ) != OUTCOME_FIELDS:
        fail("outcome fields do not match shadow finalization contract")


def validate_lease_release(
    release: dict[str, Any],
    plan: dict[str, Any],
    lease: dict[str, Any],
    validation_report: dict[str, Any],
    *,
    contracts: dict[str, Any] | None = None,
) -> None:
    contracts = (
        load_json(DEFAULT_FINALIZATION_CONTRACTS)
        if contracts is None
        else contracts
    )
    validate_finalization_contracts(contracts)
    validate_sealed_plan(plan)
    validate_write_lease(lease, plan)
    validate_validation_report(validation_report, plan, lease)

    require_exact_keys(release, RELEASE_FIELDS, "lease_release")
    if release["schema_version"] != 1:
        fail("lease_release.schema_version must be 1")
    if release["release_id"] != f"RELEASE-{lease['lease_id']}":
        fail("lease_release.release_id must be deterministic from lease_id")
    if release["lease_id"] != lease["lease_id"]:
        fail("lease_release.lease_id does not match active lease")
    if release["plan_id"] != plan["plan_id"]:
        fail("lease_release.plan_id does not match sealed plan")
    if release["base_sha"] != plan["base_sha"]:
        fail("lease_release.base_sha does not match sealed plan")
    if release["validation_report_id"] != validation_report["report_id"]:
        fail("lease_release.validation_report_id does not match Validator report")
    if release["finalizer_role"] != "FINALIZER":
        fail("lease_release.finalizer_role must be FINALIZER")
    if release["state"] != "RELEASED":
        fail("lease_release.state must be RELEASED")
    if release["sealed_plan_sha256"] != canonical_sha256(plan):
        fail("lease_release.sealed_plan_sha256 does not bind exact sealed plan")
    if validation_report["verdict"] != "PASS":
        fail("only Validator PASS may release the global write lease")
    if validation_report["findings"]:
        fail("Validator PASS used for release may not contain findings")


def release_write_lease(
    plan: dict[str, Any],
    lease: dict[str, Any],
    validation_report: dict[str, Any],
    *,
    contracts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_sealed_plan(plan)
    validate_write_lease(lease, plan)
    validate_validation_report(validation_report, plan, lease)
    if validation_report["verdict"] != "PASS":
        fail("only Validator PASS may release the global write lease")

    release = {
        "schema_version": 1,
        "release_id": f"RELEASE-{lease['lease_id']}",
        "lease_id": lease["lease_id"],
        "plan_id": plan["plan_id"],
        "base_sha": plan["base_sha"],
        "validation_report_id": validation_report["report_id"],
        "finalizer_role": "FINALIZER",
        "state": "RELEASED",
        "sealed_plan_sha256": canonical_sha256(plan),
    }
    validate_lease_release(
        release,
        plan,
        lease,
        validation_report,
        contracts=contracts,
    )
    return release


def validate_outcome(
    outcome: dict[str, Any],
    request_id: str,
    events: list[dict[str, Any]],
    plan: dict[str, Any],
    lease: dict[str, Any],
    validation_report: dict[str, Any],
    release: dict[str, Any],
    *,
    contracts: dict[str, Any] | None = None,
) -> None:
    contracts = (
        load_json(DEFAULT_FINALIZATION_CONTRACTS)
        if contracts is None
        else contracts
    )
    validate_finalization_contracts(contracts)
    validate_lease_release(
        release,
        plan,
        lease,
        validation_report,
        contracts=contracts,
    )
    final_state, hard_stopped = validate_event_log(events, request_id)
    if final_state != "DONE" or hard_stopped:
        fail("outcome requires a non-stopped event log in DONE state")
    if not events:
        fail("outcome requires a non-empty event log")
    final_event = events[-1]
    if final_event["event_type"] != "ITERATION_FINALIZED":
        fail("outcome requires ITERATION_FINALIZED as final event")

    require_exact_keys(outcome, OUTCOME_FIELDS, "outcome")
    if outcome["schema_version"] != 1:
        fail("outcome.schema_version must be 1")
    expected_id = f"OUTCOME-{plan['plan_id']}"
    if outcome["outcome_id"] != expected_id:
        fail("outcome.outcome_id must be deterministic from plan_id")
    if outcome["request_id"] != request_id:
        fail("outcome.request_id mismatch")
    if outcome["iteration"] != plan["iteration"]:
        fail("outcome.iteration does not match sealed plan")
    if outcome["plan_id"] != plan["plan_id"]:
        fail("outcome.plan_id does not match sealed plan")
    if outcome["lease_id"] != lease["lease_id"]:
        fail("outcome.lease_id does not match released lease")
    if outcome["release_id"] != release["release_id"]:
        fail("outcome.release_id does not match lease release")
    if outcome["validation_report_id"] != validation_report["report_id"]:
        fail("outcome.validation_report_id does not match Validator PASS")
    if outcome["finalizer_role"] != "FINALIZER":
        fail("outcome.finalizer_role must be FINALIZER")
    if outcome["state"] != "DONE":
        fail("outcome.state must be DONE")
    if outcome["base_sha"] != plan["base_sha"]:
        fail("outcome.base_sha does not match sealed plan")
    if outcome["sealed_plan_sha256"] != canonical_sha256(plan):
        fail("outcome.sealed_plan_sha256 does not bind exact sealed plan")
    if outcome["final_event_sha256"] != final_event["event_sha256"]:
        fail("outcome.final_event_sha256 does not bind final event")
    if final_event["actor_role"] != "FINALIZER":
        fail("outcome final event must be emitted by FINALIZER")
    if final_event["payload_ref"] != f"outcome:{expected_id}":
        fail("outcome final event payload_ref does not reference outcome")


def build_outcome(
    request_id: str,
    events: list[dict[str, Any]],
    plan: dict[str, Any],
    lease: dict[str, Any],
    validation_report: dict[str, Any],
    release: dict[str, Any],
    *,
    contracts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    final_state, hard_stopped = validate_event_log(events, request_id)
    if final_state != "DONE" or hard_stopped:
        fail("cannot build outcome before successful DONE lifecycle")
    outcome = {
        "schema_version": 1,
        "outcome_id": f"OUTCOME-{plan['plan_id']}",
        "request_id": request_id,
        "iteration": plan["iteration"],
        "plan_id": plan["plan_id"],
        "lease_id": lease["lease_id"],
        "release_id": release["release_id"],
        "validation_report_id": validation_report["report_id"],
        "finalizer_role": "FINALIZER",
        "state": "DONE",
        "base_sha": plan["base_sha"],
        "sealed_plan_sha256": canonical_sha256(plan),
        "final_event_sha256": events[-1]["event_sha256"],
    }
    validate_outcome(
        outcome,
        request_id,
        events,
        plan,
        lease,
        validation_report,
        release,
        contracts=contracts,
    )
    return outcome


def finalize_success(
    events: list[dict[str, Any]],
    request_id: str,
    plan: dict[str, Any],
    lease: dict[str, Any],
    validation_report: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    state, stopped = validate_event_log(events, request_id)
    if stopped:
        fail("cannot finalize a HARD_STOP event chain")
    if state != "PASSED":
        fail(f"finalization requires PASSED lifecycle state, got {state}")
    release = release_write_lease(plan, lease, validation_report)
    finalized_events = append_event(
        events,
        request_id,
        "FINALIZATION_STARTED",
        "FINALIZER",
        f"release:{release['release_id']}",
    )
    outcome_id = f"OUTCOME-{plan['plan_id']}"
    finalized_events = append_event(
        finalized_events,
        request_id,
        "ITERATION_FINALIZED",
        "FINALIZER",
        f"outcome:{outcome_id}",
    )
    outcome = build_outcome(
        request_id,
        finalized_events,
        plan,
        lease,
        validation_report,
        release,
    )
    return finalized_events, release, outcome


def authorize_after_release(
    next_plan: dict[str, Any],
    prior_plan: dict[str, Any],
    prior_lease: dict[str, Any],
    prior_validation_report: dict[str, Any],
    release: dict[str, Any],
) -> dict[str, Any]:
    validate_lease_release(
        release,
        prior_plan,
        prior_lease,
        prior_validation_report,
    )
    return authorize_write_lease(next_plan)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate or create Control Plane V2 SHADOW finalization artifacts."
    )
    parser.add_argument("plan", type=Path)
    parser.add_argument("lease", type=Path)
    parser.add_argument("validation_report", type=Path)
    args = parser.parse_args()
    try:
        release = release_write_lease(
            load_json(args.plan),
            load_json(args.lease),
            load_json(args.validation_report),
        )
        print(json.dumps(release, ensure_ascii=False, sort_keys=True))
        print("CONTROL PLANE SHADOW FINALIZATION: GRÜN")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"CONTROL PLANE SHADOW FINALIZATION: ROT · {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
