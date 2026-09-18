from __future__ import annotations

from enum import StrEnum


class LayoutMode(StrEnum):
    COMPACT = "compact"
    MEDIUM = "medium"
    WIDE = "wide"


def classify_layout(width: int) -> LayoutMode:
    """Pure responsive policy, testable without Textual.

    Compact deliberately starts below 100 columns rather than squeezing three panes.
    Wide starts at 140 columns where three readable panes fit comfortably.
    """
    if width < 100:
        return LayoutMode.COMPACT
    if width < 140:
        return LayoutMode.MEDIUM
    return LayoutMode.WIDE
