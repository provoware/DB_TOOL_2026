from __future__ import annotations

from pathlib import Path

from provoware_db.mask_builder.browser_shell import application, make_editor_server, render_editor_shell
from provoware_db.mask_builder.model import GRID_COLUMNS, MaskElementKind


def _request(method: str = "GET", path: str = "/") -> tuple[str, dict[str, str], bytes]:
    captured: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(application({"REQUEST_METHOD": method, "PATH_INFO": path}, start_response))
    return str(captured["status"]), dict(captured["headers"]), body


def test_shell_contains_palette_12_column_canvas_and_preview() -> None:
    html = render_editor_shell()
    assert 'data-grid-columns="12"' in html
    assert html.count('class="grid-column"') == GRID_COLUMNS
    assert 'id="preview"' in html
    for kind in MaskElementKind:
        assert f'data-kind="{kind.value}"' in html
    assert "ohne Speichern und ohne Datenbankzugriff" in html


def test_temporary_interaction_selects_palette_and_places_in_browser_state() -> None:
    html = render_editor_shell()
    assert html.count('class="placement-target"') == GRID_COLUMNS
    assert 'const draftElements = [];' in html
    assert 'button.addEventListener("click", () => selectKind(button));' in html
    assert 'button.addEventListener("click", () => placeAt(Number(button.dataset.column)));' in html
    assert 'draftElements.push({' in html
    assert 'id: "draft-" + String(nextDraftId++)' in html
    assert 'placedLayer.appendChild(card);' in html
    assert 'preview.appendChild(list);' in html


def test_grid_boundaries_are_blocked_before_draft_mutation() -> None:
    html = render_editor_shell()
    assert 'const gridColumns = Number(canvas.dataset.gridColumns);' in html
    assert 'function placementFitsGrid(column, width)' in html
    assert 'column + width <= gridColumns' in html
    assert 'if (!placementFitsGrid(column, selectedWidth)) {' in html
    assert 'Nicht platziert:' in html
    assert 'placementFitsGrid(1, gridColumns)' in html
    assert 'throw new Error("Masken-Baukasten Raster-Selbstprüfung fehlgeschlagen.")' in html
    assert 'data-width="12"' in html
    assert 'data-width="6"' in html
    assert 'data-width="4"' in html


def test_preview_and_draft_identifiers_are_deterministic_and_monotone() -> None:
    html = render_editor_shell()
    assert 'let nextDraftId = 1;' in html
    assert 'id: "draft-" + String(nextDraftId++)' in html
    assert 'draftElements.length + 1' not in html
    assert 'draftElements.forEach((item, index) =>' in html
    assert 'draftElements.forEach((item) =>' in html
    assert 'row.dataset.draftId = item.id;' in html
    forbidden = ("Math.random", "Date.now", "crypto.randomUUID", "performance.now")
    assert all(token not in html for token in forbidden)



def test_move_is_browser_only_preserves_identity_and_changes_column_only() -> None:
    html = render_editor_shell()
    assert 'let movingDraftId = null;' in html
    assert 'function beginMove(id)' in html
    assert 'movingDraftId = id;' in html
    assert 'moveButton.textContent = "Verschieben";' in html
    assert 'moveButton.addEventListener("click", () => beginMove(item.id));' in html
    assert 'const moving = draftElements.find((item) => item.id === movingDraftId);' in html
    assert 'if (!placementFitsGrid(column, moving.width)) {' in html
    assert 'moving.column = column;' in html
    assert 'movingDraftId = null;' in html
    assert 'renderDraft();' in html
    assert 'updateTargetAvailability();' in html
    assert html.count('id: "draft-" + String(nextDraftId++)') == 1
    assert 'moving.id =' not in html
    assert 'moving.kind =' not in html
    assert 'moving.label =' not in html
    assert 'moving.width =' not in html


