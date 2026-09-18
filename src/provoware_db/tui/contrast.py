from __future__ import annotations


def _rgb(hex_color: str) -> tuple[float, float, float]:
    value = hex_color.removeprefix("#")
    if len(value) != 6:
        raise ValueError("Hex-Farbe muss sechs Stellen haben.")
    return tuple(int(value[i:i+2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def _linear(channel: float) -> float:
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    r, g, b = (_linear(c) for c in _rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(first: str, second: str) -> float:
    a, b = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (a + 0.05) / (b + 0.05)
