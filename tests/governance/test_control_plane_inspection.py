from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.control_plane_inspection import (
    build_finding_bundle,
    required_inspectors,
    validate_inspection_report,
    validate_request,
)


def sample_request() -> dict:
    return {
        "schema_version": 1,
        "request_id": "REQ-I122-SHADOW",
        "state": "REQUESTED",
        "summary": "Mask-Builder UI und Testvertrag im Shadow Mode pruefen.",
        "candidate_files": [
            "src/provoware_db/mask_builder/browser_shell.py",
            "tests/mask_builder/test_browser_shell.py",
        ],
        "signals": ["UI", "FOCUS", "TESTS"],
        "side_requests": [
            {
                "request_id": "REQ-LATER-122",
                "summary": "README spaeter aus der Registry synchronisieren.",
                "disposition": "DEFER",
            }
        ],
    }


def report(kind: str, findings: list[dict] | None = None) -> dict:
    return {
        "schema_version": 1,
        "report_id": f"AUDIT-{kind}-I122",
        "request_id": "REQ-I122-SHADOW",
        "inspector_role": "INSPECTOR",
        "inspector_kind": kind,
        "state": "AUDIT_COMPLETE",
        "files_read": ["src/provoware_db/mask_builder/browser_shell.py"],
        "findings": [] if findings is None else findings,
    }


def finding(fid: str, root: str, severity: str = "MEDIUM") -> dict:
    return {
        "finding_id": fid,
        "severity": severity,
        "category": "TEST_CONTRACT",
        "root_cause_key": root,
        "summary": "Veraltete Assertion derselben Root Cause.",
        "evidence": "Gezielte read-only Pruefung hat denselben Selektorvertrag gefunden.",
        "affected_files": ["tests/mask_builder/test_browser_shell.py"],
    }


def expect_invalid(fn, marker: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert marker in str(exc), (marker, str(exc))
    else:
        raise AssertionError(f"expected failure containing {marker!r}")


def test_trigger_selection_is_deterministic_and_read_only() -> None:
    request = sample_request()
    validate_request(request)
    assert required_inspectors(request) == [
        "ACCESSIBILITY",
        "GENERAL",
        "TEST_DESIGN",
    ]


def test_security_and_frozen_inspectors_are_triggered_only_by_matching_signals() -> None:
    request = sample_request()
    request["signals"] = ["DEPENDENCY", "FROZEN_CORE", "SCHEMA"]
    assert required_inspectors(request) == [
        "FROZEN_CORE",
        "GENERAL",
        "SECURITY",
    ]


def test_untriggered_inspector_report_is_rejected() -> None:
    request = sample_request()
    unexpected = report("SECURITY")
    expect_invalid(
        lambda: validate_inspection_report(unexpected, request),
        "was not triggered by request",
    )


def test_inspector_contract_has_no_product_write_surface() -> None:
    request = sample_request()
    item = report("GENERAL")
    item["write_files"] = ["src/provoware_db/mask_builder/browser_shell.py"]
    expect_invalid(
        lambda: validate_inspection_report(item, request),
        "unknown keys",
    )


def test_side_requests_are_deferred_before_planning() -> None:
    request = sample_request()
    request["side_requests"][0]["disposition"] = "EXECUTE"
    expect_invalid(
        lambda: validate_request(request),
        "side requests must remain DEFER",
    )


def test_finding_bundle_requires_every_triggered_inspector() -> None:
    request = sample_request()
    reports = [report("GENERAL"), report("ACCESSIBILITY")]
    expect_invalid(
        lambda: build_finding_bundle(request, reports),
        "inspection set incomplete",
    )


def test_bundle_groups_same_root_cause_without_merging_findings() -> None:
    request = sample_request()
    reports = [
        report("GENERAL", [finding("F-I122-GEN-001", "width-selector-drift")]),
        report("ACCESSIBILITY", [finding("F-I122-A11Y-001", "width-selector-drift")]),
        report("TEST_DESIGN", [finding("F-I122-TEST-001", "width-selector-drift")]),
    ]
    bundle = build_finding_bundle(request, reports)
    assert bundle["state"] == "FINDINGS_READY"
    assert bundle["required_inspectors"] == [
        "ACCESSIBILITY",
        "GENERAL",
        "TEST_DESIGN",
    ]
    assert bundle["completed_inspectors"] == bundle["required_inspectors"]
    assert len(bundle["findings"]) == 3
    assert bundle["root_causes"] == [
        {
            "root_cause_key": "width-selector-drift",
            "finding_ids": [
                "F-I122-A11Y-001",
                "F-I122-GEN-001",
                "F-I122-TEST-001",
            ],
        }
    ]


def test_duplicate_finding_ids_fail_closed() -> None:
    request = sample_request()
    duplicate = finding("F-I122-DUP-001", "same-root")
    reports = [
        report("GENERAL", [deepcopy(duplicate)]),
        report("ACCESSIBILITY", [deepcopy(duplicate)]),
        report("TEST_DESIGN"),
    ]
    expect_invalid(
        lambda: build_finding_bundle(request, reports),
        "duplicate finding_id across reports",
    )


def main() -> None:
    test_trigger_selection_is_deterministic_and_read_only()
    test_security_and_frozen_inspectors_are_triggered_only_by_matching_signals()
    test_untriggered_inspector_report_is_rejected()
    test_inspector_contract_has_no_product_write_surface()
    test_side_requests_are_deferred_before_planning()
    test_finding_bundle_requires_every_triggered_inspector()
    test_bundle_groups_same_root_cause_without_merging_findings()
    test_duplicate_finding_ids_fail_closed()
    print("CONTROL PLANE V2 SHADOW INSPECTION I122 STEP 1: GRÜN")


if __name__ == "__main__":
    main()
