from provoware_db.tui.contrast import contrast_ratio
from provoware_db.tui.themes import THEME_SPECS, next_theme


def test_exactly_four_distinct_themes():
    assert len(THEME_SPECS) == 4
    assert len({theme.name for theme in THEME_SPECS}) == 4
    assert any("contrast" in theme.name for theme in THEME_SPECS)


def test_theme_text_contrast_meets_normal_text_target():
    for theme in THEME_SPECS:
        assert contrast_ratio(theme.foreground, theme.background) >= 4.5, theme.name
        assert contrast_ratio(theme.foreground, theme.surface) >= 4.5, theme.name


def test_theme_cycle_is_closed():
    name = THEME_SPECS[0].name
    for _ in range(len(THEME_SPECS)):
        name = next_theme(name)
    assert name == THEME_SPECS[0].name
