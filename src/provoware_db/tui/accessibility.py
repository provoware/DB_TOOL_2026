from __future__ import annotations

from enum import StrEnum


class DisplayMode(StrEnum):
    NORMAL = "normal"
    LARGE = "large"
    EXTRA_LARGE = "extra-large"


_DISPLAY_ORDER = (DisplayMode.NORMAL, DisplayMode.LARGE, DisplayMode.EXTRA_LARGE)


def next_display_mode(current: DisplayMode) -> DisplayMode:
    index = _DISPLAY_ORDER.index(current)
    return _DISPLAY_ORDER[(index + 1) % len(_DISPLAY_ORDER)]


def display_label(mode: DisplayMode) -> str:
    return {
        DisplayMode.NORMAL: "Normal",
        DisplayMode.LARGE: "Groß",
        DisplayMode.EXTRA_LARGE: "Sehr groß",
    }[mode]
