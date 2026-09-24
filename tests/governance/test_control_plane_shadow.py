from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.control_plane_shadow import authorize_write_lease, validate_sealed_plan


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


def main() -> None:
    test_sealed_plan_is_valid_and_grants_deterministic_creator_lease()
    test_second_active_global_writer_is_blocked()
    test_frozen_or_unregistered_write_paths_are_blocked()
    test_plan_must_be_sealed_and_creator_owned()
    test_stable_capability_preservation_is_mandatory()
    test_side_requests_cannot_expand_current_execution_scope()
    test_forbidden_file_cannot_also_be_writable()
    print("CONTROL PLANE V2 SHADOW PLAN/LEASE I121 STEP 1: GRÜN")


if __name__ == "__main__":
    main()