def test_move_rejects_invalid_target_before_mutation_and_supports_cancel_focus() -> None:
    html = render_editor_shell()
    invalid_guard = html.index('if (!placementFitsGrid(column, moving.width)) {')
    column_mutation = html.index('moving.column = column;')
    assert invalid_guard >= 0
    assert column_mutation > invalid_guard
    invalid_block = html[invalid_guard:column_mutation]
    assert 'return;' in invalid_block

    assert 'function cancelMove()' in html
    assert 'const id = movingDraftId;' in html
    assert 'movingDraftId = null;' in html
    assert 'focusMoveControl(id);' in html
    assert 'candidate.dataset.draftId === id' in html
    assert 'moveButton.dataset.draftId = item.id;' in html
    assert 'event.key === "Escape" && movingDraftId !== null' in html
    assert 'cancelMove();' in html
    assert 'targetButtons[column].focus();' in html
    assert html.count('aria-keyshortcuts="Enter Space ArrowLeft ArrowRight Escape"') == GRID_COLUMNS


def test_move_controls_remain_stacked_at_narrow_width() -> None:
    html = render_editor_shell()
    assert '.placed-element { align-items:stretch; flex-direction:column; }' in html
    assert '.move-draft, .remove-draft { align-self:stretch; width:100%; }' in html


def test_label_edit_is_keyboard_reachable_and_mutates_only_label() -> None:
    html = render_editor_shell()
    assert 'let editingDraftId = null;' in html
    assert 'function beginLabelEdit(id)' in html
    assert 'editingDraftId = id;' in html
    assert 'editButton.type = "button";' in html
    assert 'editButton.textContent = "Beschriftung ändern";' in html
    assert 'editButton.addEventListener("click", () => beginLabelEdit(item.id));' in html
    assert 'input.type = "text";' in html
    assert 'input.className = "label-editor-input";' in html
    assert 'saveButton.type = "submit";' in html
    assert 'saveButton.textContent = "Übernehmen";' in html
    assert 'editor.addEventListener("submit", (event) =>' in html
    assert 'focusLabelEditor(id);' in html

    start = html.index('function saveLabelEdit(id, input)')
    end = html.index('function removeDraft(id)')
    save_block = html[start:end]
    assert 'const nextLabel = input.value.trim();' in save_block
    assert 'item.label = nextLabel;' in save_block
    assert 'renderDraft();' in save_block
    assert 'item.id =' not in save_block
    assert 'item.kind =' not in save_block
    assert 'item.column =' not in save_block
    assert 'item.width =' not in save_block
    assert 'draftElements.push(' not in save_block
    assert 'draftElements.splice(' not in save_block
    assert html.count('id: "draft-" + String(nextDraftId++)') == 1
    assert 'row.dataset.draftId = item.id;' in html
    assert 'row.textContent = (' in html


def test_label_edit_rejects_blank_cancels_with_escape_and_restores_focus() -> None:
    html = render_editor_shell()
    start = html.index('function cancelLabelEdit(id)')
    end = html.index('function removeDraft(id)')
    edit_block = html[start:end]
    assert 'const nextLabel = input.value.trim();' in edit_block
    assert 'if (nextLabel.length === 0) {' in edit_block
    assert 'item.label = nextLabel;' in edit_block
    assert edit_block.index('if (nextLabel.length === 0) {') < edit_block.index('item.label = nextLabel;')
    assert 'input.focus();' in edit_block
    assert 'function focusLabelEditControl(id)' in html
    assert 'candidate.dataset.draftId === id' in html
    assert 'focusLabelEditControl(id);' in edit_block
    assert 'editButton.dataset.draftId = item.id;' in html
    assert 'event.key === "Escape"' in html
    assert 'cancelLabelEdit(item.id);' in html
    assert 'Bearbeitung abgebrochen · Entwurf unverändert.' in html
    assert 'item.id =' not in edit_block
    assert 'item.kind =' not in edit_block
    assert 'item.column =' not in edit_block
    assert 'item.width =' not in edit_block


def test_label_editor_remains_reachable_at_narrow_width() -> None:
    html = render_editor_shell()
    assert '.label-editor, .help-editor { align-items:stretch; flex-direction:column; width:100%; }' in html
    assert '.label-editor-input, .help-editor-input { max-width:none; width:100%; }' in html
    assert '.edit-label, .edit-help, .save-label, .save-help, .move-draft, .remove-draft { align-self:stretch; width:100%; }' in html


