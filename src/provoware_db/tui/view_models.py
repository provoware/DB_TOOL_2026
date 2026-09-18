from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, Sequence


class HealthLevel(StrEnum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class NavItem:
    id: str
    label: str
    meta: str = ""


@dataclass(frozen=True)
class FieldRow:
    id: str
    label: str
    value: str
    field_type: str
    required: bool = False
    help_text: str | None = None


@dataclass(frozen=True)
class HealthItem:
    label: str
    level: HealthLevel
    detail: str


@dataclass(frozen=True)
class EventItem:
    time_label: str
    symbol: str
    text: str


class TuiDataPort(Protocol):
    def categories(self) -> Sequence[NavItem]: ...
    def entries(self, category_id: str) -> Sequence[NavItem]: ...
    def fields(self, entry_id: str) -> Sequence[FieldRow]: ...
    def health(self) -> Sequence[HealthItem]: ...
    def recent_events(self, limit: int = 10) -> Sequence[EventItem]: ...
