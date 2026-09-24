from __future__ import annotations

import argparse
from fnmatch import fnmatchcase
import json
from pathlib import Path
import re
from typing import Any

from scripts.validate_control_plane import (
    DEFAULT_REGISTRY,
    load_registry,
    require_exact_keys,
    require_string,
    require_string_list,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACTS = ROOT / ".provoware" / "control" / "contracts.json"
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")

PLAN_FIELDS = {
    "plan_schema_version",
    "plan_id",
    "iteration",
    "base_sha",
    "state",
    "goal",
    "creator_role",
    "write_files",
    "read_files",
    "forbidden_files",
    "preserve_capabilities",
    "acceptance_criteria",
    "tests_required",
    "side_requests",
}
LEASE_FIELDS = {
    "schema_version",
    "lease_id",
    "plan_id",
    "base_sha",
    "holder",
    "write_files",
    "state",
}
RESULT_FIELDS = {
    "result_schema_version",
    "plan_id",
    "lease_id",
    "base_sha",
    "creator_role",
    "state",
    "changed_files",
    "acceptance_results",
    "test_results",
    "preserved_capabilities",
    "unexpected_side_effects",
}
REPORT_FIELDS = {
    "schema_version",
    "report_id",
    "plan_id",
    "lease_id",
    "validator_role",
    "verdict",
    "findings",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path}: JSON root must be an object")
    return data


def validate_contracts(data: dict[str, Any]) -> None:
    require_exact_keys(data, {"schema_version", "mode", "artifacts"}, "contracts")
    if data["schema_version"] != 1:
        fail("contracts.schema_version must be 1")
    if data["mode"] != "SHADOW":
        fail("contracts.mode must remain SHADOW")

    artifacts = data["artifacts"]
    if not isinstance(artifacts, dict):
        fail("contracts.artifacts: object required")
    if set(artifacts) != {
        "SEALED_PLAN",
        "WRITE_LEASE",
        "EXECUTION_RESULT",
        "VALIDATION_REPORT",
    }:
        fail(
            "Step-2 contracts must contain SEALED_PLAN, WRITE_LEASE, "
            "EXECUTION_RESULT and VALIDATION_REPORT"
        )

    plan = artifacts["SEALED_PLAN"]
    require_exact_keys(
        plan,
        {"state", "planner_role", "executor_role", "required_fields"},
        "contracts.SEALED_PLAN",
    )
    if plan["state"] != "SEALED":
        fail("SEALED_PLAN.state must be SEALED")
    if plan["planner_role"] != "PLANNER":
        fail("SEALED_PLAN.planner_role must be PLANNER")
    if plan["executor_role"] != "CREATOR":
        fail("SEALED_PLAN.executor_role must be CREATOR")
    if set(require_string_list(plan["required_fields"], "SEALED_PLAN.required_fields")) != PLAN_FIELDS:
        fail("SEALED_PLAN.required_fields do not match the shadow plan contract")

    lease = artifacts["WRITE_LEASE"]
    require_exact_keys(
        lease,
        {"state", "grantor_role", "holder_role", "cardinality", "required_fields"},
        "contracts.WRITE_LEASE",
    )
    if lease["state"] != "ACTIVE":
        fail("WRITE_LEASE.state must be ACTIVE")
    if lease["grantor_role"] != "CONTROLLER":
        fail("WRITE_LEASE.grantor_role must be CONTROLLER")
    if lease["holder_role"] != "CREATOR":
        fail("WRITE_LEASE.holder_role must be CREATOR")
    if lease["cardinality"] != "GLOBAL_SINGLETON":
        fail("WRITE_LEASE.cardinality must be GLOBAL_SINGLETON")
    if set(require_string_list(lease["required_fields"], "WRITE_LEASE.required_fields")) != LEASE_FIELDS:
        fail("WRITE_LEASE.required_fields do not match the shadow lease contract")

    result = artifacts["EXECUTION_RESULT"]
    require_exact_keys(
        result,
        {"state", "producer_role", "required_fields"},
        "contracts.EXECUTION_RESULT",
    )
    if result["state"] != "EXECUTION_COMPLETE":
        fail("EXECUTION_RESULT.state must be EXECUTION_COMPLETE")
    if result["producer_role"] != "CREATOR":
        fail("EXECUTION_RESULT.producer_role must be CREATOR")
    if set(require_string_list(result["required_fields"], "EXECUTION_RESULT.required_fields")) != RESULT_FIELDS:
        fail("EXECUTION_RESULT.required_fields do not match the shadow result contract")

    report = artifacts["VALIDATION_REPORT"]
    require_exact_keys(
        report,
        {"producer_role", "write_product_code", "required_fields"},
        "contracts.VALIDATION_REPORT",
    )
    if report["producer_role"] != "VALIDATOR":
        fail("VALIDATION_REPORT.producer_role must be VALIDATOR")
    if report["write_product_code"] is not False:
        fail("VALIDATION_REPORT may not write product code")
    if set(require_string_list(report["required_fields"], "VALIDATION_REPORT.required_fields")) != REPORT_FIELDS:
        fail("VALIDATION_REPORT.required_fields do not match the shadow report contract")


def safe_relative_paths(values: Any, label: str) -> list[str]:
    result = require_string_list(values, label)
    for raw in result:
        path = Path(raw)
        if path.is_absolute() or ".." in path.parts:
            fail(f"{label}: unsafe repository path {raw!r}")
    return result


def matching_rule(registry: dict[str, Any], file_path: str) -> dict[str, Any] | None:
    for rule in registry["paths"]:
        if fnmatchcase(file_path, rule["pattern"]):
            return rule
    return None


def validate_side_requests(values: Any) -> None:
    if not isinstance(values, list):
        fail("plan.side_requests: array required")
    seen: set[str] = set()
    for index, item in enumerate(values):
        if not isinstance(item, dict):
            fail(f"plan.side_requests[{index}]: object required")
        require_exact_keys(item, {"request_id", "disposition"}, f"plan.side_requests[{index}]")
        request_id = require_string(item["request_id"], f"plan.side_requests[{index}].request_id")
        if request_id in seen:
            fail(f"plan.side_requests: duplicate request_id {request_id!r}")
        seen.add(request_id)
        if item["disposition"] != "DEFER":
            fail("side requests must be DEFER in the sealed execution plan")


def validate_sealed_plan(
    plan: dict[str, Any],
    registry: dict[str, Any] | None = None,
    contracts: dict[str, Any] | None = None,
) -> None:
    registry = load_registry() if registry is None else registry
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_registry(registry)
    validate_contracts(contracts)

    require_exact_keys(plan, PLAN_FIELDS, "plan")
    if plan["plan_schema_version"] != 1:
        fail("plan.plan_schema_version must be 1")
    plan_id = require_string(plan["plan_id"], "plan.plan_id")
    if not plan_id.startswith("PLAN-"):
        fail("plan.plan_id must start with PLAN-")
    iteration = plan["iteration"]
    if not isinstance(iteration, int) or isinstance(iteration, bool) or iteration < 1:
        fail("plan.iteration must be a positive integer")
    base_sha = require_string(plan["base_sha"], "plan.base_sha")
    if not SHA40_RE.fullmatch(base_sha):
        fail("plan.base_sha must be a lowercase 40-character commit SHA")
    if plan["state"] != "SEALED":
        fail("plan.state must be SEALED before execution")
    require_string(plan["goal"], "plan.goal")
    if plan["creator_role"] != "CREATOR":
        fail("plan.creator_role must be CREATOR")

    write_files = safe_relative_paths(plan["write_files"], "plan.write_files")
    read_files = safe_relative_paths(plan["read_files"], "plan.read_files")
    forbidden_files = safe_relative_paths(plan["forbidden_files"], "plan.forbidden_files")
    preserve = set(
        require_string_list(plan["preserve_capabilities"], "plan.preserve_capabilities")
    )
    criteria = require_string_list(plan["acceptance_criteria"], "plan.acceptance_criteria")
    tests = require_string_list(plan["tests_required"], "plan.tests_required")
    if not write_files:
        fail("plan.write_files must not be empty")
    if not criteria:
        fail("plan.acceptance_criteria must not be empty")
    if not tests:
        fail("plan.tests_required must not be empty")
    if set(write_files) & set(forbidden_files):
        fail("plan.write_files intersects plan.forbidden_files")
    validate_side_requests(plan["side_requests"])

    known_capabilities = set(registry["capabilities"])
    unknown_preserve = sorted(preserve - known_capabilities)
    if unknown_preserve:
        fail("plan.preserve_capabilities contains unknown capability: " + ", ".join(unknown_preserve))

    for file_path in write_files:
        rule = matching_rule(registry, file_path)
        if rule is None:
            fail(f"plan write path has no control-plane rule: {file_path}")
        if rule["state"] in {"FROZEN", "ARCHIVE"} or rule["automatic_write"] is not True:
            fail(f"plan write blocked by path policy: {file_path}")
        required_preserve = set(rule.get("preserve_capabilities", []))
        missing = sorted(required_preserve - preserve)
        if missing:
            fail(
                f"plan write path {file_path} must preserve capabilities: "
                + ", ".join(missing)
            )

    # Read paths may be broader than the control registry, but explicit forbidden
    # files may never be placed in the write set. This keeps inspection cheap
    # without silently widening Creator authority.
    _ = read_files


def validate_write_lease(lease: dict[str, Any], plan: dict[str, Any]) -> None:
    require_exact_keys(lease, LEASE_FIELDS, "lease")
    if lease["schema_version"] != 1:
        fail("lease.schema_version must be 1")
    if lease["lease_id"] != f"LEASE-{plan['plan_id']}":
        fail("lease.lease_id must be deterministic from plan_id")
    if lease["plan_id"] != plan["plan_id"]:
        fail("lease.plan_id does not match plan")
    if lease["base_sha"] != plan["base_sha"]:
        fail("lease.base_sha does not match plan")
    if lease["holder"] != "CREATOR":
        fail("lease.holder must be CREATOR")
    if lease["write_files"] != plan["write_files"]:
        fail("lease.write_files must exactly match sealed plan write_files")
    if lease["state"] != "ACTIVE":
        fail("lease.state must be ACTIVE")


def authorize_write_lease(
    plan: dict[str, Any],
    active_lease: dict[str, Any] | None = None,
    registry: dict[str, Any] | None = None,
    contracts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_sealed_plan(plan, registry=registry, contracts=contracts)
    if active_lease is not None and active_lease.get("state") == "ACTIVE":
        fail(
            "global write lease already active: "
            + require_string(active_lease.get("lease_id"), "active_lease.lease_id")
        )
    lease = {
        "schema_version": 1,
        "lease_id": f"LEASE-{plan['plan_id']}",
        "plan_id": plan["plan_id"],
        "base_sha": plan["base_sha"],
        "holder": "CREATOR",
        "write_files": list(plan["write_files"]),
        "state": "ACTIVE",
    }
    validate_write_lease(lease, plan)
    return lease



def named_status_map(
    values: Any,
    label: str,
    name_key: str,
) -> dict[str, str]:
    if not isinstance(values, list):
        fail(f"{label}: array required")
    result: dict[str, str] = {}
    for index, item in enumerate(values):
        if not isinstance(item, dict):
            fail(f"{label}[{index}]: object required")
        require_exact_keys(item, {name_key, "status"}, f"{label}[{index}]")
        name = require_string(item[name_key], f"{label}[{index}].{name_key}")
        if name in result:
            fail(f"{label}: duplicate {name_key} {name!r}")
        status = item["status"]
        if status not in {"PASS", "FAIL"}:
            fail(f"{label}[{index}].status must be PASS or FAIL")
        result[name] = status
    return result


def validate_validation_report(report: dict[str, Any], plan: dict[str, Any], lease: dict[str, Any]) -> None:
    require_exact_keys(report, REPORT_FIELDS, "validation_report")
    if report["schema_version"] != 1:
        fail("validation_report.schema_version must be 1")
    if report["report_id"] != f"VALIDATION-{plan['plan_id']}":
        fail("validation_report.report_id must be deterministic from plan_id")
    if report["plan_id"] != plan["plan_id"]:
        fail("validation_report.plan_id does not match plan")
    if report["lease_id"] != lease["lease_id"]:
        fail("validation_report.lease_id does not match lease")
    if report["validator_role"] != "VALIDATOR":
        fail("validation_report.validator_role must be VALIDATOR")
    if report["verdict"] not in {"PASS", "FAIL"}:
        fail("validation_report.verdict must be PASS or FAIL")
    findings = require_string_list(report["findings"], "validation_report.findings")
    if report["verdict"] == "PASS" and findings:
        fail("PASS validation report may not contain findings")
    if report["verdict"] == "FAIL" and not findings:
        fail("FAIL validation report must contain at least one finding")


def validate_execution_result(
    plan: dict[str, Any],
    lease: dict[str, Any],
    result: dict[str, Any],
    registry: dict[str, Any] | None = None,
    contracts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = load_registry() if registry is None else registry
    contracts = load_json(DEFAULT_CONTRACTS) if contracts is None else contracts
    validate_sealed_plan(plan, registry=registry, contracts=contracts)
    validate_write_lease(lease, plan)
    validate_contracts(contracts)
    require_exact_keys(result, RESULT_FIELDS, "execution_result")

    findings: list[str] = []

    if result["result_schema_version"] != 1:
        fail("execution_result.result_schema_version must be 1")
    if result["plan_id"] != plan["plan_id"]:
        fail("execution_result.plan_id does not match sealed plan")
    if result["lease_id"] != lease["lease_id"]:
        fail("execution_result.lease_id does not match active lease")
    if result["base_sha"] != plan["base_sha"]:
        fail("execution_result.base_sha does not match sealed plan")
    if result["creator_role"] != "CREATOR":
        fail("execution_result.creator_role must be CREATOR")
    if result["state"] != "EXECUTION_COMPLETE":
        fail("execution_result.state must be EXECUTION_COMPLETE")

    changed_files = safe_relative_paths(result["changed_files"], "execution_result.changed_files")
    if not changed_files:
        findings.append("NO_CHANGED_FILES")
    unexpected_files = sorted(set(changed_files) - set(plan["write_files"]))
    if unexpected_files:
        findings.append("UNPLANNED_FILES:" + ",".join(unexpected_files))
    forbidden_changed = sorted(set(changed_files) & set(plan["forbidden_files"]))
    if forbidden_changed:
        findings.append("FORBIDDEN_FILES_CHANGED:" + ",".join(forbidden_changed))

    acceptance = named_status_map(
        result["acceptance_results"],
        "execution_result.acceptance_results",
        "criterion",
    )
    expected_acceptance = set(plan["acceptance_criteria"])
    if set(acceptance) != expected_acceptance:
        missing = sorted(expected_acceptance - set(acceptance))
        extra = sorted(set(acceptance) - expected_acceptance)
        findings.append(f"ACCEPTANCE_SET_MISMATCH:missing={missing},extra={extra}")
    failed_acceptance = sorted(name for name, status in acceptance.items() if status != "PASS")
    if failed_acceptance:
        findings.append("ACCEPTANCE_FAILED:" + ",".join(failed_acceptance))

    tests = named_status_map(
        result["test_results"],
        "execution_result.test_results",
        "test",
    )
    expected_tests = set(plan["tests_required"])
    if set(tests) != expected_tests:
        missing = sorted(expected_tests - set(tests))
        extra = sorted(set(tests) - expected_tests)
        findings.append(f"TEST_SET_MISMATCH:missing={missing},extra={extra}")
    failed_tests = sorted(name for name, status in tests.items() if status != "PASS")
    if failed_tests:
        findings.append("TEST_FAILED:" + ",".join(failed_tests))

    preserved = named_status_map(
        result["preserved_capabilities"],
        "execution_result.preserved_capabilities",
        "capability",
    )
    expected_preserve = set(plan["preserve_capabilities"])
    if set(preserved) != expected_preserve:
        missing = sorted(expected_preserve - set(preserved))
        extra = sorted(set(preserved) - expected_preserve)
        findings.append(f"PRESERVE_SET_MISMATCH:missing={missing},extra={extra}")
    failed_preserve = sorted(name for name, status in preserved.items() if status != "PASS")
    if failed_preserve:
        findings.append("CAPABILITY_REGRESSION:" + ",".join(failed_preserve))

    side_effects = require_string_list(
        result["unexpected_side_effects"],
        "execution_result.unexpected_side_effects",
    )
    if side_effects:
        findings.append("UNEXPECTED_SIDE_EFFECTS:" + ",".join(side_effects))

    report = {
        "schema_version": 1,
        "report_id": f"VALIDATION-{plan['plan_id']}",
        "plan_id": plan["plan_id"],
        "lease_id": lease["lease_id"],
        "validator_role": "VALIDATOR",
        "verdict": "PASS" if not findings else "FAIL",
        "findings": findings,
    }
    validate_validation_report(report, plan, lease)
    return report

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a sealed plan and optionally authorize a SHADOW write lease."
    )
    parser.add_argument("plan", type=Path)
    parser.add_argument("--active-lease", type=Path)
    parser.add_argument("--authorize-lease", action="store_true")
    args = parser.parse_args()

    try:
        registry = load_registry(DEFAULT_REGISTRY)
        contracts = load_json(DEFAULT_CONTRACTS)
        plan = load_json(args.plan)
        active_lease = load_json(args.active_lease) if args.active_lease else None
        validate_sealed_plan(plan, registry=registry, contracts=contracts)
        if args.authorize_lease:
            lease = authorize_write_lease(
                plan,
                active_lease=active_lease,
                registry=registry,
                contracts=contracts,
            )
            print(json.dumps(lease, ensure_ascii=False, sort_keys=True))
        print("CONTROL PLANE SHADOW PLAN/LEASE: GRÜN")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"CONTROL PLANE SHADOW PLAN/LEASE: ROT · {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
