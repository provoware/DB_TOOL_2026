from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "AGENT_GOVERNANCE_AUSWERTUNG.txt"

REQUIRED_FILES = (
    "AGENTS.md",
    ".provoware/agents/rules.yaml",
    "scripts/check_agent_collisions.py",
    "scripts/check_iteration_scope.py",
    ".provoware/templates/iteration-plan.json",
)

REQUIRED_AGENT_RULE_MARKERS = (
    "Codesparsamkeit",
    "Trafficsparsamkeit",
    "Keine unnötigen Tests",
    "Dateibesitz und Kollisionsschutz",
    "Screenshot-Regel",
    "exakt die nächsten drei Schritte",
    "Laienhilfe-Subagent",
    "Zwei-Schritt-Iteration",
    "interner Zwischen-Gate",
    "atomarer Remote-Head",
    "NO_FIX_REQUIRED",
)

REQUIRED_MACHINE_RULES = (
    "smallest_meaningful_patch: true",
    "code_sparing: true",
    "traffic_sparing: true",
    "one_writer_per_file: true",
    "no_full_test_without_reason: true",
    "no_repeat_test_without_new_change_or_finding: true",
    "screenshot_every_n_iterations: 5",
    "exactly_three_next_steps_required: true",
    "layman_guide_delta_every_iteration: true",
    "layman_guide_agent_never_modify_product_code: true",
    "layman_guide_updates_must_be_incremental: true",
    "two_step_iteration_required: true",
    "step_two_requires_step_one_green: true",
    "single_branch_pr_for_two_steps: true",
    "freeze_after_both_steps_only: true",
    "second_step_must_share_scope: true",
    "atomic_remote_head_per_step: true",
    "repair_head_requires_failed_gate: true",
    "no_status_only_commit_for_no_fix_step_two: true",
    "manifest_ci_targets_must_exist: true",
)


def run(cmd: list[str], expected: int = 0) -> tuple[bool, str]:
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    output = (result.stdout + result.stderr).strip()
    return result.returncode == expected, output


def main() -> int:
    lines: list[str] = ["PROVOWARE AGENT GOVERNANCE GATE", ""]
    failures = 0

    for rel in REQUIRED_FILES:
        path = ROOT / rel
        ok = path.is_file()
        lines.append(f"{'GRÜN' if ok else 'ROT'}: Datei {rel}")
        failures += 0 if ok else 1

    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for marker in REQUIRED_AGENT_RULE_MARKERS:
        ok = marker in agents
        lines.append(f"{'GRÜN' if ok else 'ROT'}: AGENTS.md Regel '{marker}'")
        failures += 0 if ok else 1

    machine = (ROOT / ".provoware/agents/rules.yaml").read_text(encoding="utf-8")
    for marker in REQUIRED_MACHINE_RULES:
        ok = marker in machine
        lines.append(f"{'GRÜN' if ok else 'ROT'}: rules.yaml '{marker}'")
        failures += 0 if ok else 1

    compile_ok, compile_out = run([
        sys.executable,
        "-m",
        "py_compile",
        "scripts/check_agent_collisions.py",
        "scripts/check_iteration_scope.py",
        "scripts/validate_agent_governance.py",
        "scripts/validate_iteration_manifest.py",
    ])
    lines.append(f"{'GRÜN' if compile_ok else 'ROT'}: Python-Compile Governance-Skripte")
    if not compile_ok:
        failures += 1
        lines.append(compile_out)

    collision_ok, collision_out = run([
        sys.executable,
        "scripts/check_agent_collisions.py",
        ".provoware/examples/plan-agent-web.json",
        ".provoware/examples/plan-agent-core.json",
    ])
    lines.append(f"{'GRÜN' if collision_ok else 'ROT'}: Beispielpläne kollisionsfrei")
    if not collision_ok:
        failures += 1
        lines.append(collision_out)

    with tempfile.TemporaryDirectory() as tmp:
        temp = Path(tmp)
        a = temp / "a.json"
        b = temp / "b.json"
        a.write_text(json.dumps({"agent": "A", "write_files": ["same.py"]}), encoding="utf-8")
        b.write_text(json.dumps({"agent": "B", "write_files": ["same.py"]}), encoding="utf-8")
        conflict_ok, conflict_out = run([
            sys.executable,
            "scripts/check_agent_collisions.py",
            str(a),
            str(b),
        ], expected=2)
        lines.append(f"{'GRÜN' if conflict_ok else 'ROT'}: echte Dateikollision wird geblockt")
        if not conflict_ok:
            failures += 1
            lines.append(conflict_out)

        plan = temp / "plan.json"
        plan.write_text(
            json.dumps({"agent": "A", "write_files": ["src/example.py"]}),
            encoding="utf-8",
        )
        scope_ok, scope_out = run([
            sys.executable,
            "scripts/check_iteration_scope.py",
            str(plan),
            "--changed-file",
            "src/example.py",
        ])
        lines.append(f"{'GRÜN' if scope_ok else 'ROT'}: Scope-Guard akzeptiert geplante Datei")
        if not scope_ok:
            failures += 1
            lines.append(scope_out)

        missing_ci = json.loads(
            (ROOT / ".provoware/iterations/0063-two-step-process-metrics.json").read_text(encoding="utf-8")
        )
        missing_ci["ci"]["compile"] = ["tests/does-not-exist-i63.py"]
        missing_manifest = temp / "missing-ci.json"
        missing_manifest.write_text(json.dumps(missing_ci), encoding="utf-8")
        missing_ok, missing_out = run([
            sys.executable,
            "scripts/validate_iteration_manifest.py",
            str(missing_manifest),
        ], expected=2)
        lines.append(f"{'GRÜN' if missing_ok else 'ROT'}: Manifest blockiert nicht vorhandenes CI-Ziel")
        if not missing_ok:
            failures += 1
            lines.append(missing_out)

        for unplanned in (
            "src/unplanned.py",
            ".provoware/unplanned.json",
            "docs/unplanned.md",
            ".github/unplanned.yml",
            "README.md",
        ):
            blocked, blocked_out = run([
                sys.executable,
                "scripts/check_iteration_scope.py",
                str(plan),
                "--changed-file",
                unplanned,
            ], expected=2)
            lines.append(
                f"{'GRÜN' if blocked else 'ROT'}: Scope-Guard blockiert ungeplant {unplanned}"
            )
            if not blocked:
                failures += 1
                lines.append(blocked_out)

    lines.extend([
        "",
        f"FEHLER: {failures}",
        "GESAMTSTATUS: " + ("GRÜN" if failures == 0 else "ROT"),
        "Empfehlung: Governance nur erweitern, wenn ein realer neuer Kollisions- oder Kostenfall entsteht.",
    ])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
