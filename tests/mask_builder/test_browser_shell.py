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
    assert '.label-editor, .help-editor, .option-editor { align-items:stretch; flex-direction:column; width:100%; }' in html
    assert '.label-editor-input, .help-editor-input, .option-editor-input { max-width:none; width:100%; }' in html
    assert '.edit-label, .edit-help, .save-label, .save-help, .toggle-required, .datatype-select, .default-value-control, .add-option, .move-draft, .remove-draft { align-self:stretch; width:100%; }' in html


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

    assert '.label-editor, .help-editor, .option-editor { align-items:stretch; flex-direction:column; width:100%; }' in html
    assert '.label-editor-input, .help-editor-input, .option-editor-input { max-width:none; width:100%; }' in html
    assert '.edit-label, .edit-help, .save-label, .save-help, .toggle-required, .datatype-select, .default-value-control, .add-option, .move-draft, .remove-draft { align-self:stretch; width:100%; }' in html


def test_required_toggle_is_browser_only_and_mutates_only_required_state() -> None:
    html = render_editor_shell()
    assert 'isRequired: false,' in html
    assert 'function toggleRequired(id)' in html
    assert 'item.isRequired = !item.isRequired;' in html
    assert 'requiredButton.type = "button";' in html
    assert 'requiredButton.className = "toggle-required";' in html
    assert 'requiredButton.dataset.draftId = item.id;' in html
    assert 'requiredButton.setAttribute("aria-pressed", String(item.isRequired));' in html
    assert 'requiredButton.addEventListener("click", () => toggleRequired(item.id));' in html
    assert 'item.isRequired ? "Pflichtfeld: Ja" : "Pflichtfeld: Nein"' in html
    assert '(item.isRequired ? " · Pflichtfeld" : "")' in html

    start = html.index('function toggleRequired(id)')
    end = html.index('function removeDraft(id)')
    toggle_block = html[start:end]
    assert 'item.isRequired = !item.isRequired;' in toggle_block
    assert 'renderDraft();' in toggle_block
    assert 'item.id =' not in toggle_block
    assert 'item.kind =' not in toggle_block
    assert 'item.label =' not in toggle_block
    assert 'item.helpText =' not in toggle_block
    assert 'item.column =' not in toggle_block
    assert 'item.width =' not in toggle_block
    assert 'draftElements.push(' not in toggle_block
    assert 'draftElements.splice(' not in toggle_block
    assert html.count('id: "draft-" + String(nextDraftId++)') == 1


def test_required_toggle_is_field_only_accessible_and_narrow_safe() -> None:
    html = render_editor_shell()

    assert 'if (item.kind === "field") {' in html
    assert 'requiredState.className = "required-state";' in html
    assert 'requiredState.id = "draft-required-" + item.id;' in html
    assert 'requiredState.textContent = item.isRequired ? "Pflichtfeld" : "Optional";' in html
    assert 'requiredButton.setAttribute("aria-describedby", requiredState.id);' in html

    render_start = html.index('function renderDraft()')
    render_end = html.index('function selectKind(button)')
    render_block = html[render_start:render_end]
    field_guard = render_block.index('if (item.kind === "field") {')
    required_button = render_block.index('const requiredButton = document.createElement("button");')
    move_button = render_block.index('const moveButton = document.createElement("button");')
    assert field_guard >= 0
    assert required_button > field_guard
    assert move_button > required_button

    assert '.required-state, .datatype-label, .default-value-label { color:#d7def5; font-weight:600; }' in html
    assert '.edit-label, .edit-help, .save-label, .save-help, .toggle-required, .datatype-select, .default-value-control, .add-option, .move-draft, .remove-draft { align-self:stretch; width:100%; }' in html



def test_datatype_is_field_only_browser_local_and_mutates_only_datatype() -> None:
    html = render_editor_shell()
    assert 'dataType: selectedKind === "field" ? "text" : null,' in html
    assert 'function changeDataType(id, select)' in html
    assert 'item.kind !== "field"' in html
    assert 'item.dataType = select.value;' in html
    assert 'dataTypeSelect.className = "datatype-select";' in html
    assert 'dataTypeSelect.dataset.draftId = item.id;' in html
    assert 'dataTypeSelect.setAttribute("aria-labelledby", dataTypeLabel.id);' in html
    assert '["text", "Text"]' in html
    assert '["number", "Zahl"]' in html
    assert '["date", "Datum"]' in html
    assert '["boolean", "Ja/Nein"]' in html
    assert 'dataTypeSelect.addEventListener("change", () => changeDataType(item.id, dataTypeSelect));' in html
    assert '(item.kind === "field" ? " · Datentyp: " + item.dataType : "")' in html

    start = html.index('function changeDataType(id, select)')
    end = html.index('function removeDraft(id)')
    datatype_block = html[start:end]
    assert 'item.dataType = select.value;' in datatype_block
    assert 'renderDraft();' in datatype_block
    assert 'item.id =' not in datatype_block
    assert 'item.kind =' not in datatype_block
    assert 'item.label =' not in datatype_block
    assert 'item.helpText =' not in datatype_block
    assert 'item.isRequired =' not in datatype_block
    assert 'item.column =' not in datatype_block
    assert 'item.width =' not in datatype_block
    assert 'draftElements.push(' not in datatype_block
    assert 'draftElements.splice(' not in datatype_block
    assert html.count('id: "draft-" + String(nextDraftId++)') == 1





