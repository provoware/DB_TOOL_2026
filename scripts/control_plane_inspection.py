from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.validate_control_plane import (
    require_exact_keys,
    require_string,
    require_string_list,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACTS = ROOT / ".provoware" / "control" / "inspection_contracts.json"

REQUEST_FIELDS = {
    "schema_version",
    "request_id",
    "state",
    "summary",
    "candidate_files",
    "signals",
    "side_requests",
}
FINDING_FIELDS = {
    "finding_id",
    "severity",
    "category",
    "root_cause_key",
    "summary",
    "evidence",
    "affected_files",
}
REPORT_FIELDS = {
    "schema_version",
    "report_id",
    "request_id",
    "inspector_role",
    "inspector_kind",
    "state",
    "files_read",
    "findings",
}
BUNDLE_FIELDS = {
    "schema_version",
    "bundle_id",
    "request_id",
    "state",
    "required_inspectors",
    "completed_inspectors",
    "root_causes",
    "findings",
    "side_requests",
}
PLANNER_INPUT_FIELDS = {
    "schema_version",
    "input_id",
    "request_id",
    "bundle_id",
    "state",
    "planner_role",
    "root_causes",
    "findings",
    "side_requests",
}
DRAFT_PLAN_FIELDS = {
    "plan_schema_version",
    "plan_id",
    "iteration",
    "base_sha",
    "state",
    "planner_role",
    "creator_role",
    "source_planner_input_id",
    "goal",
    "proposed_write_files",
    "proposed_read_files",
    "forbidden_files",
    "preserve_capabilities",
    "acceptance_criteria",
    "tests_required",
    "finding_actions",
    "side_requests",
}
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")

ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9._:-]*$")


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path}: JSON root must be an object")
    return data


def safe_paths(values: Any, label: str) -> list[str]:
    result = require_string_list(values, label)
    for raw in result:
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts:
            fail(f"{label}: unsafe repository path {raw!r}")
    return result


def require_id(value: Any, label: str, prefix: str) -> str:
    text = require_string(value, label)
    if not text.startswith(prefix):
        fail(f"{label} must start with {prefix}")
    if not ID_RE.fullmatch(text):
        fail(f"{label} contains unsupported characters")
    return text


def validate_contracts(data: dict[str, Any]) -> None:
    require_exact_keys(
        data,
        {
            "schema_version",
            "mode",
            "inspector_role",
            "planner_role",
            "inspector_kinds",
            "allowed_signals",
            "severity_order",
            "trigger_map",
            "request_required_fields",
            "finding_required_fields",
            "inspection_report_required_fields",
            "finding_bundle_required_fields",
            "allowed_finding_dispositions",
            "planner_input_required_fields",
            "draft_plan_required_fields",
        },
        "inspection_contracts",
    )
    if data["schema_version"] != 1:
        fail("inspection_contracts.schema_version must be 1")
    if data["mode"] != "SHADOW":
        fail("inspection_contracts.mode must remain SHADOW")
    if data["inspector_role"] != "INSPECTOR":
        fail("inspection_contracts.inspector_role must be INSPECTOR")
    if data["planner_role"] != "PLANNER":
        fail("inspection_contracts.planner_role must be PLANNER")

    kinds = set(require_string_list(data["inspector_kinds"], "inspection_contracts.inspector_kinds"))
    if "GENERAL" not in kinds:
        fail("GENERAL inspector kind is required")
    signals = set(require_string_list(data["allowed_signals"], "inspection_contracts.allowed_signals"))
    severities = require_string_list(data["severity_order"], "inspection_contracts.severity_order")
    if severities != ["BLOCKER", "HIGH", "MEDIUM", "LOW", "INFO"]:
        fail("severity_order must be BLOCKER,HIGH,MEDIUM,LOW,INFO")
    dispositions = require_string_list(
        data["allowed_finding_dispositions"],
        "inspection_contracts.allowed_finding_dispositions",
    )
    if dispositions != ["PLAN", "DEFER", "ACCEPT_RISK", "DUPLICATE", "INVALID"]:
        fail("allowed_finding_dispositions must use the fixed shadow ordering")

    trigger_map = data["trigger_map"]
    if not isinstance(trigger_map, dict):
        fail("inspection_contracts.trigger_map must be an object")
    for inspector_kind, mapped_signals in trigger_map.items():
        if inspector_kind not in kinds or inspector_kind == "GENERAL":
            fail(f"trigger_map references invalid inspector kind {inspector_kind!r}")
        unknown = set(require_string_list(mapped_signals, f"trigger_map.{inspector_kind}")) - signals
        if unknown:
            fail(f"trigger_map.{inspector_kind} contains unknown signals: {sorted(unknown)}")

    expected_fields = (
        ("request_required_fields", REQUEST_FIELDS),
        ("finding_required_fields", FINDING_FIELDS),
        ("inspection_report_required_fields", REPORT_FIELDS),
        ("finding_bundle_required_fields", BUNDLE_FIELDS),
        ("planner_input_required_fields", PLANNER_INPUT_FIELDS),
        ("draft_plan_required_fields", DRAFT_PLAN_FIELDS),
    )
    for field_name, expected in expected_fields:
        actual = set(require_string_list(data[field_name], f"inspection_contracts.{field_name}"))
        if actual != expected:
            fail(f"{field_name} does not match the shadow artifact contract")


