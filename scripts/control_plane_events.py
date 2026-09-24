from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
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
DEFAULT_EVENT_CONTRACTS = ROOT / ".provoware" / "control" / "event_contracts.json"

EVENT_FIELDS = {
    "schema_version",
    "event_id",
    "request_id",
    "sequence",
    "event_type",
    "actor_role",
    "from_state",
    "to_state",
    "effect",
    "payload_ref",
    "previous_event_sha256",
    "event_sha256",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail(f"{path}: JSON root must be an object")
    return data


def validate_event_contracts(data: dict[str, Any]) -> None:
    require_exact_keys(
        data,
        {
            "schema_version",
            "mode",
            "genesis_hash",
            "allowed_effects",
            "event_fields",
            "informational_events",
        },
        "event_contracts",
    )
    if data["schema_version"] != 1:
        fail("event_contracts.schema_version must be 1")
    if data["mode"] != "SHADOW":
        fail("event_contracts.mode must remain SHADOW")
    if data["genesis_hash"] != "GENESIS":
        fail("event_contracts.genesis_hash must be GENESIS")
    effects = require_string_list(
        data["allowed_effects"],
        "event_contracts.allowed_effects",
    )
    if effects != ["TRANSITION", "AUDIT", "DEFER", "HARD_STOP"]:
        fail("event_contracts.allowed_effects must use fixed shadow ordering")
    if set(require_string_list(data["event_fields"], "event_contracts.event_fields")) != EVENT_FIELDS:
        fail("event_contracts.event_fields do not match append-only event contract")

    informational = data["informational_events"]
    if not isinstance(informational, dict):
        fail("event_contracts.informational_events must be an object")
    if set(informational) != {"FINDING_RECORDED", "PLAN_SUBMITTED"}:
        fail("informational_events must be FINDING_RECORDED and PLAN_SUBMITTED")
    expected = {
        "FINDING_RECORDED": ("INSPECTOR", "INSPECTING"),
        "PLAN_SUBMITTED": ("PLANNER", "PLANNING"),
    }
    for event_type, (role, state) in expected.items():
        item = informational[event_type]
        if not isinstance(item, dict):
            fail(f"informational_events.{event_type} must be an object")
        require_exact_keys(
            item,
            {"actor_role", "allowed_state", "effect"},
            f"informational_events.{event_type}",
        )
        if item["actor_role"] != role:
            fail(f"informational_events.{event_type}.actor_role mismatch")
        if item["allowed_state"] != state:
            fail(f"informational_events.{event_type}.allowed_state mismatch")
        if item["effect"] != "AUDIT":
            fail(f"informational_events.{event_type}.effect must be AUDIT")


def canonical_event_hash(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "event_sha256"}
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def event_semantics(
    event_type: str,
    actor_role: str,
    current_state: str,
    registry: dict[str, Any],
    contracts: dict[str, Any],
) -> tuple[str, str, bool]:
    triggers = registry["triggers"]
    if event_type in triggers:
        trigger = triggers[event_type]
        if trigger["required_role"] != actor_role:
            fail(f"{event_type}: actor_role must be {trigger['required_role']}")
        if "from_state" in trigger:
            if trigger["from_state"] != current_state:
                fail(
                    f"{event_type}: invalid state transition from {current_state}; "
                    f"expected {trigger['from_state']}"
                )
            return trigger["to_state"], "TRANSITION", False

        action = trigger["action"]
        if action not in {"DEFER", "HARD_STOP"}:
            fail(f"{event_type}: unsupported special action {action}")
        return current_state, action, action == "HARD_STOP"

    informational = contracts["informational_events"]
    if event_type in informational:
        info = informational[event_type]
        if info["actor_role"] != actor_role:
            fail(f"{event_type}: actor_role must be {info['actor_role']}")
        if info["allowed_state"] != current_state:
            fail(
                f"{event_type}: informational event not allowed in state {current_state}"
            )
        return current_state, info["effect"], False

    fail(f"unknown control-plane event type: {event_type}")


def validate_event_log(
    events: list[dict[str, Any]],
    request_id: str,
    *,
    registry: dict[str, Any] | None = None,
    contracts: dict[str, Any] | None = None,
) -> tuple[str, bool]:
    registry = load_registry(DEFAULT_REGISTRY) if registry is None else registry
    contracts = load_json(DEFAULT_EVENT_CONTRACTS) if contracts is None else contracts
    validate_registry(registry)
    validate_event_contracts(contracts)
    require_string(request_id, "request_id")
    if not isinstance(events, list):
        fail("event log must be an array")

    current_state = registry["lifecycle"]["initial_state"]
    previous_hash = contracts["genesis_hash"]
    hard_stopped = False

    for index, event in enumerate(events, start=1):
        if hard_stopped:
            fail("event log contains events after HARD_STOP")
        if not isinstance(event, dict):
            fail(f"events[{index - 1}] must be an object")
        require_exact_keys(event, EVENT_FIELDS, f"events[{index - 1}]")
        if event["schema_version"] != 1:
            fail(f"events[{index - 1}].schema_version must be 1")
        if event["request_id"] != request_id:
            fail(f"events[{index - 1}].request_id mismatch")
        if event["sequence"] != index:
            fail(f"events[{index - 1}].sequence must be {index}")
        event_type = require_string(event["event_type"], f"events[{index - 1}].event_type")
        actor_role = require_string(event["actor_role"], f"events[{index - 1}].actor_role")
        if actor_role not in registry["roles"]:
            fail(f"events[{index - 1}].actor_role is unknown")
        expected_id = f"EVT-{request_id}-{index:04d}-{event_type}"
        if event["event_id"] != expected_id:
            fail(f"events[{index - 1}].event_id mismatch")
        if event["previous_event_sha256"] != previous_hash:
            fail(f"events[{index - 1}].previous_event_sha256 breaks hash chain")
        if event["from_state"] != current_state:
            fail(f"events[{index - 1}].from_state does not match current state")
        require_string(event["payload_ref"], f"events[{index - 1}].payload_ref")

        next_state, effect, stop = event_semantics(
            event_type,
            actor_role,
            current_state,
            registry,
            contracts,
        )
        if event["to_state"] != next_state:
            fail(f"events[{index - 1}].to_state mismatch")
        if event["effect"] != effect:
            fail(f"events[{index - 1}].effect mismatch")

        expected_hash = canonical_event_hash(event)
        if event["event_sha256"] != expected_hash:
            fail(f"events[{index - 1}].event_sha256 mismatch")

        current_state = next_state
        previous_hash = event["event_sha256"]
        hard_stopped = stop

    return current_state, hard_stopped


def append_event(
    events: list[dict[str, Any]],
    request_id: str,
    event_type: str,
    actor_role: str,
    payload_ref: str,
    *,
    registry: dict[str, Any] | None = None,
    contracts: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    registry = load_registry(DEFAULT_REGISTRY) if registry is None else registry
    contracts = load_json(DEFAULT_EVENT_CONTRACTS) if contracts is None else contracts
    current_state, hard_stopped = validate_event_log(
        events,
        request_id,
        registry=registry,
        contracts=contracts,
    )
    if hard_stopped:
        fail("cannot append event after HARD_STOP")
    require_string(payload_ref, "payload_ref")

    next_state, effect, stop = event_semantics(
        event_type,
        actor_role,
        current_state,
        registry,
        contracts,
    )
    sequence = len(events) + 1
    previous_hash = (
        contracts["genesis_hash"]
        if not events
        else events[-1]["event_sha256"]
    )
    event = {
        "schema_version": 1,
        "event_id": f"EVT-{request_id}-{sequence:04d}-{event_type}",
        "request_id": request_id,
        "sequence": sequence,
        "event_type": event_type,
        "actor_role": actor_role,
        "from_state": current_state,
        "to_state": next_state,
        "effect": effect,
        "payload_ref": payload_ref,
        "previous_event_sha256": previous_hash,
        "event_sha256": "",
    }
    event["event_sha256"] = canonical_event_hash(event)

    result = [*deepcopy(events), event]
    final_state, final_hard_stop = validate_event_log(
        result,
        request_id,
        registry=registry,
        contracts=contracts,
    )
    if final_state != next_state or final_hard_stop != stop:
        fail("appended event did not produce expected shadow state")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Control Plane V2 SHADOW append-only event log."
    )
    parser.add_argument("event_log", type=Path)
    parser.add_argument("--request-id", required=True)
    args = parser.parse_args()
    try:
        raw = json.loads(args.event_log.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            fail("event log JSON root must be an array")
        state, stopped = validate_event_log(raw, args.request_id)
        print(
            json.dumps(
                {"state": state, "hard_stopped": stopped},
                sort_keys=True,
            )
        )
        print("CONTROL PLANE SHADOW EVENTS: GRÜN")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"CONTROL PLANE SHADOW EVENTS: ROT · {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
