from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Callable, Iterable, TypeVar
from uuid import uuid4

from provoware_db.storage.sqlite.errors import PostCommitValidationError
from provoware_db.validation.gates import Check, execute_validated_write

from .operation_journal import OperationJournal

T = TypeVar("T")
_CODE_RE = re.compile(r"\b([A-Z]{2,5}-\d{3})\b")


def _error_code(exc: BaseException) -> str | None:
    match = _CODE_RE.search(str(exc))
    return match.group(1) if match else None


class CoordinatedWriter:
    """Coordinates durable state journal with one transactional main.db write."""

    def __init__(
        self,
        main_con: sqlite3.Connection,
        state_con: sqlite3.Connection,
        main_db_path: Path,
        *,
        app_session_id: str,
        app_version: str,
    ) -> None:
        self.main_con = main_con
        self.main_db_path = Path(main_db_path)
        self.journal = OperationJournal(state_con, app_session_id=app_session_id, app_version=app_version)

    def execute(
        self,
        *,
        operation_type: str,
        entity_type: str | None,
        entity_id: str | None,
        action: Callable[[sqlite3.Connection, str], T],
        preconditions: Iterable[Check] = (),
        transactional_postconditions_factory: Callable[[str], Iterable[Check]] | None = None,
        committed_postconditions_factory: Callable[[str], Iterable[Check]] | None = None,
    ) -> tuple[str, T]:
        operation_id = f"op_{uuid4().hex}"
        self.journal.start(operation_id, operation_type, entity_type, entity_id)
        tx_checks = () if transactional_postconditions_factory is None else transactional_postconditions_factory(operation_id)
        committed_checks = () if committed_postconditions_factory is None else committed_postconditions_factory(operation_id)
        try:
            result = execute_validated_write(
                self.main_con,
                self.main_db_path,
                lambda con: action(con, operation_id),
                preconditions=preconditions,
                transactional_postconditions=tx_checks,
                committed_postconditions=committed_checks,
            )
        except PostCommitValidationError as exc:
            self.journal.mark_failed(operation_id, error_code=_error_code(exc) or "VAL-330")
            raise
        except Exception as exc:
            self.journal.mark_rolled_back(operation_id, error_code=_error_code(exc))
            raise
        self.journal.mark_committed(operation_id)
        return operation_id, result