def validate_side_requests(values: Any) -> list[dict[str, str]]:
    if not isinstance(values, list):
        fail("request.side_requests: array required")
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for index, item in enumerate(values):
        if not isinstance(item, dict):
            fail(f"request.side_requests[{index}]: object required")
        require_exact_keys(
            item,
            {"request_id", "summary", "disposition"},
            f"request.side_requests[{index}]",
        )
        request_id = require_id(
            item["request_id"],
            f"request.side_requests[{index}].request_id",
            "REQ-",
        )
        if request_id in seen:
            fail(f"request.side_requests: duplicate request_id {request_id!r}")
        seen.add(request_id)
        summary = require_string(item["summary"], f"request.side_requests[{index}].summary")
        if item["disposition"] != "DEFER":
            fail("side requests must remain DEFER before planning")
        result.append(
            {
                "request_id": request_id,
                "summary": summary,
                "disposition": "DEFER",
            }
        )
    return result


def validate_request(
    request: dict[str, Any],
    contracts: dict[str, Any] | None = None,
) -> None:
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_contracts(contracts)
    require_exact_keys(request, REQUEST_FIELDS, "request")
    if request["schema_version"] != 1:
        fail("request.schema_version must be 1")
    require_id(request["request_id"], "request.request_id", "REQ-")
    if request["state"] != "REQUESTED":
        fail("request.state must be REQUESTED")
    require_string(request["summary"], "request.summary")
    safe_paths(request["candidate_files"], "request.candidate_files")
    signals = set(require_string_list(request["signals"], "request.signals"))
    unknown = signals - set(contracts["allowed_signals"])
    if unknown:
        fail("request.signals contains unknown signals: " + ", ".join(sorted(unknown)))
    validate_side_requests(request["side_requests"])


def required_inspectors(
    request: dict[str, Any],
    contracts: dict[str, Any] | None = None,
) -> list[str]:
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_request(request, contracts=contracts)
    signals = set(request["signals"])
    selected = {"GENERAL"}
    for inspector_kind, mapped_signals in contracts["trigger_map"].items():
        if signals.intersection(mapped_signals):
            selected.add(inspector_kind)
    return sorted(selected)


def validate_finding(
    finding: dict[str, Any],
    contracts: dict[str, Any],
    *,
    report_id: str,
) -> None:
    require_exact_keys(finding, FINDING_FIELDS, f"{report_id}.finding")
    require_id(finding["finding_id"], f"{report_id}.finding_id", "F-")
    if finding["severity"] not in contracts["severity_order"]:
        fail(f"{report_id}.finding severity is invalid")
    require_string(finding["category"], f"{report_id}.finding.category")
    require_string(finding["root_cause_key"], f"{report_id}.finding.root_cause_key")
    require_string(finding["summary"], f"{report_id}.finding.summary")
    require_string(finding["evidence"], f"{report_id}.finding.evidence")
    safe_paths(finding["affected_files"], f"{report_id}.finding.affected_files")