def test_help_text_edit_is_browser_only_optional_and_preserves_identity() -> None:
    html = render_editor_shell()
    assert 'let editingHelpDraftId = null;' in html
    assert 'helpText: "",' in html
    assert 'function beginHelpEdit(id)' in html
    assert 'editingHelpDraftId = id;' in html
    assert 'helpButton.type = "button";' in html
    assert 'helpButton.textContent = "Hilfetext ändern";' in html
    assert 'helpButton.addEventListener("click", () => beginHelpEdit(item.id));' in html
    assert 'helpInput.className = "help-editor-input";' in html
    assert 'helpInput.rows = 2;' in html
    assert 'saveHelpButton.type = "submit";' in html
    assert 'saveHelpEdit(item.id, helpInput);' in html
    assert 'focusHelpEditor(id);' in html

    start = html.index('function saveHelpEdit(id, input)')
    end = html.index('function removeDraft(id)')
    save_block = html[start:end]
    assert 'const nextHelpText = input.value.trim();' in save_block
    assert 'item.helpText = nextHelpText;' in save_block
    assert 'renderDraft();' in save_block
    assert 'item.id =' not in save_block
    assert 'item.kind =' not in save_block
    assert 'item.label =' not in save_block
    assert 'item.column =' not in save_block
    assert 'item.width =' not in save_block
    assert 'draftElements.push(' not in save_block
    assert 'draftElements.splice(' not in save_block
    assert html.count('id: "draft-" + String(nextDraftId++)') == 1

    assert 'helpText.textContent = item.helpText;' in html
    assert 'helpText.hidden = item.helpText.length === 0;' in html
    assert '" · Hilfe: " + item.helpText' in html


def test_help_text_accessibility_cancel_focus_and_narrow_layout() -> None:
    html = render_editor_shell()

    assert 'helpText.id = "draft-help-" + item.id;' in html
    assert 'card.setAttribute("role", "group");' in html
    assert 'card.setAttribute("aria-label", item.label);' in html
    assert 'if (item.helpText.length > 0) {' in html
    assert 'card.setAttribute("aria-describedby", helpText.id);' in html

    assert 'function focusHelpEditControl(id)' in html
    assert 'candidate.dataset.draftId === id' in html
    assert 'helpButton.dataset.draftId = item.id;' in html
    assert 'function cancelHelpEdit(id)' in html
    assert 'if (editingHelpDraftId !== id) {' in html
    assert 'editingHelpDraftId = null;' in html
    assert 'focusHelpEditControl(id);' in html
    assert 'event.key === "Escape"' in html
    assert 'cancelHelpEdit(item.id);' in html
    assert 'Hilfetext")' in html
    assert 'Bearbeitung abgebrochen · Entwurf unverändert.' in html

    start = html.index('function cancelHelpEdit(id)')
    end = html.index('function removeDraft(id)')
    help_block = html[start:end]
    assert 'item.helpText =' not in help_block.split('function saveHelpEdit(id, input)')[0]
    assert 'focusHelpEditControl(id);' in help_block

    assert '.label-editor, .help-editor { align-items:stretch; flex-direction:column; width:100%; }' in html
    assert '.label-editor-input, .help-editor-input { max-width:none; width:100%; }' in html
    assert '.edit-label, .edit-help, .save-label, .save-help, .move-draft, .remove-draft { align-self:stretch; width:100%; }' in html

def test_remove_is_browser_only_and_restores_original_target_focus() -> None:
    html = render_editor_shell()
    assert 'function removeDraft(id)' in html
    assert 'draftElements.findIndex((item) => item.id === id)' in html
    assert 'draftElements.splice(index, 1);' in html
    assert 'removeButton.textContent = "Entfernen";' in html
    assert 'removeButton.addEventListener("click", () => removeDraft(item.id));' in html
    assert 'targetButtons[removed.column].focus();' in html
    assert 'emptyState.hidden = draftElements.length > 0;' in html
    assert 'Noch keine Komponenten platziert.' in html



