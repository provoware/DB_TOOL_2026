from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.control_plane_finalization import (
    release_write_lease,
    validate_lease_release,
)
from scripts.control_plane_shadow import (
    authorize_write_lease,
    validate_execution_result,
)


BASE_SHA = "8a57a7555e249f20b05bd991ec6cc7d0b5e5e61f"


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


def main() -> None:
    test_finalizer_releases_only_matching_passed_lease()
    test_validator_fail_cannot_release_global_writer()
    test_mismatched_validation_identity_cannot_release()
    test_release_is_bound_to_exact_sealed_plan()
    test_only_finalizer_identity_is_accepted()
    print("CONTROL PLANE V2 SHADOW FINALIZATION I124 STEP 1: GRÜN")


if __name__ == "__main__":
    main()
