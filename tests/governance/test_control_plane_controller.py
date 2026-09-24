from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.control_plane_controller import (
    canonical_sha256,
    seal_draft_plan,
    validate_controller_decision,
)
from scripts.control_plane_inspection import (
    build_finding_bundle,
    build_planner_input,
)
from scripts.control_plane_shadow import authorize_write_lease


BASE_SHA = "dc33925a5bb42f6a15c8e5d4512705a615dc72fb"


def request() -> dict:
    return {
        "schema_version": 1,
        "request_id": "REQ-I123-SHADOW",
        "state": "REQUESTED",
        "summary": "Controller-Handoff fuer einen kleinen Mask-Builder-Repair pruefen.",
        "candidate_files": [
            "src/provoware_db/mask_builder/browser_shell.py",
            "tests/mask_builder/test_browser_shell.py",
        ],
        "signals": [],
        "side_requests": [
            {
                "request_id": "REQ-LATER-I123",
                "summary": "Spaetere Produktidee bleibt ausserhalb des laufenden Plans.",
                "disposition": "DEFER",
            }
        ],
    }


def finding() -> dict:
    return {
        "finding_id": "F-I123-GEN-001",
        "severity": "MEDIUM",
        "category": "TEST_CONTRACT",
        "root_cause_key": "sample-repair",
        "summary": "Beispiel-Finding fuer Controller-Handoff.",
        "evidence": "Read-only Inspector-Evidence.",
        "affected_files": ["tests/mask_builder/test_browser_shell.py"],
    }


def report() -> dict:
    return {
        "schema_version": 1,
        "report_id": "AUDIT-GENERAL-I123",
        "request_id": "REQ-I123-SHADOW",
        "inspector_role": "INSPECTOR",
        "inspector_kind": "GENERAL",
        "state": "AUDIT_COMPLETE",
        "files_read": ["tests/mask_builder/test_browser_shell.py"],
        "findings": [finding()],
    }


def artifacts() -> tuple[dict, dict, dict, dict]:
    req = request()
    bundle = build_finding_bundle(req, [report()])
    planner_input = build_planner_input(req, bundle)
    draft = {
        "plan_schema_version": 1,
        "plan_id": "PLAN-I123-SHADOW",
        "iteration": 123,
        "base_sha": BASE_SHA,
        "state": "DRAFT",
        "planner_role": "PLANNER",
        "creator_role": "CREATOR",
        "source_planner_input_id": planner_input["input_id"],
        "goal": "Eine geplante Aenderung mit Source und Regressionstest versiegeln.",
        "proposed_write_files": [
            "src/provoware_db/mask_builder/browser_shell.py",
            "tests/mask_builder/test_browser_shell.py",
        ],
        "proposed_read_files": [
            ".provoware/control/registry.json",
        ],
        "forbidden_files": [
            "src/provoware_db/domain/models.py",
        ],
        "preserve_capabilities": [
            "MASK_PROPERTIES_V1",
        ],
        "acceptance_criteria": [
            "Scope entspricht exakt dem Planner-Draft.",
        ],
        "tests_required": [
            "gezielter Mask-Builder-Test",
        ],
        "finding_actions": [
            {
                "finding_id": "F-I123-GEN-001",
                "disposition": "PLAN",
                "rationale": "Finding wird in der geplanten Iteration behandelt.",
            }
        ],
        "side_requests": list(planner_input["side_requests"]),
    }
    return req, bundle, planner_input, draft


def expect_invalid(fn, marker: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert marker in str(exc), (marker, str(exc))
    else:
        raise AssertionError(f"expected failure containing {marker!r}")


def test_controller_seals_exact_draft_and_binds_it_by_digest() -> None:
    req, bundle, planner_input, draft = artifacts()
    decision, sealed = seal_draft_plan(
        req,
        bundle,
        planner_input,
        draft,
        expected_base_sha=BASE_SHA,
    )
    assert sealed["state"] == "SEALED"
    assert sealed["write_files"] == draft["proposed_write_files"]
    assert sealed["read_files"] == draft["proposed_read_files"]
    assert decision["state"] == "PLAN_SEALED"
    assert decision["controller_role"] == "CONTROLLER"
    assert decision["sealed_plan_sha256"] == canonical_sha256(sealed)
    assert decision["approved_finding_ids"] == ["F-I123-GEN-001"]
    validate_controller_decision(decision, sealed, planner_input)


def test_registered_test_path_can_share_creator_scope_with_product_code() -> None:
    req, bundle, planner_input, draft = artifacts()
    _, sealed = seal_draft_plan(
        req,
        bundle,
        planner_input,
        draft,
        expected_base_sha=BASE_SHA,
    )
    assert "tests/mask_builder/test_browser_shell.py" in sealed["write_files"]


def test_stale_base_sha_fails_before_sealing() -> None:
    req, bundle, planner_input, draft = artifacts()
    expect_invalid(
        lambda: seal_draft_plan(
            req,
            bundle,
            planner_input,
            draft,
            expected_base_sha="a" * 40,
        ),
        "base_sha is stale",
    )


def test_frozen_write_path_is_rejected_by_existing_i121_guard() -> None:
    req, bundle, planner_input, draft = artifacts()
    draft["proposed_write_files"] = ["src/provoware_db/domain/models.py"]
    draft["forbidden_files"] = []
    expect_invalid(
        lambda: seal_draft_plan(
            req,
            bundle,
            planner_input,
            draft,
            expected_base_sha=BASE_SHA,
        ),
        "write blocked by path policy",
    )


def test_stable_capability_cannot_be_dropped() -> None:
    req, bundle, planner_input, draft = artifacts()
    draft["preserve_capabilities"] = []
    expect_invalid(
        lambda: seal_draft_plan(
            req,
            bundle,
            planner_input,
            draft,
            expected_base_sha=BASE_SHA,
        ),
        "must preserve capabilities: MASK_PROPERTIES_V1",
    )


def test_controller_does_not_bypass_global_single_writer_lease() -> None:
    req, bundle, planner_input, draft = artifacts()
    _, sealed = seal_draft_plan(
        req,
        bundle,
        planner_input,
        draft,
        expected_base_sha=BASE_SHA,
    )
    first = authorize_write_lease(sealed)
    expect_invalid(
        lambda: authorize_write_lease(sealed, active_lease=first),
        "global write lease already active",
    )


def test_controller_decision_detects_sealed_plan_tampering() -> None:
    req, bundle, planner_input, draft = artifacts()
    decision, sealed = seal_draft_plan(
        req,
        bundle,
        planner_input,
        draft,
        expected_base_sha=BASE_SHA,
    )
    tampered = deepcopy(sealed)
    tampered["goal"] = "Manipulierter Plan"
    expect_invalid(
        lambda: validate_controller_decision(decision, tampered, planner_input),
        "does not bind exact sealed plan",
    )


def main() -> None:
    test_controller_seals_exact_draft_and_binds_it_by_digest()
    test_registered_test_path_can_share_creator_scope_with_product_code()
    test_stale_base_sha_fails_before_sealing()
    test_frozen_write_path_is_rejected_by_existing_i121_guard()
    test_stable_capability_cannot_be_dropped()
    test_controller_does_not_bypass_global_single_writer_lease()
    test_controller_decision_detects_sealed_plan_tampering()
    print("CONTROL PLANE V2 SHADOW CONTROLLER I123 STEP 1: GRÜN")


if __name__ == "__main__":
    main()