def validate_inspection_report(
    report: dict[str, Any],
    request: dict[str, Any],
    contracts: dict[str, Any] | None = None,
) -> None:
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_request(request, contracts=contracts)
    require_exact_keys(report, REPORT_FIELDS, "inspection_report")
    if report["schema_version"] != 1:
        fail("inspection_report.schema_version must be 1")
    report_id = require_id(report["report_id"], "inspection_report.report_id", "AUDIT-")
    if report["request_id"] != request["request_id"]:
        fail("inspection_report.request_id does not match request")
    if report["inspector_role"] != "INSPECTOR":
        fail("inspection_report.inspector_role must be INSPECTOR")
    if report["inspector_kind"] not in required_inspectors(request, contracts=contracts):
        fail("inspection_report.inspector_kind was not triggered by request")
    if report["state"] != "AUDIT_COMPLETE":
        fail("inspection_report.state must be AUDIT_COMPLETE")
    safe_paths(report["files_read"], "inspection_report.files_read")
    if not isinstance(report["findings"], list):
        fail("inspection_report.findings: array required")
    seen: set[str] = set()
    for finding in report["findings"]:
        if not isinstance(finding, dict):
            fail("inspection_report.findings[]: object required")
        validate_finding(finding, contracts, report_id=report_id)
        finding_id = finding["finding_id"]
        if finding_id in seen:
            fail(f"inspection_report duplicate finding_id {finding_id!r}")
        seen.add(finding_id)


