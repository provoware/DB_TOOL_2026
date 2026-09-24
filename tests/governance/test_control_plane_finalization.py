from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.control_plane_events import append_event, validate_event_log
from scripts.control_plane_finalization import (
    authorize_after_release,
    finalize_success,
    release_write_lease,
    validate_lease_release,
    validate_outcome,
)
from scripts.control_plane_shadow import (
    authorize_write_lease,
    validate_execution_result,
)


BASE_SHA = "8a57a7555e249f20b05bd991ec6cc7d0b5e5e61f"
REQUEST_ID = "REQ-I124-SHADOW"


def plan() -> dict:
    return {
        "plan_schema_version": 1,
        "plan_id": "PLAN-I124-SHADOW",
        "iteration": 124,
        "base_sha": BASE_SHA,
        "state": "SEALED",
        "goal": "Shadow-Finalizer pruefen.",
        "creator_role": "CREATOR",
        "write_files": ["tests/mask_builder/test_browser_shell.py"],
        "read_files": [".provoware/control/registry.json"],
        "forbidden_files": ["src/provoware_db/domain/models.py"],
        "preserve_capabilities": [],
        "acceptance_criteria": ["Creator-Scope bleibt exakt."],
        "tests_required": ["gezielter Test"],
        "side_requests": [{"request_id": "REQ-LATER-I124", "disposition": "DEFER"}],
    }


def passing_result(current_plan: dict, lease: dict) -> dict:
    return {
        "result_schema_version": 1,
        "plan_id": current_plan["plan_id"],
        "lease_id": lease["lease_id"],
        "base_sha": current_plan["base_sha"],
        "creator_role": "CREATOR",
        "state": "EXECUTION_COMPLETE",
        "changed_files": list(current_plan["write_files"]),
        "acceptance_results": [
            {"criterion": item, "status": "PASS"}
            for item in current_plan["acceptance_criteria"]
        ],
        "test_results": [
            {"test": item, "status": "PASS"}
            for item in current_plan["tests_required"]
        ],
        "preserved_capabilities": [],
        "unexpected_side_effects": [],
    }


