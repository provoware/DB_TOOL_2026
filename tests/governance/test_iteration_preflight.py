from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "iteration_preflight.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("iteration_preflight", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _manifest(kind: str, profile: str, *, write_files: list[str] | None = None):
    return {
        "change_kind": kind,
        "gate_profile": profile,
        "write_files": write_files or [],
        "pip_requirements": [],
        "ci": {"compile": [], "python_tests": []},
    }


def test_gate_route_contract_is_single_source() -> None:
    module = _load_module()

    assert module.resolve_gate_route(_manifest("scope_only", "scope")) == (False, False, False)
    assert module.resolve_gate_route(_manifest("governance", "governance")) == (False, True, False)
    assert module.resolve_gate_route(_manifest("product", "product")) == (True, False, True)
    assert module.resolve_gate_route(_manifest("ui", "ui")) == (True, False, True)


def test_preflight_blocks_profile_downgrade_and_frozen_core() -> None:
    module = _load_module()

    try:
        module.resolve_gate_route(_manifest("product", "scope"))
    except ValueError as exc:
        assert "downgrade blocked" in str(exc)
    else:
        raise AssertionError("product/scope must fail closed")

    try:
        module.resolve_gate_route(
            _manifest(
                "product",
                "product",
                write_files=["src/provoware_db/storage/sqlite/schema_guard.py"],
            )
        )
    except ValueError as exc:
        assert "Frozen-core path requires gate_profile=deep" in str(exc)
    else:
        raise AssertionError("frozen-core write without deep gate must fail closed")


def test_current_repository_preflight_is_green() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--json"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["iteration"] >= 152
    assert payload["profile"] == "governance"
    assert payload["run_governance"] is True
