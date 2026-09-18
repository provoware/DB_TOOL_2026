from __future__ import annotations

from enum import StrEnum


class DatabaseKind(StrEnum):
    MAIN = "main"
    STATE = "state"
    TESTLAB = "testlab"


SCHEMA_VERSION = 1
APPLICATION_IDS = {
    DatabaseKind.MAIN: 0x50564D31,   # PVM1
    DatabaseKind.STATE: 0x50565331,  # PVS1
    DatabaseKind.TESTLAB: 0x50565431, # PVT1
}

EXPECTED_TABLES = {
    DatabaseKind.MAIN: {
        "schema_migrations", "categories", "entries", "field_definitions",
        "field_options", "scalar_field_values", "single_choice_values",
        "multi_choice_values", "audit_events",
    },
    DatabaseKind.STATE: {
        "runtime_meta", "app_sessions", "edit_sessions", "drafts",
        "operation_journal", "backup_catalog", "health_runs",
        "health_results", "error_events",
    },
    DatabaseKind.TESTLAB: {
        "test_runs", "test_results", "fault_injections",
        "fixture_catalog", "test_artifacts",
    },
}
