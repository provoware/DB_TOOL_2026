from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.validate_control_plane import load_registry, validate_registry


def expect_invalid(data: dict, marker: str) -> None:
    try:
        validate_registry(data)
    except ValueError as exc:
        if marker not in str(exc):
            raise AssertionError(f"expected {marker!r} in {str(exc)!r}") from exc
    else:
        raise AssertionError(f"expected registry validation failure containing {marker!r}")


def protected_rule(data: dict, pattern: str) -> dict:
    return next(rule for rule in data["paths"] if rule["pattern"] == pattern)


def test_current_registry_is_green() -> None:
    validate_registry(load_registry())


def test_single_product_writer_is_fail_closed() -> None:
    data = deepcopy(load_registry())
    data["workflow"]["single_product_writer"] = False
    expect_invalid(data, "single_product_writer must be true")


def test_planner_and_validator_remain_read_only() -> None:
    for flag in ("planner_read_only", "validator_read_only", "inspectors_read_only"):
        data = deepcopy(load_registry())
        data["workflow"][flag] = False
        expect_invalid(data, f"{flag} must be true")


def test_frozen_paths_cannot_enable_automatic_writes() -> None:
    data = deepcopy(load_registry())
    protected_rule(data, "src/provoware_db/domain/**")["automatic_write"] = True
    expect_invalid(data, "FROZEN path may not allow automatic writes")


def test_legacy_protected_path_cannot_disappear_or_downgrade() -> None:
    data = deepcopy(load_registry())
    data["paths"] = [
        rule for rule in data["paths"] if rule["pattern"] != "src/provoware_db/domain/**"
    ]
    expect_invalid(data, "legacy protected paths missing")

    data = deepcopy(load_registry())
    protected_rule(data, "src/provoware_db/storage/**")["required_gate"] = "ui"
    expect_invalid(data, "must require deep gate")


def test_mask_properties_evidence_must_exist_and_be_green() -> None:
    data = deepcopy(load_registry())
    data["capabilities"]["MASK_PROPERTIES_V1"]["evidence"][0] = (
        "docs/development/screenshots/iteration-0119/does-not-exist.json"
    )
    expect_invalid(data, "evidence file missing")


def test_latest_product_iteration_cannot_be_stale() -> None:
    data = deepcopy(load_registry())
    data["project"]["latest_product_iteration"] = 118
    expect_invalid(data, "latest_product_iteration is stale")


def test_persistence_cannot_open_in_shadow_foundation() -> None:
    data = deepcopy(load_registry())
    data["project"]["persistence"] = "OPEN"
    expect_invalid(data, "persistence must remain CLOSED")


def test_shadow_foundation_cannot_become_authoritative_incidentally() -> None:
    data = deepcopy(load_registry())
    data["mode"] = "ENFORCED"
    data["authoritative"] = True
    expect_invalid(data, "must remain SHADOW and non-authoritative")


def main() -> None:
    test_current_registry_is_green()
    test_single_product_writer_is_fail_closed()
    test_planner_and_validator_remain_read_only()
    test_frozen_paths_cannot_enable_automatic_writes()
    test_legacy_protected_path_cannot_disappear_or_downgrade()
    test_mask_properties_evidence_must_exist_and_be_green()
    test_latest_product_iteration_cannot_be_stale()
    test_persistence_cannot_open_in_shadow_foundation()
    test_shadow_foundation_cannot_become_authoritative_incidentally()
    print("CONTROL PLANE V2 REGISTRY I120 STEP 1: GRÜN")


if __name__ == "__main__":
    main()