def test_narrow_right_edge_field_keeps_remove_button_reachable() -> None:
    html = render_editor_shell()
    assert 'data-width="4"' in html
    assert 'data-column="8"' in html
    assert '@media (max-width:1000px)' in html
    assert '.placed-element { align-items:stretch; flex-direction:column; }' in html
    assert '.placed-element > span { min-width:0; overflow-wrap:anywhere; }' in html
    assert '.remove-draft { align-self:stretch; width:100%; }' in html

def test_keyboard_contract_uses_native_buttons_focus_and_live_status() -> None:
    html = render_editor_shell()
    assert html.count('aria-keyshortcuts="Enter Space ArrowLeft ArrowRight Escape"') == GRID_COLUMNS
    assert 'button.addEventListener("keydown", (event) =>' in html
    assert 'event.key === "ArrowLeft"' in html
    assert 'event.key === "ArrowRight"' in html
    assert 'targetButtons[next].focus();' in html
    assert 'button:focus-visible' in html
    assert 'outline:3px solid #ffe66d' in html
    assert 'id="interaction-status" role="status" aria-live="polite"' in html


def test_empty_state_hidden_rule_wins_after_placement() -> None:
    html = render_editor_shell()
    assert ".canvas-empty[hidden] { display:none; }" in html


def test_temporary_interaction_has_no_persistence_or_network_write_path() -> None:
    html = render_editor_shell()
    forbidden = (
        "fetch(",
        "XMLHttpRequest",
        "localStorage",
        "sessionStorage",
        "indexedDB",
        'method="post"',
        "WebSocket",
    )
    assert all(token not in html for token in forbidden)


def test_root_is_get_only_and_unknown_paths_are_not_found() -> None:
    status, headers, body = _request()
    assert status == "200 OK"
    assert headers["Cache-Control"] == "no-store"
    assert b"12-Spalten-Arbeitsfl" in body

    status, headers, _ = _request("POST", "/")
    assert status == "405 Method Not Allowed"
    assert headers["Allow"] == "GET"

    status, _, _ = _request("GET", "/api/preview")
    assert status == "404 Not Found"


def test_server_rejects_non_loopback_binding() -> None:
    try:
        make_editor_server("0.0.0.0", 0)
    except ValueError as exc:
        assert "Loopback" in str(exc)
    else:
        raise AssertionError("non-loopback binding must fail closed")


def test_browser_shell_has_no_database_or_store_dependency() -> None:
    source = Path(__file__).parents[2] / "src" / "provoware_db" / "mask_builder" / "browser_shell.py"
    text = source.read_text(encoding="utf-8")
    forbidden = ("MaskTemplateStore", "CatalogService", "sqlite", "repository", "open_connection", "execute(", "INSERT ", "UPDATE ", "DELETE ")
    assert all(token not in text for token in forbidden)


def main() -> None:
    test_shell_contains_palette_12_column_canvas_and_preview()
    test_temporary_interaction_selects_palette_and_places_in_browser_state()
    test_grid_boundaries_are_blocked_before_draft_mutation()
    test_preview_and_draft_identifiers_are_deterministic_and_monotone()
    test_move_is_browser_only_preserves_identity_and_changes_column_only()
    test_move_rejects_invalid_target_before_mutation_and_supports_cancel_focus()
    test_move_controls_remain_stacked_at_narrow_width()
    test_label_edit_is_keyboard_reachable_and_mutates_only_label()
    test_label_edit_rejects_blank_cancels_with_escape_and_restores_focus()
    test_label_editor_remains_reachable_at_narrow_width()
    test_help_text_edit_is_browser_only_optional_and_preserves_identity()
    test_help_text_accessibility_cancel_focus_and_narrow_layout()
    test_remove_is_browser_only_and_restores_original_target_focus()
    test_narrow_right_edge_field_keeps_remove_button_reachable()
    test_keyboard_contract_uses_native_buttons_focus_and_live_status()
    test_empty_state_hidden_rule_wins_after_placement()
    test_temporary_interaction_has_no_persistence_or_network_write_path()
    test_root_is_get_only_and_unknown_paths_are_not_found()
    test_server_rejects_non_loopback_binding()
    test_browser_shell_has_no_database_or_store_dependency()
    print("MASK BUILDER TEMPORARY HELP TEXT I107 STEP 2: GRÜN")


if __name__ == "__main__":
    main()
