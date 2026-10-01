from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import tempfile
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = ROOT / ".provoware" / "browser-lock.json"
MAX_ARCHIVE_BYTES = 1_000_000_000


def load_lock(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version", "browser", "platform", "revision", "url", "sha256",
        "cache_dir", "executable", "allowed_download_hosts",
    }
    if set(data) != required or data["schema_version"] != 1:
        raise ValueError("browser lock has an unsupported shape or schema")
    for key in ("browser", "platform", "revision", "url", "sha256", "cache_dir", "executable"):
        if not isinstance(data[key], str):
            raise ValueError(f"browser lock field {key!r} must be a string")
    if not isinstance(data["allowed_download_hosts"], list) or not all(
        isinstance(item, str) and item for item in data["allowed_download_hosts"]
    ):
        raise ValueError("allowed_download_hosts must contain non-empty strings")
    return data


def safe_relative(raw: str, label: str) -> Path:
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe {label}: {raw!r}")
    return Path(*path.parts)


def validate_config(lock: dict[str, Any]) -> None:
    if lock["revision"] == "UNCONFIGURED":
        raise ValueError("browser lock is unconfigured; pin revision, URL and SHA-256")
    if len(lock["sha256"]) != 64 or any(char not in "0123456789abcdef" for char in lock["sha256"]):
        raise ValueError("browser lock SHA-256 must be 64 lowercase hexadecimal characters")
    safe_relative(lock["cache_dir"], "cache_dir")
    safe_relative(lock["executable"], "executable")


def obtain_archive(lock: dict[str, Any], supplied: Path | None, destination: Path) -> None:
    if supplied is not None:
        shutil.copyfile(supplied, destination)
        return
    parsed = urlparse(lock["url"])
    if parsed.scheme != "https" or parsed.hostname not in lock["allowed_download_hosts"]:
        raise ValueError("browser URL must use HTTPS and an allowed host")
    with urlopen(lock["url"], timeout=60) as response, destination.open("wb") as output:
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in lock["allowed_download_hosts"]:
            raise ValueError("browser download redirect left the allowed HTTPS hosts")
        shutil.copyfileobj(response, output)


def verify_archive(path: Path, expected: str) -> None:
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError("browser archive exceeds the size limit")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected:
        raise ValueError(f"browser archive SHA-256 mismatch: expected {expected}, got {digest}")


def safe_extract(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as bundle:
        if sum(info.file_size for info in bundle.infolist()) > MAX_ARCHIVE_BYTES:
            raise ValueError("extracted browser archive exceeds the size limit")
        for info in bundle.infolist():
            relative = safe_relative(info.filename, "archive member")
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"symbolic links are forbidden in browser archive: {info.filename!r}")
            target = destination / relative
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def installed_executable(lock_path: Path, root: Path) -> Path | None:
    lock = load_lock(lock_path)
    try:
        validate_config(lock)
    except ValueError:
        return None
    target = root / safe_relative(lock["cache_dir"], "cache_dir") / lock["revision"]
    executable = target / safe_relative(lock["executable"], "executable")
    receipt = target / ".provoware-browser.json"
    if not executable.is_file() or not os.access(executable, os.X_OK) or not receipt.is_file():
        return None
    try:
        recorded = json.loads(receipt.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if recorded != {"revision": lock["revision"], "sha256": lock["sha256"]}:
        return None
    return executable


def install(lock_path: Path, archive: Path | None, root: Path) -> Path:
    lock = load_lock(lock_path)
    validate_config(lock)
    cache = root / safe_relative(lock["cache_dir"], "cache_dir")
    target = cache / lock["revision"]
    with tempfile.TemporaryDirectory(prefix="provoware-browser-") as raw_temp:
        temp = Path(raw_temp)
        bundle = temp / "browser.zip"
        unpacked = temp / "unpacked"
        unpacked.mkdir()
        obtain_archive(lock, archive, bundle)
        verify_archive(bundle, lock["sha256"])
        safe_extract(bundle, unpacked)
        executable_relative = safe_relative(lock["executable"], "executable")
        executable = unpacked / executable_relative
        if not executable.is_file():
            raise ValueError(f"browser executable missing from archive: {lock['executable']}")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        cache.mkdir(parents=True, exist_ok=True)
        existing = installed_executable(lock_path, root)
        if existing is not None:
            return existing
        if target.exists():
            raise ValueError(f"browser target exists without a valid receipt: {target}")
        staging = Path(tempfile.mkdtemp(prefix=".install-", dir=cache))
        try:
            payload = staging / "payload"
            shutil.copytree(unpacked, payload)
            receipt = payload / ".provoware-browser.json"
            receipt.write_text(
                json.dumps({"revision": lock["revision"], "sha256": lock["sha256"]}, sort_keys=True) + "\n"
            )
            os.replace(payload, target)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
    return target / safe_relative(lock["executable"], "executable")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install a pinned project-local Chromium archive.")
    parser.add_argument("--lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        executable = install(args.lock.resolve(), args.archive.resolve() if args.archive else None, args.root.resolve())
    except (OSError, ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"TEST BROWSER INSTALL: ROT · {exc}")
        return 2
    print(f"TEST BROWSER INSTALL: GRÜN · {executable}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
