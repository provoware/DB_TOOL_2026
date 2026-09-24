from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.control_plane_shadow import (
    authorize_write_lease,
    validate_execution_result,
    validate_sealed_plan,
    validate_validation_report,
)


BASE_SHA = "dd2b84c81cd26729dcef2b1202a328216e65a44b"


def sample_plan() -> dict:
    return {
        "plan_schema_version": 1,
        "plan_id": "PLAN-I999-SHADOW",
        "iteration": 999,
        "base_sha": BASE_SHA,
        "state": "SEALED",
        "goal": "Shadow-Plan fuer kollisionsfreie Mask-Builder-Arbeit pruefen.",
        "creator_role": "CREATOR",
        "write_files": [
            "src/provoware_db/mask_builder/browser_shell.py",
        ],
        "read_files": [
            ".provoware/control/registry.json",
            "tests/mask_builder/test_browser_shell.py",
        ],
        "forbidden_files": [
            "src/provoware_db/domain/models.py",
        ],
        "preserve_capabilities": [
            "MASK_PROPERTIES_V1",
        ],
        "acceptance_criteria": [
            "Scope bleibt innerhalb des versiegelten Plans.",
        ],
        "tests_required": [
            "gezielter Mask-Builder-Gate",
        ],
        "side_requests": [
            {
                "request_id": "REQ-LATER-001",
                "disposition": "DEFER",
            }
        ],
    }


def sample_result(plan: dict, lease: dict) -> dict:
    return {
        "result_schema_version": 1,
        "plan_id": plan["plan_id"],
        "lease_id": lease["lease_id"],
        "base_sha": plan["base_sha"],
        "creator_role": "CREATOR",
        "state": "EXECUTION_COMPLETE",
        "changed_files": list(plan["write_files"]),
        "acceptance_results": [
            {"criterion": item, "status": "PASS"}
            for item in plan["acceptance_criteria"]
        ],
        "test_results": [
            {"test": item, "status": "PASS"}
            for item in plan["tests_required"]
        ],
        "preserved_capabilities": [
            {"capability": item, "status": "PASS"}
            for item in plan["preserve_capabilities"]
        ],
        "unexpected_side_effects": [],
    }


def expect_invalid(plan: dict, marker: str, active_lease: dict | None = None) -> None:
    try:
        if active_lease is None:
            validate_sealed_plan(plan)
        else:
            authorize_write_lease(plan, active_lease=active_lease)
    except ValueError as exc:
        if marker not in str(exc):
            raise AssertionError(f"expected {marker!r} in {str(exc)!r}") from exc
    else:
        raise AssertionError(f"expected failure containing {marker!r}")


def test_sealed_plan_is_valid_and_grants_deterministic_creator_lease() -> None:
    plan = sample_plan()
    validate_sealed_plan(plan)
    lease = authorize_write_lease(plan)
    assert lease == {
        "schema_version": 1,
        "lease_id": "LEASE-PLAN-I999-SHADOW",
        "plan_id": "PLAN-I999-SHADOW",
        "base_sha": BASE_SHA,
        "holder": "CREATOR",
        "write_files": ["src/provoware_db/mask_builder/browser_shell.py"],
        "state": "ACTIVE",
    }


def test_second_active_global_writer_is_blocked() -> None:
    plan = sample_plan()
    active = authorize_write_lease(plan)

    second = sample_plan()
    second["plan_id"] = "PLAN-I1000-SHADOW"
    second["iteration"] = 1000
    expect_invalid(second, "global write lease already active", active_lease=active)


def test_frozen_or_unregistered_write_paths_are_blocked() -> None:
    plan = sample_plan()
    plan["write_files"] = ["src/provoware_db/domain/models.py"]
    plan["forbidden_files"] = []
    expect_invalid(plan, "write blocked by path policy")

    plan = sample_plan()
    plan["write_files"] = ["src/provoware_db/unknown/new_module.py"]
    expect_invalid(plan, "has no control-plane rule")


def test_plan_must_be_sealed_and_creator_owned() -> None:
    plan = sample_plan()
    plan["state"] = "DRAFT"
    expect_invalid(plan, "must be SEALED")

    plan = sample_plan()
    plan["creator_role"] = "PLANNER"
    expect_invalid(plan, "creator_role must be CREATOR")


def test_stable_capability_preservation_is_mandatory() -> None:
    plan = sample_plan()
    plan["preserve_capabilities"] = []
    expect_invalid(plan, "must preserve capabilities: MASK_PROPERTIES_V1")


def test_side_requests_cannot_expand_current_execution_scope() -> None:
    plan = sample_plan()
    plan["side_requests"][0]["disposition"] = "EXECUTE"
    expect_invalid(plan, "side requests must be DEFER")


