from provoware_db.tui.accessibility import DisplayMode, display_label, next_display_mode


def test_display_cycle_has_three_predictable_steps():
    assert next_display_mode(DisplayMode.NORMAL) is DisplayMode.LARGE
    assert next_display_mode(DisplayMode.LARGE) is DisplayMode.EXTRA_LARGE
    assert next_display_mode(DisplayMode.EXTRA_LARGE) is DisplayMode.NORMAL
    assert display_label(DisplayMode.NORMAL) == "Normal"
    assert display_label(DisplayMode.LARGE) == "Groß"
    assert display_label(DisplayMode.EXTRA_LARGE) == "Sehr groß"
