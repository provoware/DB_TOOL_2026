"""I178/I179: Der Selbstcheck muss ein vorhandenes, nichtleeres Editor-JS prüfen."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SELF_CHECK = ROOT / "scripts/repo_self_check.sh"
EDITOR_ASSET = "src/provoware_db/mask_builder/interaction_script.js"


class RepositorySelfCheckAssetTests(unittest.TestCase):
    def _run_isolated(self, *, include_editor_asset: bool, empty_editor_asset: bool = False) -> subprocess.CompletedProcess[str]:
        """Nur Dateiexistenz/Inhalt prüfen; die unabhängigen Python-Gates simulieren."""
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            (fixture / "scripts").mkdir()
            shutil.copy2(SELF_CHECK, fixture / "scripts/repo_self_check.sh")
            source = SELF_CHECK.read_text(encoding="utf-8")
            files = re.search(r"^for f in (.+); do$", source, re.MULTILINE)
            self.assertIsNotNone(files)
            for relative in files.group(1).split():
                path = fixture / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            asset = fixture / EDITOR_ASSET
            if include_editor_asset:
                asset.parent.mkdir(parents=True, exist_ok=True)
                if not empty_editor_asset:
                    asset.write_text("// browser editor script fixture\n", encoding="utf-8")
            else:
                asset.unlink(missing_ok=True)

            fake_bin = fixture / "fake-bin"
            fake_bin.mkdir()
            python_stub = fake_bin / "python3"
            python_stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            python_stub.chmod(0o755)
            env = dict(os.environ, PATH=str(fake_bin) + os.pathsep + os.environ.get("PATH", ""))
            return subprocess.run(
                ["bash", str(fixture / "scripts/repo_self_check.sh")],
                cwd=fixture,
                env=env,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )

    def test_missing_editor_asset_is_a_failing_self_check(self) -> None:
        result = self._run_isolated(include_editor_asset=False)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"ROT: {EDITOR_ASSET} fehlt", result.stdout)
        self.assertIn("GESAMTSTATUS: ROT", result.stdout)

    def test_existing_editor_asset_keeps_self_check_green(self) -> None:
        result = self._run_isolated(include_editor_asset=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"GRÜN: {EDITOR_ASSET} vorhanden", result.stdout)
        self.assertIn("GESAMTSTATUS: GRÜN", result.stdout)

    def test_empty_editor_asset_is_a_failing_self_check(self) -> None:
        result = self._run_isolated(include_editor_asset=True, empty_editor_asset=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(f"ROT: {EDITOR_ASSET} ist leer", result.stdout)
        self.assertIn("GESAMTSTATUS: ROT", result.stdout)


if __name__ == "__main__":
    unittest.main()
