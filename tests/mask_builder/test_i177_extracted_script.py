"""I177: unverändertes Inline-HTML beim Auslagern des Interaktionsskripts."""
from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import unittest

from provoware_db.mask_builder.browser_shell import (
    _INTERACTION_SCRIPT,
    application,
    render_editor_shell,
)

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "src/provoware_db/mask_builder/interaction_script.js"
BASELINE_GIT_BLOB = "20fd1f9b5080c4cf53b738b3109697d6bfd28851"


class ExtractionRegressionTests(unittest.TestCase):
    def test_inlined_script_is_byte_for_byte_identical_to_pre_refactor_source(self) -> None:
        javascript = ASSET.read_text(encoding="utf-8")
        self.assertEqual(
            _INTERACTION_SCRIPT, "\n<script>\n" + javascript + "\n</script>\n"
        )
        original = _INTERACTION_SCRIPT.encode("utf-8")
        actual = hashlib.sha1(
            b"blob " + str(len(original)).encode("ascii") + b"\0" + original
        ).hexdigest()
        self.assertEqual(actual, BASELINE_GIT_BLOB)
        self.assertEqual(render_editor_shell().count(_INTERACTION_SCRIPT), 1)

    def test_extracted_file_contains_only_js_and_remains_syntactically_valid(self) -> None:
        javascript = ASSET.read_text(encoding="utf-8")
        self.assertNotIn("<script", javascript)
        self.assertNotIn("</script", javascript)
        check = subprocess.run(
            ["node", "--check", str(ASSET)],
            capture_output=True, text=True, check=False, timeout=30,
        )
        self.assertEqual(check.returncode, 0, check.stderr)

    def test_http_response_is_exact_generated_html_and_still_read_only(self) -> None:
        observed = {}

        def start_response(status, headers):
            observed["status"] = status
            observed["headers"] = dict(headers)

        body = b"".join(
            application({"REQUEST_METHOD": "GET", "PATH_INFO": "/"}, start_response)
        )
        self.assertEqual(observed["status"], "200 OK")
        self.assertEqual(body, render_editor_shell().encode("utf-8"))
        self.assertEqual(int(observed["headers"]["Content-Length"]), len(body))
        self.assertEqual(observed["headers"]["Cache-Control"], "no-store")
        for method, path, expected in (
            ("POST", "/", "405 Method Not Allowed"),
            ("GET", "/interaction_script.js", "404 Not Found"),
            ("GET", "/api/save", "404 Not Found"),
        ):
            statuses = []
            application(
                {"REQUEST_METHOD": method, "PATH_INFO": path},
                lambda status, headers: statuses.append(status),
            )
            self.assertEqual(statuses, [expected])


if __name__ == "__main__":
    unittest.main()