def test_choice_datatypes_are_browser_local_and_keep_scalar_default_inactive() -> None:
    html = render_editor_shell()
    assert 'function isChoiceDataType(dataType)' in html
    assert 'dataType === "single_choice" || dataType === "multi_choice"' in html
    assert '["single_choice", "Einfachauswahl"]' in html
    assert '["multi_choice", "Mehrfachauswahl"]' in html
    assert 'if (!isChoiceDataType(item.dataType)) {' in html
    assert 'item.kind !== "field" || isChoiceDataType(item.dataType) || item.defaultValue.length === 0' in html

    start = html.index('function changeDataType(id, select)')
    end = html.index('function isChoiceDataType(dataType)')
    change_block = html[start:end]
    assert 'item.dataType = select.value;' in change_block
    assert 'item.defaultValue =' not in change_block
    assert 'defaultValue = ' not in change_block

    assert 'defaultSelection' not in html




def test_choice_datatype_incomplete_state_focus_preview_and_narrow_semantics() -> None:
    html = render_editor_shell()
    assert 'choiceState.className = "choice-state";' in html
    assert 'choiceState.id = "draft-choice-state-" + item.id;' in html
    assert 'choiceState.textContent = item.options.length === 0' in html
    assert '"Auswahltyp unvollständig · noch keine Optionen konfiguriert."' in html
    assert 'dataTypeSelect.setAttribute("aria-describedby", choiceState.id);' in html
    assert '" · Auswahloptionen: noch nicht konfiguriert"' in html
    assert '" · Auswahltyp unvollständig: noch keine Optionen konfiguriert"' in html
    assert '.choice-state { color:#b8bfd2; font-weight:600; overflow-wrap:anywhere; }' in html
    assert '.placed-element > span, .datatype-label, .default-value-label, .choice-state { min-width:0; overflow-wrap:anywhere; }' in html

    start = html.index('function changeDataType(id, select)')
    end = html.index('function isChoiceDataType(dataType)')
    change_block = html[start:end]
    assert 'renderDraft();' in change_block
    assert 'focusDataTypeControl(id);' in change_block
    assert change_block.index('renderDraft();') < change_block.index('focusDataTypeControl(id);')
    assert 'item.defaultValue =' not in change_block

    assert 'defaultSelection' not in html
    assert 'draft-option-' not in html
    assert 'option-editor' not in html




def test_choice_option_add_is_browser_local_monotone_and_append_only() -> None:
    html = render_editor_shell()
    assert 'let nextDraftOptionId = 1;' in html
    assert 'options: selectedKind === "field" ? [] : null,' in html
    assert 'function addDraftOption(id, input)' in html
    assert 'item.kind !== "field" || !isChoiceDataType(item.dataType)' in html
    assert 'const label = input.value.trim();' in html
    assert 'if (label.length === 0) {' in html
    assert 'option.label.toLowerCase() === label.toLowerCase()' in html
    assert 'item.options.push({' in html
    assert 'id: "draft-option-" + String(nextDraftOptionId++),' in html
    assert 'label,' in html
    assert 'focusOptionInput(id);' in html

    start = html.index('function addDraftOption(id, input)')
    end = html.index('function removeDraft(id)')
    add_block = html[start:end]
    mutation = add_block.index('item.options.push({')
    assert add_block.index('if (label.length === 0) {') < mutation
    assert add_block.index('if (duplicate) {') < mutation
    assert 'item.id =' not in add_block
    assert 'item.dataType =' not in add_block
    assert 'item.defaultValue =' not in add_block
    assert 'item.column =' not in add_block
    assert 'item.width =' not in add_block
    assert 'item.options.splice(' not in add_block
    assert '.sort(' not in add_block

    assert 'optionEditor.className = "option-editor";' in html
    assert 'optionInput.className = "option-editor-input";' in html
    assert 'addOptionButton.className = "add-option";' in html
    assert 'addDraftOption(item.id, optionInput);' in html
    assert 'optionRow.dataset.optionId = option.id;' in html
    assert 'item.options.forEach((option) =>' in html
    assert 'item.options.map((option) => option.label).join(" | ")' in html

    assert 'remove-option' not in html
    assert 'reorder-option' not in html
    assert 'move-option' not in html
    assert 'defaultSelection' not in html


