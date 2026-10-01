from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from scripts.install_test_browser import install, installed_executable


def write_archive(path: Path, member: str = "chrome-linux64/chrome") -> str:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, b"#!/bin/sh\nexit 0\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_lock(path: Path, digest: str) -> None:
    path.write_text(json.dumps({
        "schema_version": 1,
        "browser": "chromium",
        "platform": "linux-x86_64",
        "revision": "test-revision",
        "url": "https://storage.googleapis.com/example/chrome.zip",
        "sha256": digest,
        "cache_dir": ".browser-cache/chromium",
        "executable": "chrome-linux64/chrome",
        "allowed_download_hosts": ["storage.googleapis.com"],
    }), encoding="utf-8")


def test_installs_verified_offline_archive(tmp_path: Path) -> None:
    archive = tmp_path / "chrome.zip"
    lock = tmp_path / "browser-lock.json"
    write_lock(lock, write_archive(archive))

    executable = install(lock, archive, tmp_path / "project")

    assert executable.is_file()
    assert executable.stat().st_mode & 0o100
    receipt = json.loads((executable.parents[1] / ".provoware-browser.json").read_text())
    assert receipt["revision"] == "test-revision"
    assert installed_executable(lock, tmp_path / "project") == executable

    receipt["sha256"] = "0" * 64
    (executable.parents[1] / ".provoware-browser.json").write_text(json.dumps(receipt))
    assert installed_executable(lock, tmp_path / "project") is None


def test_rejects_sha256_mismatch(tmp_path: Path) -> None:
    archive = tmp_path / "chrome.zip"
    lock = tmp_path / "browser-lock.json"
    write_archive(archive)
    write_lock(lock, "0" * 64)

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        install(lock, archive, tmp_path / "project")


def test_rejects_archive_path_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "chrome.zip"
    lock = tmp_path / "browser-lock.json"
    digest = write_archive(archive, "../outside")
    write_lock(lock, digest)

    with pytest.raises(ValueError, match="unsafe archive member"):
        install(lock, archive, tmp_path / "project")