def test_forbidden_file_cannot_also_be_writable() -> None:
    plan = sample_plan()
    plan["forbidden_files"] = ["src/provoware_db/mask_builder/browser_shell.py"]
    expect_invalid(plan, "write_files intersects plan.forbidden_files")



def test_matching_execution_result_produces_read_only_validator_pass() -> None:
    plan = sample_plan()
    lease = authorize_write_lease(plan)
    report = validate_execution_result(plan, lease, sample_result(plan, lease))
    assert report == {
        "schema_version": 1,
        "report_id": "VALIDATION-PLAN-I999-SHADOW",
        "plan_id": "PLAN-I999-SHADOW",
        "lease_id": "LEASE-PLAN-I999-SHADOW",
        "validator_role": "VALIDATOR",
        "verdict": "PASS",
        "findings": [],
    }
    validate_validation_report(report, plan, lease)


def test_unplanned_or_forbidden_file_produces_fail_report() -> None:
    plan = sample_plan()
    lease = authorize_write_lease(plan)
    result = sample_result(plan, lease)
    result["changed_files"].append("src/provoware_db/domain/models.py")
    report = validate_execution_result(plan, lease, result)
    assert report["verdict"] == "FAIL"
    assert any(item.startswith("UNPLANNED_FILES:") for item in report["findings"])
    assert any(item.startswith("FORBIDDEN_FILES_CHANGED:") for item in report["findings"])


def test_failed_or_missing_acceptance_and_tests_are_reported() -> None:
    plan = sample_plan()
    lease = authorize_write_lease(plan)
    result = sample_result(plan, lease)
    result["acceptance_results"][0]["status"] = "FAIL"
    result["test_results"] = []
    report = validate_execution_result(plan, lease, result)
    assert report["verdict"] == "FAIL"
    assert any(item.startswith("ACCEPTANCE_FAILED:") for item in report["findings"])
    assert any(item.startswith("TEST_SET_MISMATCH:") for item in report["findings"])


def test_capability_regression_or_side_effect_fails_validation() -> None:
    plan = sample_plan()
    lease = authorize_write_lease(plan)
    result = sample_result(plan, lease)
    result["preserved_capabilities"][0]["status"] = "FAIL"
    result["unexpected_side_effects"] = ["unexpected network write"]
    report = validate_execution_result(plan, lease, result)
    assert report["verdict"] == "FAIL"
    assert "CAPABILITY_REGRESSION:MASK_PROPERTIES_V1" in report["findings"]
    assert "UNEXPECTED_SIDE_EFFECTS:unexpected network write" in report["findings"]


def test_execution_identity_must_match_sealed_plan_and_lease() -> None:
    plan = sample_plan()
    lease = authorize_write_lease(plan)
    result = sample_result(plan, lease)
    result["lease_id"] = "LEASE-WRONG"
    try:
        validate_execution_result(plan, lease, result)
    except ValueError as exc:
        assert "lease_id does not match active lease" in str(exc)
    else:
        raise AssertionError("mismatched execution lease must fail closed")


def test_validator_report_cannot_claim_pass_with_findings() -> None:
    plan = sample_plan()
    lease = authorize_write_lease(plan)
    report = {
        "schema_version": 1,
        "report_id": "VALIDATION-PLAN-I999-SHADOW",
        "plan_id": plan["plan_id"],
        "lease_id": lease["lease_id"],
        "validator_role": "VALIDATOR",
        "verdict": "PASS",
        "findings": ["should-not-exist"],
    }
    try:
        validate_validation_report(report, plan, lease)
    except ValueError as exc:
        assert "PASS validation report may not contain findings" in str(exc)
    else:
        raise AssertionError("PASS report with findings must fail closed")

def main() -> None:
    test_sealed_plan_is_valid_and_grants_deterministic_creator_lease()
    test_second_active_global_writer_is_blocked()
    test_frozen_or_unregistered_write_paths_are_blocked()
    test_plan_must_be_sealed_and_creator_owned()
    test_stable_capability_preservation_is_mandatory()
    test_side_requests_cannot_expand_current_execution_scope()
    test_forbidden_file_cannot_also_be_writable()
    test_matching_execution_result_produces_read_only_validator_pass()
    test_unplanned_or_forbidden_file_produces_fail_report()
    test_failed_or_missing_acceptance_and_tests_are_reported()
    test_capability_regression_or_side_effect_fails_validation()
    test_execution_identity_must_match_sealed_plan_and_lease()
    test_validator_report_cannot_claim_pass_with_findings()
    print("CONTROL PLANE V2 SHADOW PLAN/LEASE/VALIDATION I121 STEP 2: GRÜN")


if __name__ == "__main__":
    main()
