from provoware_db.tui.layout_policy import LayoutMode, classify_layout


def test_required_terminal_sizes_map_to_safe_layouts():
    expected = {
        80: LayoutMode.COMPACT,
        100: LayoutMode.MEDIUM,
        120: LayoutMode.MEDIUM,
        140: LayoutMode.WIDE,
        160: LayoutMode.WIDE,
        200: LayoutMode.WIDE,
    }
    for width, mode in expected.items():
        assert classify_layout(width) is mode


def test_boundaries_are_explicit():
    assert classify_layout(99) is LayoutMode.COMPACT
    assert classify_layout(100) is LayoutMode.MEDIUM
    assert classify_layout(139) is LayoutMode.MEDIUM
    assert classify_layout(140) is LayoutMode.WIDE
