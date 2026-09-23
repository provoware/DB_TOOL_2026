from __future__ import annotations

import json
import os
from pathlib import Path
import re
from uuid import uuid4

from provoware_db.mask_builder.model import (
    MaskTemplate,
    MaskValidationError,
    require_valid_template,
    template_from_dict,
    template_to_dict,
)


_SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


class TemplateStoreError(RuntimeError):
    pass


class TemplateStoreConflict(TemplateStoreError):
    pass


class MaskTemplateStore:
    """Atomic JSON store for validated mask templates outside authoritative DBs."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def _target(self, template_id: str) -> Path:
        if not _SAFE_ID_RE.fullmatch(template_id):
            raise TemplateStoreError("STORE-400: Vorlagen-ID ist für Dateispeicherung ungültig.")
        return self.root / f"{template_id}.json"

    def load(self, template_id: str) -> MaskTemplate:
        target = self._target(template_id)
        if not target.is_file():
            raise FileNotFoundError(f"STORE-404: Vorlage wurde nicht gefunden: {template_id}")
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TemplateStoreError(f"STORE-422: Vorlagendatei ist beschädigt: {template_id}") from exc
        if not isinstance(raw, dict):
            raise TemplateStoreError(f"STORE-422: Vorlagendatei hat ein ungültiges Format: {template_id}")
        try:
            template = template_from_dict(raw)
        except MaskValidationError as exc:
            raise TemplateStoreError(f"STORE-422: Vorlage ist inkompatibel oder ungültig: {template_id}") from exc
        if template.id != template_id:
            raise TemplateStoreError("STORE-423: Vorlagen-ID stimmt nicht mit dem Dateinamen überein.")
        return template

    def list_templates(self) -> tuple[MaskTemplate, ...]:
        if not self.root.exists():
            return ()
        templates = [self.load(path.stem) for path in sorted(self.root.glob("*.json"))]
        return tuple(sorted(templates, key=lambda item: (item.name.casefold(), item.id)))

    def save(
        self,
        template: MaskTemplate,
        *,
        expected_current_version: int | None = None,
    ) -> Path:
        require_valid_template(template)
        target = self._target(template.id)
        self.root.mkdir(parents=True, exist_ok=True)

        if target.exists():
            current = self.load(template.id)
            if expected_current_version is None:
                raise TemplateStoreConflict(
                    "STORE-409: Bestehende Vorlage darf nur mit bekannter Vorversion aktualisiert werden."
                )
            if current.version != expected_current_version:
                raise TemplateStoreConflict(
                    f"STORE-410: Versionskonflikt. Erwartet {expected_current_version}, vorhanden {current.version}."
                )
            if template.version <= current.version:
                raise TemplateStoreConflict(
                    "STORE-411: Neue Vorlagenversion muss größer als die bestehende Version sein."
                )
        elif expected_current_version is not None:
            raise TemplateStoreConflict(
                "STORE-412: Eine erwartete Vorversion wurde angegeben, aber die Vorlage existiert nicht."
            )

        payload = json.dumps(
            template_to_dict(template),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        ) + "\n"
        temp = self.root / f".{template.id}.{uuid4().hex}.tmp"
        try:
            with temp.open("x", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
            try:
                dir_fd = os.open(self.root, os.O_RDONLY)
            except OSError:
                dir_fd = None
            if dir_fd is not None:
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
        finally:
            if temp.exists():
                temp.unlink()
        return target
