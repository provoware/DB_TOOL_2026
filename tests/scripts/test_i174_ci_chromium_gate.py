from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/targeted-iteration.yml"
MANIFEST = ROOT / ".provoware/iterations/0174-ci-chromium-evidence.json"


def main() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    manifest = MANIFEST.read_text(encoding="utf-8")

    required_workflow = (
        'root_path = str(root.resolve())',
        'python_path = src_path + os.pathsep + root_path',
        '[sys.executable, "-W", "error", target]',
        'if: always()',
        'path: runtime/iteration-*',
    )
    missing_workflow = [token for token in required_workflow if token not in workflow]
    if missing_workflow:
        raise SystemExit("I174 CI CHROMIUM GATE: ROT · workflow missing " + ", ".join(missing_workflow))

    required_manifest = (
        '"tests/scripts/test_i174_ci_chromium_gate.py"',
        '"tests/mask_builder/test_i172_chromium_evidence.py"',
        '"screenshot_required": true',
        '"status": "CI_GATE_PENDING"',
    )
    missing_manifest = [token for token in required_manifest if token not in manifest]
    if missing_manifest:
        raise SystemExit("I174 CI CHROMIUM GATE: ROT · manifest missing " + ", ".join(missing_manifest))

    print("I174 CI CHROMIUM GATE: GRÜN · real browser target and evidence upload routed")


if __name__ == "__main__":
    main()
