from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "src/provoware_db/web/templates/index.html").read_text(encoding="utf-8")
CSS = (ROOT / "src/provoware_db/web/static/app.css").read_text(encoding="utf-8")


def test_three_stage_structure_and_core_ui_regions_exist():
    required = (
        'id="categories"',
        'id="entries"',
        'id="fields"',
        'class="health-summary"',
        'class="actions"',
        'id="events-title"',
    )
    for marker in required:
        assert marker in HTML


def test_accessibility_and_keyboard_focus_contract():
    assert 'lang="de"' in HTML
    assert 'aria-label="Arbeitsschritte"' in HTML
    assert 'role="status"' in HTML
    assert ":focus-visible" in CSS
    assert "outline:" in CSS


def test_responsive_breakpoints_and_no_sql_in_frontend_shell():
    assert "@media (max-width: 1399px)" in CSS
    assert "@media (max-width: 799px)" in CSS
    combined = (HTML + CSS).lower()
    for forbidden in ("select * from", "insert into", "update ", "delete from", "sqlite3"):
        assert forbidden not in combined