def build_finding_bundle(
    request: dict[str, Any],
    reports: list[dict[str, Any]],
    contracts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_request(request, contracts=contracts)
    required = required_inspectors(request, contracts=contracts)
    by_kind: dict[str, dict[str, Any]] = {}
    findings_by_id: dict[str, dict[str, Any]] = {}
    root_causes: dict[str, list[str]] = {}

    for report in reports:
        validate_inspection_report(report, request, contracts=contracts)
        kind = report["inspector_kind"]
        if kind in by_kind:
            fail(f"duplicate inspection report for {kind}")
        by_kind[kind] = report
        for finding in report["findings"]:
            finding_id = finding["finding_id"]
            if finding_id in findings_by_id:
                fail(f"duplicate finding_id across reports: {finding_id}")
            findings_by_id[finding_id] = finding
            root_causes.setdefault(finding["root_cause_key"], []).append(finding_id)

    completed = sorted(by_kind)
    if completed != required:
        missing = sorted(set(required) - set(completed))
        extra = sorted(set(completed) - set(required))
        fail(f"inspection set incomplete: missing={missing}, extra={extra}")

    normalized_root_causes = [
        {
            "root_cause_key": key,
            "finding_ids": sorted(ids),
        }
        for key, ids in sorted(root_causes.items())
    ]
    bundle = {
        "schema_version": 1,
        "bundle_id": f"BUNDLE-{request['request_id']}",
        "request_id": request["request_id"],
        "state": "FINDINGS_READY",
        "required_inspectors": required,
        "completed_inspectors": completed,
        "root_causes": normalized_root_causes,
        "findings": [findings_by_id[key] for key in sorted(findings_by_id)],
        "side_requests": validate_side_requests(request["side_requests"]),
    }
    validate_finding_bundle(bundle, request, contracts=contracts)
    return bundle


def validate_finding_bundle(
    bundle: dict[str, Any],
    request: dict[str, Any],
    contracts: dict[str, Any] | None = None,
) -> None:
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_request(request, contracts=contracts)
    require_exact_keys(bundle, BUNDLE_FIELDS, "finding_bundle")
    if bundle["schema_version"] != 1:
        fail("finding_bundle.schema_version must be 1")
    if bundle["bundle_id"] != f"BUNDLE-{request['request_id']}":
        fail("finding_bundle.bundle_id must be deterministic from request_id")
    if bundle["request_id"] != request["request_id"]:
        fail("finding_bundle.request_id does not match request")
    if bundle["state"] != "FINDINGS_READY":
        fail("finding_bundle.state must be FINDINGS_READY")
    required = required_inspectors(request, contracts=contracts)
    if bundle["required_inspectors"] != required:
        fail("finding_bundle.required_inspectors mismatch")
    if bundle["completed_inspectors"] != required:
        fail("finding_bundle.completed_inspectors must equal required inspectors")
    if not isinstance(bundle["root_causes"], list):
        fail("finding_bundle.root_causes: array required")
    if not isinstance(bundle["findings"], list):
        fail("finding_bundle.findings: array required")
    validate_side_requests(bundle["side_requests"])



def build_planner_input(
    request: dict[str, Any],
    bundle: dict[str, Any],
    contracts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_finding_bundle(bundle, request, contracts=contracts)
    planner_input = {
        "schema_version": 1,
        "input_id": f"PLANNER-{bundle['bundle_id']}",
        "request_id": request["request_id"],
        "bundle_id": bundle["bundle_id"],
        "state": "FINDINGS_READY",
        "planner_role": "PLANNER",
        "root_causes": list(bundle["root_causes"]),
        "findings": list(bundle["findings"]),
        "side_requests": list(bundle["side_requests"]),
    }
    validate_planner_input(planner_input, request, bundle, contracts=contracts)
    return planner_input


def validate_planner_input(
    planner_input: dict[str, Any],
    request: dict[str, Any],
    bundle: dict[str, Any],
    contracts: dict[str, Any] | None = None,
) -> None:
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_finding_bundle(bundle, request, contracts=contracts)
    require_exact_keys(planner_input, PLANNER_INPUT_FIELDS, "planner_input")
    if planner_input["schema_version"] != 1:
        fail("planner_input.schema_version must be 1")
    if planner_input["input_id"] != f"PLANNER-{bundle['bundle_id']}":
        fail("planner_input.input_id must be deterministic from bundle_id")
    if planner_input["request_id"] != request["request_id"]:
        fail("planner_input.request_id does not match request")
    if planner_input["bundle_id"] != bundle["bundle_id"]:
        fail("planner_input.bundle_id does not match finding bundle")
    if planner_input["state"] != "FINDINGS_READY":
        fail("planner_input.state must be FINDINGS_READY")
    if planner_input["planner_role"] != "PLANNER":
        fail("planner_input.planner_role must be PLANNER")
    if planner_input["root_causes"] != bundle["root_causes"]:
        fail("planner_input.root_causes must exactly preserve finding bundle")
    if planner_input["findings"] != bundle["findings"]:
        fail("planner_input.findings must exactly preserve finding bundle")
    if planner_input["side_requests"] != bundle["side_requests"]:
        fail("planner_input.side_requests must exactly preserve deferred side requests")


def validate_finding_actions(
    values: Any,
    planner_input: dict[str, Any],
    contracts: dict[str, Any],
) -> None:
    if not isinstance(values, list):
        fail("draft_plan.finding_actions: array required")
    expected = {item["finding_id"] for item in planner_input["findings"]}
    seen: set[str] = set()
    allowed = set(contracts["allowed_finding_dispositions"])
    for index, item in enumerate(values):
        label = f"draft_plan.finding_actions[{index}]"
        if not isinstance(item, dict):
            fail(f"{label}: object required")
        require_exact_keys(item, {"finding_id", "disposition", "rationale"}, label)
        finding_id = require_string(item["finding_id"], f"{label}.finding_id")
        if finding_id in seen:
            fail(f"draft_plan.finding_actions duplicate finding_id {finding_id!r}")
        seen.add(finding_id)
        if finding_id not in expected:
            fail(f"draft_plan.finding_actions references unknown finding {finding_id!r}")
        if item["disposition"] not in allowed:
            fail(f"{label}.disposition is invalid")
        require_string(item["rationale"], f"{label}.rationale")
    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        fail(f"draft_plan must account for every finding: missing={missing}, extra={extra}")


def validate_draft_plan(
    draft_plan: dict[str, Any],
    planner_input: dict[str, Any],
    contracts: dict[str, Any] | None = None,
) -> None:
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_contracts(contracts)
    require_exact_keys(draft_plan, DRAFT_PLAN_FIELDS, "draft_plan")
    if draft_plan["plan_schema_version"] != 1:
        fail("draft_plan.plan_schema_version must be 1")
    require_id(draft_plan["plan_id"], "draft_plan.plan_id", "PLAN-")
    iteration = draft_plan["iteration"]
    if not isinstance(iteration, int) or isinstance(iteration, bool) or iteration < 1:
        fail("draft_plan.iteration must be a positive integer")
    base_sha = require_string(draft_plan["base_sha"], "draft_plan.base_sha")
    if not SHA40_RE.fullmatch(base_sha):
        fail("draft_plan.base_sha must be a lowercase 40-character commit SHA")
    if draft_plan["state"] != "DRAFT":
        fail("Planner may emit only DRAFT plans; sealing belongs to CONTROLLER")
    if draft_plan["planner_role"] != "PLANNER":
        fail("draft_plan.planner_role must be PLANNER")
    if draft_plan["creator_role"] != "CREATOR":
        fail("draft_plan.creator_role must be CREATOR")
    if draft_plan["source_planner_input_id"] != planner_input["input_id"]:
        fail("draft_plan.source_planner_input_id does not match planner input")
    require_string(draft_plan["goal"], "draft_plan.goal")

    proposed_write = safe_paths(draft_plan["proposed_write_files"], "draft_plan.proposed_write_files")
    safe_paths(draft_plan["proposed_read_files"], "draft_plan.proposed_read_files")
    forbidden = safe_paths(draft_plan["forbidden_files"], "draft_plan.forbidden_files")
    if not proposed_write:
        fail("draft_plan.proposed_write_files must not be empty")
    if set(proposed_write) & set(forbidden):
        fail("draft_plan proposed_write_files intersects forbidden_files")
    require_string_list(draft_plan["preserve_capabilities"], "draft_plan.preserve_capabilities")
    if not require_string_list(draft_plan["acceptance_criteria"], "draft_plan.acceptance_criteria"):
        fail("draft_plan.acceptance_criteria must not be empty")
    if not require_string_list(draft_plan["tests_required"], "draft_plan.tests_required"):
        fail("draft_plan.tests_required must not be empty")

    validate_finding_actions(draft_plan["finding_actions"], planner_input, contracts)
    side_requests = validate_side_requests(draft_plan["side_requests"])
    if side_requests != planner_input["side_requests"]:
        fail("draft_plan.side_requests must preserve all deferred side requests unchanged")

    # A Planner proposes work but has no authority to seal, execute or widen side requests.
    if "write_files" in draft_plan:
        fail("draft_plan may not expose executable write_files")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate SHADOW inspection requests/reports and build a finding bundle."
    )
    parser.add_argument("request", type=Path)
    parser.add_argument("reports", nargs="*", type=Path)
    parser.add_argument("--print-triggers", action="store_true")
    parser.add_argument("--build-bundle", action="store_true")
    parser.add_argument("--planner-input", action="store_true")
    args = parser.parse_args()
    try:
        contracts = load_json(DEFAULT_CONTRACTS)
        request = load_json(args.request)
        validate_request(request, contracts=contracts)
        if args.print_triggers:
            print(json.dumps(required_inspectors(request, contracts=contracts)))
        if args.build_bundle or args.planner_input:
            reports = [load_json(path) for path in args.reports]
            bundle = build_finding_bundle(request, reports, contracts=contracts)
            if args.build_bundle:
                print(json.dumps(bundle, ensure_ascii=False, sort_keys=True))
            if args.planner_input:
                print(
                    json.dumps(
                        build_planner_input(request, bundle, contracts=contracts),
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                )
        print("CONTROL PLANE SHADOW INSPECTION: GRÜN")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"CONTROL PLANE SHADOW INSPECTION: ROT · {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
