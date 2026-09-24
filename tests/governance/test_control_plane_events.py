from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.control_plane_events import append_event, validate_event_log


REQUEST_ID = "REQ-I123-EVENTS"


def expect_invalid(fn, marker: str) -> None:
    try:
        fn()
    except ValueError as exc:
        assert marker in str(exc), (marker, str(exc))
    else:
        raise AssertionError(f"expected failure containing {marker!r}")


def build_execution_prefix() -> list[dict]:
    events: list[dict] = []
    events = append_event(
        events, REQUEST_ID, "REQUEST_CREATED", "INSPECTOR", "request:REQ-I123-EVENTS"
    )
    events = append_event(
        events, REQUEST_ID, "FINDING_RECORDED", "INSPECTOR", "finding:F-I123-001"
    )
    events = append_event(
        events, REQUEST_ID, "AUDIT_COMPLETE", "INSPECTOR", "bundle:BUNDLE-I123"
    )
    events = append_event(
        events, REQUEST_ID, "FINDINGS_READY", "PLANNER", "planner:INPUT-I123"
    )
    events = append_event(
        events, REQUEST_ID, "PLAN_SUBMITTED", "PLANNER", "draft:PLAN-I123"
    )
    events = append_event(
        events, REQUEST_ID, "PLAN_SEALED", "CONTROLLER", "seal:SEAL-PLAN-I123"
    )
    events = append_event(
        events, REQUEST_ID, "WRITE_LEASE_GRANTED", "CONTROLLER", "lease:LEASE-I123"
    )
    return events


def test_happy_path_is_hash_chained_and_reaches_execution() -> None:
    events = build_execution_prefix()
    state, stopped = validate_event_log(events, REQUEST_ID)
    assert state == "EXECUTING"
    assert stopped is False
    assert [event["sequence"] for event in events] == list(range(1, 8))
    assert events[0]["previous_event_sha256"] == "GENESIS"
    for previous, current in zip(events, events[1:]):
        assert current["previous_event_sha256"] == previous["event_sha256"]


def test_append_returns_new_log_without_mutating_existing_events() -> None:
    events: list[dict] = []
    next_events = append_event(
        events, REQUEST_ID, "REQUEST_CREATED", "INSPECTOR", "request:REQ-I123-EVENTS"
    )
    assert events == []
    assert len(next_events) == 1


def test_mutation_or_reordering_breaks_append_only_validation() -> None:
    events = build_execution_prefix()

    mutated = deepcopy(events)
    mutated[3]["payload_ref"] = "planner:TAMPERED"
    expect_invalid(
        lambda: validate_event_log(mutated, REQUEST_ID),
        "event_sha256 mismatch",
    )

    reordered = deepcopy(events)
    reordered[1], reordered[2] = reordered[2], reordered[1]
    expect_invalid(
        lambda: validate_event_log(reordered, REQUEST_ID),
        "sequence must be 2",
    )


def test_invalid_lifecycle_jump_fails_closed() -> None:
    events: list[dict] = []
    events = append_event(
        events, REQUEST_ID, "REQUEST_CREATED", "INSPECTOR", "request:REQ-I123-EVENTS"
    )
    expect_invalid(
        lambda: append_event(
            events,
            REQUEST_ID,
            "WRITE_LEASE_GRANTED",
            "CONTROLLER",
            "lease:too-early",
        ),
        "invalid state transition",
    )


def test_unknown_event_and_wrong_actor_fail_closed() -> None:
    expect_invalid(
        lambda: append_event(
            [],
            REQUEST_ID,
            "UNKNOWN_TRIGGER",
            "INSPECTOR",
            "unknown:x",
        ),
        "unknown control-plane event type",
    )
    expect_invalid(
        lambda: append_event(
            [],
            REQUEST_ID,
            "REQUEST_CREATED",
            "PLANNER",
            "request:x",
        ),
        "actor_role must be INSPECTOR",
    )


def test_side_request_is_deferred_without_state_change() -> None:
    events: list[dict] = []
    events = append_event(
        events, REQUEST_ID, "REQUEST_CREATED", "INSPECTOR", "request:REQ-I123-EVENTS"
    )
    before_state, _ = validate_event_log(events, REQUEST_ID)
    events = append_event(
        events,
        REQUEST_ID,
        "SIDE_REQUEST_CREATED",
        "PLANNER",
        "request:REQ-LATER-I123",
    )
    after_state, stopped = validate_event_log(events, REQUEST_ID)
    assert before_state == after_state == "INSPECTING"
    assert stopped is False
    assert events[-1]["effect"] == "DEFER"


def test_frozen_violation_hard_stops_future_events() -> None:
    events: list[dict] = []
    events = append_event(
        events, REQUEST_ID, "REQUEST_CREATED", "INSPECTOR", "request:REQ-I123-EVENTS"
    )
    events = append_event(
        events,
        REQUEST_ID,
        "FROZEN_VIOLATION",
        "CONTROLLER",
        "frozen:CP-06",
    )
    state, stopped = validate_event_log(events, REQUEST_ID)
    assert state == "INSPECTING"
    assert stopped is True
    assert events[-1]["effect"] == "HARD_STOP"

    expect_invalid(
        lambda: append_event(
            events,
            REQUEST_ID,
            "AUDIT_COMPLETE",
            "INSPECTOR",
            "bundle:should-not-run",
        ),
        "cannot append event after HARD_STOP",
    )


def main() -> None:
    test_happy_path_is_hash_chained_and_reaches_execution()
    test_append_returns_new_log_without_mutating_existing_events()
    test_mutation_or_reordering_breaks_append_only_validation()
    test_invalid_lifecycle_jump_fails_closed()
    test_unknown_event_and_wrong_actor_fail_closed()
    test_side_request_is_deferred_without_state_change()
    test_frozen_violation_hard_stops_future_events()
    print("CONTROL PLANE V2 SHADOW EVENTS I123 STEP 2: GRÜN")


if __name__ == "__main__":
    main()