def test_default_value_is_field_only_browser_local_and_type_validated() -> None:
    html = render_editor_shell()
    assert 'defaultValue: selectedKind === "field" ? "" : null,' in html
    assert 'function defaultValueCandidate(dataType, rawValue)' in html
    assert 'function updateDefaultValue(id, control)' in html
    assert 'item.kind !== "field"' in html
    assert 'item.defaultValue = candidate.value;' in html
    assert 'Number.isFinite(parsed)' in html
    assert '/^\\\\d{4}-\\\\d{2}-\\\\d{2}$/.test(value)' in html
    assert 'parsed.toISOString().slice(0, 10) === value' in html
    assert '["", "true", "false"].includes(value)' in html
    assert 'defaultValueControl.className = "default-value-control";' in html
    assert 'defaultValueControl.addEventListener("change", () => updateDefaultValue(item.id, defaultValueControl));' in html
    assert 'defaultValueControl.inputMode = "decimal";' in html
    assert 'defaultValueControl.placeholder = "JJJJ-MM-TT";' in html
    assert '["", "Leer"]' in html
    assert '["true", "Ja"]' in html
    assert '["false", "Nein"]' in html
    assert '" · Standard: " + defaultValuePreview(item)' in html

    start = html.index('function updateDefaultValue(id, control)')
    end = html.index('function defaultValuePreview(item)')
    update_block = html[start:end]
    invalid_guard = update_block.index('if (!candidate.valid) {')
    mutation = update_block.index('item.defaultValue = candidate.value;')
    assert invalid_guard >= 0
    assert mutation > invalid_guard
    assert 'return;' in update_block[invalid_guard:mutation]
    assert 'item.id =' not in update_block
    assert 'item.kind =' not in update_block
    assert 'item.label =' not in update_block
    assert 'item.helpText =' not in update_block
    assert 'item.isRequired =' not in update_block
    assert 'item.dataType =' not in update_block
    assert 'item.column =' not in update_block
    assert 'item.width =' not in update_block
    assert 'draftElements.push(' not in update_block
    assert 'draftElements.splice(' not in update_block
    assert html.count('id: "draft-" + String(nextDraftId++)') == 1


def test_default_value_semantics_focus_and_narrow_layout() -> None:
    html = render_editor_shell()
    assert 'function focusDefaultValueControl(id)' in html
    assert 'placedLayer.querySelectorAll(".default-value-control")' in html
    assert html.count('focusDefaultValueControl(id);') >= 2

    assert 'defaultValueLabel = document.createElement("label")' in html
    assert 'defaultValueLabel.id = "draft-default-value-label-" + item.id;' in html
    assert 'defaultValueControl.id = "draft-default-value-" + item.id;' in html
    assert 'defaultValueLabel.htmlFor = defaultValueControl.id;' in html
    assert 'defaultValueControl.setAttribute("aria-labelledby", defaultValueLabel.id);' in html
    assert 'aria-label", item.label + " · Standardwert"' not in html

    assert 'button:focus-visible, select:focus-visible, input:focus-visible' in html
    assert '.placed-element > span, .datatype-label, .default-value-label, .choice-state { min-width:0; overflow-wrap:anywhere; }' in html
    assert '.edit-label, .edit-help, .save-label, .save-help, .toggle-required, .datatype-select, .default-value-control, .add-option, .move-draft, .remove-draft { align-self:stretch; width:100%; }' in html

    update_start = html.index('function updateDefaultValue(id, control)')
    update_end = html.index('function defaultValuePreview(item)')
    update_block = html[update_start:update_end]
    assert 'if (!candidate.valid) {' in update_block
    assert update_block.count('focusDefaultValueControl(id);') == 2


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
    assert '.placed-element > span, .datatype-label, .default-value-label, .choice-state { min-width:0; overflow-wrap:anywhere; }' in html
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
    test_required_toggle_is_browser_only_and_mutates_only_required_state()
    test_required_toggle_is_field_only_accessible_and_narrow_safe()
    test_datatype_is_field_only_browser_local_and_mutates_only_datatype()
    test_choice_datatypes_are_browser_local_and_keep_scalar_default_inactive()
    test_choice_datatype_incomplete_state_focus_preview_and_narrow_semantics()
    test_choice_option_add_is_browser_local_monotone_and_append_only()
    test_default_value_is_field_only_browser_local_and_type_validated()
    test_default_value_semantics_focus_and_narrow_layout()
    test_remove_is_browser_only_and_restores_original_target_focus()
    test_narrow_right_edge_field_keeps_remove_button_reachable()
    test_keyboard_contract_uses_native_buttons_focus_and_live_status()
    test_empty_state_hidden_rule_wins_after_placement()
    test_temporary_interaction_has_no_persistence_or_network_write_path()
    test_root_is_get_only_and_unknown_paths_are_not_found()
    test_server_rejects_non_loopback_binding()
    test_browser_shell_has_no_database_or_store_dependency()
    print("MASK BUILDER TEMPORARY CHOICE OPTIONS I113 STEP 1: GRÜN")


if __name__ == "__main__":
    main()
