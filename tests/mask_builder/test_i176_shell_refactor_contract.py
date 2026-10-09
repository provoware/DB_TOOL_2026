"""I176: prüft den unveränderten Masken-Editor vor einer möglichen Dateiaufteilung.

Keine produktive Datenbank, kein Dateischreibzugriff, keine Browsermutation.
"""
from __future__ import annotations

import subprocess
import unittest

from provoware_db.mask_builder.browser_shell import application, render_editor_shell


class ShellSplitContractTests(unittest.TestCase):
    def test_inlined_assets_have_stable_boundaries_and_valid_javascript(self) -> None:
        html = render_editor_shell()
        self.assertEqual(html.count("<style>"), 1)
        self.assertEqual(html.count("</style>"), 1)
        self.assertEqual(html.count("<script>"), 1)
        self.assertEqual(html.count("</script>"), 1)
        self.assertLess(html.index("<style>"), html.index("<script>"))
        self.assertTrue(html.partition("<style>")[2].partition("</style>")[0].strip())

        script = html.partition("<script>")[2].partition("</script>")[0]
        self.assertIn('"use strict";', script)
        result = subprocess.run(
            ["node", "--check", "-"], input=script, text=True,
            capture_output=True, check=False, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_get_response_matches_rendered_document_byte_for_byte(self) -> None:
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        payload = b"".join(
            application({"REQUEST_METHOD": "GET", "PATH_INFO": "/"}, start_response)
        )
        self.assertEqual(captured["status"], "200 OK")
        self.assertEqual(payload, render_editor_shell().encode("utf-8"))
        self.assertEqual(int(captured["headers"]["Content-Length"]), len(payload))
        self.assertEqual(captured["headers"]["Cache-Control"], "no-store")

    def test_extraction_does_not_introduce_write_or_remote_routes(self) -> None:
        html = render_editor_shell()
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "indexedDB", "WebSocket"):
            self.assertNotIn(forbidden, html)
        for method, path, expected in [
            ("POST", "/", "405 Method Not Allowed"),
            ("PUT", "/", "405 Method Not Allowed"),
            ("GET", "/assets/editor.js", "404 Not Found"),
            ("GET", "/api/save", "404 Not Found"),
        ]:
            observed = []

            def start_response(status, headers):
                observed.append(status)

            application({"REQUEST_METHOD": method, "PATH_INFO": path}, start_response)
            self.assertEqual(observed, [expected])


if __name__ == "__main__":
    unittest.main()
