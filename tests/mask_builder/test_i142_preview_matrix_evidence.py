from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import threading

from provoware_db.mask_builder.browser_shell import make_editor_server


ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).with_name("i142_preview_matrix_evidence.mjs")
OUTPUT = ROOT / "runtime" / "iteration-0142" / "preview-matrix-evidence.json"


def main() -> int:
    node = shutil.which("node")
    if node is None:
        raise SystemExit("I142 EVIDENCE: ROT · node executable missing")

    subprocess.run([node, "--check", str(HARNESS)], check=True)

    server = make_editor_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [node, str(HARNESS), f"http://{host}:{port}/", str(OUTPUT)],
            cwd=ROOT,
            text=True,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    if not OUTPUT.is_file():
        raise SystemExit("I142 EVIDENCE: ROT · evidence file missing")

    evidence = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if evidence.get("overall_status") != "GREEN":
        print(OUTPUT.read_text(encoding="utf-8"))
        raise SystemExit(result.returncode or 2)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    checks = evidence.get("checks", [])
    modes = [(item["mode"], item["width"]) for item in checks]
    if modes != [("desktop", "1152"), ("tablet", "768"), ("narrow", "360")]:
        raise SystemExit(f"I142 EVIDENCE: ROT · unexpected viewport matrix {modes!r}")

    print("I142 REAL CHROMIUM PREVIEW MATRIX: GRÜN · Desktop 1152 + Tablet 768 + Schmal 360")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
