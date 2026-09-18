from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeSpec:
    name: str
    label: str
    primary: str
    secondary: str
    accent: str
    foreground: str
    background: str
    success: str
    warning: str
    error: str
    surface: str
    panel: str
    dark: bool = True


THEME_SPECS: tuple[ThemeSpec, ...] = (
    ThemeSpec("provoware-neon-violet", "Neon Violett", "#A855F7", "#7C3AED", "#00F5FF", "#F8FAFC", "#090712", "#2BFF88", "#FFD84A", "#FF4D6D", "#151126", "#1E1833"),
    ThemeSpec("provoware-neon-cyan", "Neon Cyan", "#00E5FF", "#0077FF", "#39FFB6", "#F4FFFF", "#041014", "#35FF7A", "#FFE45C", "#FF5370", "#092129", "#0D2B35"),
    ThemeSpec("provoware-neon-lime", "Neon Grün", "#7CFF00", "#21D97A", "#00FFD5", "#F7FFF0", "#071008", "#84FF3B", "#FFD84A", "#FF5364", "#112016", "#172B1D"),
    ThemeSpec("provoware-high-contrast", "Maximaler Kontrast", "#FFFF00", "#FFFFFF", "#00FFFF", "#FFFFFF", "#000000", "#00FF66", "#FFFF00", "#FF3B3B", "#090909", "#111111"),
)


def theme_names() -> tuple[str, ...]:
    return tuple(spec.name for spec in THEME_SPECS)


def next_theme(current: str) -> str:
    names = theme_names()
    try:
        index = names.index(current)
    except ValueError:
        return names[0]
    return names[(index + 1) % len(names)]


def build_textual_themes():
    """Build Textual Theme objects lazily so pure tests don't require Textual."""
    from textual.theme import Theme

    return tuple(
        Theme(
            name=s.name,
            primary=s.primary,
            secondary=s.secondary,
            accent=s.accent,
            foreground=s.foreground,
            background=s.background,
            success=s.success,
            warning=s.warning,
            error=s.error,
            surface=s.surface,
            panel=s.panel,
            dark=s.dark,
            variables={
                "footer-key-foreground": s.accent,
                "input-selection-background": f"{s.primary} 35%",
            },
        )
        for s in THEME_SPECS
    )
