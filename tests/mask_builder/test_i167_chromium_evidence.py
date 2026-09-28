from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import threading

from provoware_db.mask_builder.browser_shell import make_editor_server


ROOT = Path(__file__).resolve().parents[2]
HARNESS = Path(__file__).with_name("i167_chromium_evidence.mjs")
OUTPUT = ROOT / "runtime" / "iteration-0167" / "chromium-evidence.json"
BROWSERS = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser")


def browser_executable() -> str | None:
    return next((path for name in BROWSERS if (path := shutil.which(name))), None)


def main() -> int:
    node = shutil.which("node")
    if node is None:
        print("I167 CHROMIUM GATE: RED · node executable missing")
        return 2

    syntax = subprocess.run([node, "--check", str(HARNESS)], check=False)
    if syntax.returncode != 0:
        print("I167 CHROMIUM GATE: RED · harness syntax invalid")
        return 2

    browser = browser_executable()
    if browser is None:
        print("I167 CHROMIUM GATE: BLOCKED · Chrome/Chromium executable missing")
        return 3

    server = make_editor_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [node, str(HARNESS), f"http://{host}:{port}/", str(OUTPUT)],
            cwd=ROOT,
            check=False,
        )
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    if not OUTPUT.is_file():
        print(f"I167 CHROMIUM GATE: RED · evidence missing · browser={browser}")
        return 2

    try:
        evidence = json.loads(OUTPUT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"I167 CHROMIUM GATE: RED · evidence unreadable · {exc}")
        return 2

    if result.returncode != 0 or evidence.get("overall_status") != "GREEN":
        failures = evidence.get("failures", ["unknown failure"])
        print("I167 CHROMIUM GATE: RED · " + ", ".join(failures))
        return 2

    screenshot = Path(evidence.get("screenshot_path", ""))
    if not screenshot.is_file() or not evidence.get("screenshot_sha256"):
        print("I167 CHROMIUM GATE: RED · screenshot evidence incomplete")
        return 2

    print(
        "I167 CHROMIUM GATE: GREEN · required states, keyboard tooltips, "
        "live status and 1440x900 dark screenshot verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