def expect_invalid(fn, marker: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert marker in str(exc), (marker, str(exc))
    else:
        raise AssertionError(f"expected failure containing {marker!r}")


def pass_artifacts() -> tuple[dict, dict, dict]:
    current_plan = plan()
    lease = authorize_write_lease(current_plan)
    report = validate_execution_result(
        current_plan,
        lease,
        passing_result(current_plan, lease),
    )
    assert report["verdict"] == "PASS"
    return current_plan, lease, report


def event_prefix_to_execution() -> list[dict]:
    events: list[dict] = []
    events = append_event(events, REQUEST_ID, "REQUEST_CREATED", "INSPECTOR", "request:I124")
    events = append_event(events, REQUEST_ID, "AUDIT_COMPLETE", "INSPECTOR", "bundle:I124")
    events = append_event(events, REQUEST_ID, "FINDINGS_READY", "PLANNER", "planner:I124")
    events = append_event(events, REQUEST_ID, "PLAN_SUBMITTED", "PLANNER", "draft:I124")
    events = append_event(events, REQUEST_ID, "PLAN_SEALED", "CONTROLLER", "seal:I124")
    events = append_event(events, REQUEST_ID, "WRITE_LEASE_GRANTED", "CONTROLLER", "lease:I124")
    state, stopped = validate_event_log(events, REQUEST_ID)
    assert state == "EXECUTING"
    assert stopped is False
    return events


def pass_event_log(report: dict) -> list[dict]:
    events = event_prefix_to_execution()
    events = append_event(events, REQUEST_ID, "EXECUTION_COMPLETE", "CREATOR", "result:I124")
    events = append_event(events, REQUEST_ID, "VALIDATION_STARTED", "VALIDATOR", "validation:start")
    events = append_event(
        events,
        REQUEST_ID,
        "VALIDATION_PASSED",
        "VALIDATOR",
        f"validation:{report['report_id']}",
    )
    state, stopped = validate_event_log(events, REQUEST_ID)
    assert state == "PASSED"
    assert stopped is False
    return events


def test_finalizer_releases_only_matching_passed_lease() -> None:
    current_plan, lease, report = pass_artifacts()
    release = release_write_lease(current_plan, lease, report)
    assert release["state"] == "RELEASED"
    assert release["finalizer_role"] == "FINALIZER"
    assert release["lease_id"] == lease["lease_id"]
    assert release["validation_report_id"] == report["report_id"]
    validate_lease_release(release, current_plan, lease, report)


def test_validator_fail_cannot_release_global_writer() -> None:
    current_plan = plan()
    lease = authorize_write_lease(current_plan)
    result = passing_result(current_plan, lease)
    result["test_results"][0]["status"] = "FAIL"
    report = validate_execution_result(current_plan, lease, result)
    assert report["verdict"] == "FAIL"
    expect_invalid(
        lambda: release_write_lease(current_plan, lease, report),
        "only Validator PASS may release",
    )


def test_mismatched_validation_identity_cannot_release() -> None:
    current_plan, lease, report = pass_artifacts()
    wrong_report = deepcopy(report)
    wrong_report["lease_id"] = "LEASE-WRONG"
    expect_invalid(
        lambda: release_write_lease(current_plan, lease, wrong_report),
        "lease_id does not match lease",
    )


def test_release_is_bound_to_exact_sealed_plan() -> None:
    current_plan, lease, report = pass_artifacts()
    release = release_write_lease(current_plan, lease, report)
    tampered_plan = deepcopy(current_plan)
    tampered_plan["goal"] = "Manipulierter Plan"
    expect_invalid(
        lambda: validate_lease_release(release, tampered_plan, lease, report),
        "sealed_plan_sha256 does not bind exact sealed plan",
    )


def test_only_finalizer_identity_is_accepted() -> None:
    current_plan, lease, report = pass_artifacts()
    release = release_write_lease(current_plan, lease, report)
    release["finalizer_role"] = "CREATOR"
    expect_invalid(
        lambda: validate_lease_release(release, current_plan, lease, report),
        "finalizer_role must be FINALIZER",
    )


def test_pass_lifecycle_reaches_done_and_outcome_binds_final_event() -> None:
    current_plan, lease, report = pass_artifacts()
    events = pass_event_log(report)
    events, release, outcome = finalize_success(
        events,
        REQUEST_ID,
        current_plan,
        lease,
        report,
    )
    state, stopped = validate_event_log(events, REQUEST_ID)
    assert state == "DONE"
    assert stopped is False
    assert events[-2]["event_type"] == "FINALIZATION_STARTED"
    assert events[-1]["event_type"] == "ITERATION_FINALIZED"
    assert outcome["state"] == "DONE"
    assert outcome["final_event_sha256"] == events[-1]["event_sha256"]
    assert events[-1]["payload_ref"] == f"outcome:{outcome['outcome_id']}"
    validate_outcome(
        outcome,
        REQUEST_ID,
        events,
        current_plan,
        lease,
        report,
        release,
    )


def test_validation_fail_returns_to_planner_and_cannot_finalize() -> None:
    current_plan = plan()
    lease = authorize_write_lease(current_plan)
    result = passing_result(current_plan, lease)
    result["test_results"][0]["status"] = "FAIL"
    report = validate_execution_result(current_plan, lease, result)
    assert report["verdict"] == "FAIL"

    events = event_prefix_to_execution()
    events = append_event(events, REQUEST_ID, "EXECUTION_COMPLETE", "CREATOR", "result:fail")
    events = append_event(events, REQUEST_ID, "VALIDATION_STARTED", "VALIDATOR", "validation:start")
    events = append_event(events, REQUEST_ID, "VALIDATION_FAILED", "VALIDATOR", "validation:fail")
    state, _ = validate_event_log(events, REQUEST_ID)
    assert state == "FAILED"
    events = append_event(events, REQUEST_ID, "REPLAN_REQUESTED", "PLANNER", "replan:I124")
    state, stopped = validate_event_log(events, REQUEST_ID)
    assert state == "PLANNING"
    assert stopped is False

    expect_invalid(
        lambda: release_write_lease(current_plan, lease, report),
        "only Validator PASS may release",
    )
    expect_invalid(
        lambda: finalize_success(events, REQUEST_ID, current_plan, lease, report),
        "finalization requires PASSED lifecycle state",
    )


def test_next_creator_authorization_requires_valid_prior_release() -> None:
    current_plan, lease, report = pass_artifacts()
    release = release_write_lease(current_plan, lease, report)

    next_plan = deepcopy(current_plan)
    next_plan["plan_id"] = "PLAN-I125-SHADOW"
    next_plan["iteration"] = 125
    next_plan["goal"] = "Naechste unabhaengige Shadow-Ausfuehrung."
    next_lease = authorize_after_release(
        next_plan,
        current_plan,
        lease,
        report,
        release,
    )
    assert next_lease["plan_id"] == "PLAN-I125-SHADOW"
    assert next_lease["state"] == "ACTIVE"

    tampered_release = deepcopy(release)
    tampered_release["sealed_plan_sha256"] = "0" * 64
    expect_invalid(
        lambda: authorize_after_release(
            next_plan,
            current_plan,
            lease,
            report,
            tampered_release,
        ),
        "does not bind exact sealed plan",
    )


def main() -> None:
    test_finalizer_releases_only_matching_passed_lease()
    test_validator_fail_cannot_release_global_writer()
    test_mismatched_validation_identity_cannot_release()
    test_release_is_bound_to_exact_sealed_plan()
    test_only_finalizer_identity_is_accepted()
    test_pass_lifecycle_reaches_done_and_outcome_binds_final_event()
    test_validation_fail_returns_to_planner_and_cannot_finalize()
    test_next_creator_authorization_requires_valid_prior_release()
    print("CONTROL PLANE V2 SHADOW FINALIZATION/OUTCOME I124 STEP 2: GRÜN")


if __name__ == "__main__":
    main()
