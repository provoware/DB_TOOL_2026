(() => {
  "use strict";

  const paletteButtons = Array.from(document.querySelectorAll(".palette-item"));
  const targetButtons = Array.from(document.querySelectorAll(".placement-target"));
  const canvas = document.querySelector(".canvas");
  const placedLayer = document.getElementById("placed-elements");
  const emptyState = document.querySelector(".canvas-empty");
  const preview = document.getElementById("preview");
  const previewShell = document.querySelector(".preview-viewport-shell");
  const previewModeLabel = document.getElementById("preview-mode-label");
  const previewModeButtons = Array.from(document.querySelectorAll(".preview-mode-button"));
  const status = document.getElementById("interaction-status");
  const gridAssistantButton = document.getElementById("grid-assistant-button");
  const gridAssistantOutput = document.getElementById("grid-assistant-output");
  const gridColumns = Number(canvas.dataset.gridColumns);
  const draftElements = [];
  const temporaryGridLayout = new Map();
  let nextDraftId = 1;
  let nextDraftOptionId = 1;
  let selectedKind = null;
  let selectedLabel = null;
  let selectedWidth = null;
  let movingDraftId = null;
  let editingDraftId = null;
  let editingHelpDraftId = null;
  let pendingGridSuggestion = null;
  const collapsedSectionIds = new Set();

  function setStatus(message) {
    status.textContent = message;
  }

  function validateTemporaryGridPosition(row, column, width) {
    return (
      Number.isInteger(row)
      && row >= 1
      && placementFitsGrid(column, width)
    );
  }

  function setTemporaryGridPosition(id, row, column, width) {
    if (!validateTemporaryGridPosition(row, column, width)) {
      throw new Error("Temporäre Rasterposition ist ungültig.");
    }
    temporaryGridLayout.set(id, { row, column });
  }

  function temporaryGridPosition(item, fallbackRow) {
    const existing = temporaryGridLayout.get(item.id);
    if (
      existing !== undefined
      && validateTemporaryGridPosition(existing.row, existing.column, item.width)
    ) {
      return existing;
    }
    setTemporaryGridPosition(item.id, fallbackRow, item.column, item.width);
    return temporaryGridLayout.get(item.id);
  }

  function syncTemporaryRowsToDraftOrder() {
    draftElements.forEach((item, index) => {
      const position = temporaryGridPosition(item, index + 1);
      setTemporaryGridPosition(item.id, index + 1, position.column, item.width);
    });
  }

  function gridSuggestionSnapshot(items) {
    return items.map((item, index) => {
      const position = temporaryGridPosition(item, index + 1);
      return {
        id: item.id,
        row: position.row,
        column: position.column,
        width: item.width,
      };
    });
  }

  function computeGridSuggestion(items) {
    let row = 1;
    let column = 0;
    return items.map((item) => {
      if (column + item.width > gridColumns) {
        row += 1;
        column = 0;
      }
      const suggestion = {
        id: item.id,
        label: item.label,
        row,
        column,
        width: item.width,
      };
      column += item.width;
      return suggestion;
    });
  }

  function currentGridLayout(items) {
    return items.map((item, index) => {
      const position = temporaryGridPosition(item, index + 1);
      return {
        id: item.id,
        label: item.label,
        row: position.row,
        column: position.column,
        width: item.width,
      };
    });
  }

  function compareGridLayouts(current, suggestion) {
    const currentById = new Map(current.map((item) => [item.id, item]));
    return suggestion.map((next) => {
      const previous = currentById.get(next.id);
      if (previous === undefined) {
        throw new Error("Rastervergleich enthält unbekannte Draft-ID.");
      }
      const rowChanged = previous.row !== next.row;
      const columnChanged = previous.column !== next.column;
      return {
        id: next.id,
        label: next.label,
        before: previous,
        after: next,
        rowChanged,
        columnChanged,
        changed: rowChanged || columnChanged,
      };
    });
  }

  function applyPendingGridSuggestion() {
    if (pendingGridSuggestion === null) {
      setStatus("Raster-Assistent · kein bestätigter Vorschlag zur Übernahme vorhanden.");
      gridAssistantButton.focus();
      return;
    }

    const currentFingerprint = JSON.stringify(gridSuggestionSnapshot(draftElements));
    if (currentFingerprint !== pendingGridSuggestion.sourceFingerprint) {
      pendingGridSuggestion = null;
      showGridSuggestion();
      setStatus("Raster-Assistent · Vorschlag war veraltet und wurde neu berechnet · nichts übernommen.");
      gridAssistantButton.focus();
      return;
    }

    const draftBefore = JSON.stringify(draftElements);
    const nextLayout = new Map(temporaryGridLayout);
    pendingGridSuggestion.positions.forEach((position) => {
      const item = draftElements.find((candidate) => candidate.id === position.id);
      if (
        item === undefined
        || item.width !== position.width
        || !validateTemporaryGridPosition(position.row, position.column, position.width)
      ) {
        throw new Error("Rastervorschlag kann nicht atomar übernommen werden.");
      }
      nextLayout.set(position.id, { row: position.row, column: position.column });
    });

    if (JSON.stringify(draftElements) !== draftBefore) {
      throw new Error("Rasterübernahme darf Draftdaten nicht verändern.");
    }

    temporaryGridLayout.clear();
    nextLayout.forEach((position, id) => temporaryGridLayout.set(id, position));
    pendingGridSuggestion = null;
    renderDraft();
    showGridSuggestion();
    setStatus("Raster-Assistent · Vorschlag browserlokal übernommen · Draftdaten und Breiten unverändert.");
    gridAssistantButton.focus();
  }

  function showGridSuggestion() {
    const before = JSON.stringify(gridSuggestionSnapshot(draftElements));
    const current = currentGridLayout(draftElements);
    const suggestion = computeGridSuggestion(draftElements);
    const comparison = compareGridLayouts(current, suggestion);
    const after = JSON.stringify(gridSuggestionSnapshot(draftElements));
    if (before !== after) {
      throw new Error("Raster-Assistent darf den Draft nicht verändern.");
    }

    gridAssistantOutput.replaceChildren();
    if (suggestion.length === 0) {
      pendingGridSuggestion = null;
      const empty = document.createElement("p");
      empty.textContent = "Noch keine Komponenten für einen Vorschlag vorhanden.";
      gridAssistantOutput.appendChild(empty);
      setStatus("Raster-Assistent · kein Vorschlag möglich · Draft unverändert.");
      return;
    }

    const changedCount = comparison.filter((item) => item.changed).length;
    pendingGridSuggestion = changedCount === 0
      ? null
      : {
          sourceFingerprint: before,
          positions: suggestion.map((item) => ({
            id: item.id,
            row: item.row,
            column: item.column,
            width: item.width,
          })),
        };
    const summary = document.createElement("p");
    summary.className = "grid-assistant-summary";
    summary.textContent =
      String(changedCount)
      + " von "
      + String(comparison.length)
      + " Position(en) würden sich ändern. Noch nichts übernommen.";
    gridAssistantOutput.appendChild(summary);

    const table = document.createElement("table");
    table.className = "grid-assistant-comparison";
    const caption = document.createElement("caption");
    caption.textContent = "Vorher/Nachher-Vorschau des Rastervorschlags";
    table.appendChild(caption);

    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    ["Element", "Vorher", "Nachher", "Geplante Änderung"].forEach((text) => {
      const cell = document.createElement("th");
      cell.scope = "col";
      cell.textContent = text;
      headRow.appendChild(cell);
    });
    head.appendChild(headRow);
    table.appendChild(head);

    const body = document.createElement("tbody");
    comparison.forEach((item) => {
      const row = document.createElement("tr");
      row.dataset.draftId = item.id;

      const labelCell = document.createElement("th");
      labelCell.scope = "row";
      labelCell.textContent = item.label;
      row.appendChild(labelCell);

      const beforeCell = document.createElement("td");
      beforeCell.textContent =
        "Zeile " + String(item.before.row)
        + " · Spalte " + String(item.before.column + 1)
        + " · Breite " + String(item.before.width);
      row.appendChild(beforeCell);

      const afterCell = document.createElement("td");
      afterCell.textContent =
        "Zeile " + String(item.after.row)
        + " · Spalte " + String(item.after.column + 1)
        + " · Breite " + String(item.after.width);
      row.appendChild(afterCell);

      const changeCell = document.createElement("td");
      const changes = [];
      if (item.rowChanged) {
        changes.push("Zeile " + String(item.before.row) + " → " + String(item.after.row));
      }
      if (item.columnChanged) {
        changes.push("Spalte " + String(item.before.column + 1) + " → " + String(item.after.column + 1));
      }
      changeCell.textContent = changes.length === 0 ? "Keine" : changes.join(" · ");
      row.appendChild(changeCell);
      body.appendChild(row);
    });
    table.appendChild(body);
    gridAssistantOutput.appendChild(table);

    const note = document.createElement("p");
    note.className = "grid-assistant-contract-note";
    note.textContent =
      changedCount === 0
        ? "Aktuelles Layout entspricht bereits dem Rastervorschlag."
        : "Übernahme wirkt ausschließlich auf den flüchtigen Zeile+Spalte-Layoutvertrag. Draftdaten, Breiten und Reihenfolge bleiben unverändert.";
    gridAssistantOutput.appendChild(note);

    if (changedCount > 0) {
      const applyButton = document.createElement("button");
      applyButton.type = "button";
      applyButton.className = "grid-assistant-apply";
      applyButton.textContent = "Rastervorschlag übernehmen";
      applyButton.setAttribute("aria-describedby", "grid-assistant-title");
      applyButton.addEventListener("click", applyPendingGridSuggestion);
      gridAssistantOutput.appendChild(applyButton);
    }

    setStatus(
      "Raster-Assistent · Vorher/Nachher geprüft · "
      + String(changedCount)
      + (changedCount === 0 ? " Änderung(en) offen." : " Änderung(en) bereit zur browserlokalen Übernahme.")
    );
  }

  function setPreviewMode(mode) {
    const previewModes = {
      desktop: { width: "1152", label: "Desktop · 1152 px" },
      tablet: { width: "768", label: "Tablet · 768 px" },
      narrow: { width: "360", label: "Schmal · 360 px" },
    };
    const config = previewModes[mode];
    if (config === undefined) {
      return;
    }
    preview.dataset.previewMode = mode;
    preview.dataset.previewWidth = config.width;
    previewModeLabel.textContent = config.label;
    previewShell.setAttribute(
      "aria-label",
      config.label.replace(" · ", "-Vorschau, ").replace(" px", " Pixel breit")
    );
    previewModeButtons.forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.previewMode === mode));
    });
    setStatus(config.label + " aktiviert · nur temporäre Vorschau.");
  }

  function focusPreviewSectionToggle(id) {
    const button = Array.from(preview.querySelectorAll(".preview-section-toggle"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (button !== undefined) {
      button.focus();
    }
  }

  function togglePreviewSection(id) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "section" || !item.isVisible) {
      return;
    }
    if (collapsedSectionIds.has(id)) {
      collapsedSectionIds.delete(id);
    } else {
      collapsedSectionIds.add(id);
    }
    renderDraft();
    setStatus(
      item.label
      + (collapsedSectionIds.has(id) ? " · Abschnitt eingeklappt" : " · Abschnitt ausgeklappt")
      + " · nur temporärer Browserzustand."
    );
    focusPreviewSectionToggle(id);
  }

  function nextDraftElementId() {
    return "draft-" + String(nextDraftId++);
  }

  function placementFitsGrid(column, width) {
    return (
      Number.isInteger(column)
      && Number.isInteger(width)
      && column >= 0
      && width >= 1
      && column + width <= gridColumns
    );
  }

  function updateTargetAvailability() {
    const moving = movingDraftId === null
      ? null
      : draftElements.find((item) => item.id === movingDraftId);
    const activeWidth = moving === null ? selectedWidth : moving.width;
    targetButtons.forEach((button) => {
      const column = Number(button.dataset.column);
      const invalid = (
        activeWidth !== null
        && !placementFitsGrid(column, activeWidth)
      );
      button.setAttribute("aria-disabled", String(invalid));
      button.title = invalid
        ? "Diese Komponente passt ab hier nicht vollständig ins 12-Spalten-Raster."
        : "";
    });
  }

  function beginMove(id) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined) {
      return;
    }
    movingDraftId = id;
    updateTargetAvailability();
    setStatus(item.label + " verschieben · Zielspalte wählen. Escape bricht ab.");
    setTargetTabStop(item.column);
    targetButtons[item.column].focus();
  }

  function focusMoveControl(id) {
    const button = Array.from(placedLayer.querySelectorAll(".move-draft"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (button !== undefined) {
      button.focus();
    }
  }

  function cancelMove() {
    if (movingDraftId === null) {
      return;
    }
    const id = movingDraftId;
    const item = draftElements.find((candidate) => candidate.id === id);
    movingDraftId = null;
    updateTargetAvailability();
    setStatus(
      (item === undefined ? "Verschieben" : item.label + " verschieben")
      + " abgebrochen · Entwurf unverändert."
    );
    focusMoveControl(id);
  }

  function focusLabelEditor(id) {
    const input = Array.from(placedLayer.querySelectorAll(".label-editor-input"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (input !== undefined) {
      input.focus();
      input.select();
    }
  }

  function focusLabelEditControl(id) {
    const button = Array.from(placedLayer.querySelectorAll(".edit-label"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (button !== undefined) {
      button.focus();
    }
  }

  function beginLabelEdit(id) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined) {
      return;
    }
    editingDraftId = id;
    renderDraft();
    setStatus(item.label + " · neue Beschriftung eingeben und übernehmen.");
    focusLabelEditor(id);
  }

  function cancelLabelEdit(id) {
    if (editingDraftId !== id) {
      return;
    }
    const item = draftElements.find((candidate) => candidate.id === id);
    editingDraftId = null;
    renderDraft();
    setStatus(
      (item === undefined ? "Beschriftung" : item.label)
      + " · Bearbeitung abgebrochen · Entwurf unverändert."
    );
    focusLabelEditControl(id);
  }

  function saveLabelEdit(id, input) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined) {
      return;
    }
    const nextLabel = input.value.trim();
    if (nextLabel.length === 0) {
      setStatus("Nicht übernommen: Beschriftung darf nicht leer sein.");
      input.focus();
      return;
    }
    item.label = nextLabel;
    editingDraftId = null;
    renderDraft();
    setStatus(item.label + " · Beschriftung geändert · nur temporärer Browserentwurf.");
    focusLabelEditControl(id);
  }

  function focusHelpEditor(id) {
    const input = Array.from(placedLayer.querySelectorAll(".help-editor-input"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (input !== undefined) {
      input.focus();
      input.select();
    }
  }

  function focusHelpEditControl(id) {
    const button = Array.from(placedLayer.querySelectorAll(".edit-help"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (button !== undefined) {
      button.focus();
    }
  }

  function beginHelpEdit(id) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined) {
      return;
    }
    editingHelpDraftId = id;
    renderDraft();
    setStatus(item.label + " · Hilfetext eingeben und übernehmen.");
    focusHelpEditor(id);
  }

  function cancelHelpEdit(id) {
    if (editingHelpDraftId !== id) {
      return;
    }
    const item = draftElements.find((candidate) => candidate.id === id);
    editingHelpDraftId = null;
    renderDraft();
    setStatus(
      (item === undefined ? "Hilfetext" : item.label + " · Hilfetext")
      + " Bearbeitung abgebrochen · Entwurf unverändert."
    );
    focusHelpEditControl(id);
  }

  function saveHelpEdit(id, input) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined) {
      return;
    }
    const nextHelpText = input.value.trim();
    item.helpText = nextHelpText;
    editingHelpDraftId = null;
    renderDraft();
    setStatus(
      item.label
      + (nextHelpText.length === 0 ? " · Hilfetext entfernt" : " · Hilfetext geändert")
      + " · nur temporärer Browserentwurf."
    );
    focusHelpEditControl(id);
  }

  function focusRequiredControl(id) {
    const button = Array.from(placedLayer.querySelectorAll(".toggle-required"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (button !== undefined) {
      button.focus();
    }
  }

  function requiredRuleFor(item) {
    return {
      id: "draft-rule-required-" + item.id,
      kind: "required",
      targetFieldId: item.id,
      enabled: item.isRequired,
      parameters: {},
    };
  }

  function evaluateRequiredRule(rule, item, value) {
    const validParameters = (
      rule !== null
      && typeof rule.parameters === "object"
      && rule.parameters !== null
      && Object.keys(rule.parameters).length === 0
    );
    if (
      rule === null
      || rule.kind !== "required"
      || typeof rule.id !== "string"
      || item === undefined
      || item.kind !== "field"
      || rule.targetFieldId !== item.id
      || !validParameters
    ) {
      return { state: "not_evaluable", message: "Vorschau nicht möglich: Pflichtwertregel oder Zielfeld ist ungültig." };
    }
    if (!rule.enabled) {
      return { state: "not_evaluable", message: "Pflichtwert-Preview ist ausgeschaltet." };
    }
    if (typeof value !== "string") {
      return { state: "not_evaluable", message: "Vorschau nicht möglich: Der Testwert ist ungültig." };
    }
    return value.trim().length === 0
      ? { state: "violated", message: "Dieses Feld ist ein Pflichtfeld. Gib einen Wert ein." }
      : { state: "satisfied", message: "Pflichtwert vorhanden." };
  }

  function updateRequiredPreview(id, control, resultNode) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field") {
      resultNode.dataset.ruleState = "not_evaluable";
      resultNode.textContent = "Vorschau nicht möglich: Das Zielfeld ist ungültig.";
      return;
    }
    item.requiredPreviewValue = control.value;
    const result = evaluateRequiredRule(requiredRuleFor(item), item, item.requiredPreviewValue);
    resultNode.dataset.ruleState = result.state;
    resultNode.textContent = result.message;
    setStatus(item.label + " · " + result.message + " · nur temporäre Vorschau.");
  }

  function parseCanonicalNumber(value) {
    if (typeof value !== "string" || !/^-?(0|[1-9][0-9]*)(\.[0-9]+)?$/.test(value)) {
      return null;
    }
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  function numberRangeRuleFor(item) {
    const boundary = parseCanonicalNumber(item.numberRangeBoundaryValue);
    return {
      id: "draft-rule-number-range-" + item.id,
      kind: "number_range",
      targetFieldId: item.id,
      enabled: item.dataType === "number",
      parameters: {
        min: item.numberRangeBoundType === "min" ? boundary : null,
        max: item.numberRangeBoundType === "max" ? boundary : null,
      },
    };
  }

  function evaluateNumberRangeRule(rule, item, value) {
    const parameters = rule === null ? null : rule.parameters;
    const validParameters = (
      parameters !== null
      && typeof parameters === "object"
      && Object.keys(parameters).length === 2
      && Object.hasOwn(parameters, "min")
      && Object.hasOwn(parameters, "max")
      && (parameters.min === null || (typeof parameters.min === "number" && Number.isFinite(parameters.min)))
      && (parameters.max === null || (typeof parameters.max === "number" && Number.isFinite(parameters.max)))
      && ((parameters.min === null) !== (parameters.max === null))
    );
    if (
      rule === null
      || rule.kind !== "number_range"
      || typeof rule.id !== "string"
      || item === undefined
      || item.kind !== "field"
      || item.dataType !== "number"
      || rule.targetFieldId !== item.id
      || !validParameters
    ) {
      return { state: "not_evaluable", reason: "invalid_number_range", message: "Der Zahlenbereich ist ungültig. Prüfe die Grenze." };
    }
    const parsedValue = parseCanonicalNumber(value);
    if (parsedValue === null) {
      return { state: "not_evaluable", reason: "invalid_number_value", message: "Gib eine gültige Zahl ohne Leerzeichen ein." };
    }
    if (parameters.min !== null && parsedValue < parameters.min) {
      return { state: "violated", reason: "number_below_min", message: "Der Testwert muss mindestens " + String(parameters.min) + " sein." };
    }
    if (parameters.max !== null && parsedValue > parameters.max) {
      return { state: "violated", reason: "number_above_max", message: "Der Testwert darf höchstens " + String(parameters.max) + " sein." };
    }
    return { state: "satisfied", reason: "number_in_range", message: "Der Testwert liegt im erlaubten Zahlenbereich." };
  }

  function updateNumberRangePreview(id, boundSelect, boundaryInput, valueInput, resultNode) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field" || item.dataType !== "number") {
      resultNode.dataset.ruleState = "not_evaluable";
      resultNode.textContent = "Vorschau nicht möglich: Das Zahlenfeld ist ungültig.";
      return;
    }
    item.numberRangeBoundType = boundSelect.value;
    item.numberRangeBoundaryValue = boundaryInput.value;
    item.numberRangePreviewValue = valueInput.value;
    const result = evaluateNumberRangeRule(numberRangeRuleFor(item), item, item.numberRangePreviewValue);
    resultNode.dataset.ruleState = result.state;
    resultNode.textContent = result.message;
    setStatus(item.label + " · " + result.message + " · nur temporäre Vorschau.");
  }

  function dateRangeRuleFor(item) {
    return {
      id: "draft-rule-date-range-" + item.id,
      kind: "date_range",
      targetFieldId: item.id,
      enabled: item.dataType === "date",
      parameters: { from: item.dateRangeFrom || null, to: item.dateRangeTo || null },
    };
  }

  function evaluateDateRangeRule(rule, item, value) {
    const parameters = rule === null ? null : rule.parameters;
    const isDate = (candidate) => candidate === null || /^\d{4}-\d{2}-\d{2}$/.test(candidate);
    if (
      rule === null
      || rule.kind !== "date_range"
      || item === undefined
      || item.kind !== "field"
      || item.dataType !== "date"
      || rule.targetFieldId !== item.id
      || parameters === null
      || !isDate(parameters.from)
      || !isDate(parameters.to)
      || (parameters.from === null && parameters.to === null)
      || (parameters.from !== null && parameters.to !== null && parameters.from > parameters.to)
    ) {
      return { state: "not_evaluable", message: "Der Datumsbereich ist ungültig. Prüfe Von- und Bis-Datum." };
    }
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
      return { state: "not_evaluable", message: "Wähle einen gültigen Testtag aus." };
    }
    if (parameters.from !== null && value < parameters.from) {
      return { state: "violated", message: "Der Testtag liegt vor dem erlaubten Zeitraum." };
    }
    if (parameters.to !== null && value > parameters.to) {
      return { state: "violated", message: "Der Testtag liegt nach dem erlaubten Zeitraum." };
    }
    return { state: "satisfied", message: "Der Testtag liegt im erlaubten Zeitraum." };
  }

  function updateDateRangePreview(id, fromInput, toInput, valueInput, resultNode) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field" || item.dataType !== "date") {
      resultNode.dataset.ruleState = "not_evaluable";
      resultNode.textContent = "Vorschau nicht möglich: Das Datumsfeld ist ungültig.";
      return;
    }
    item.dateRangeFrom = fromInput.value;
    item.dateRangeTo = toInput.value;
    item.dateRangePreviewValue = valueInput.value;
    const result = evaluateDateRangeRule(dateRangeRuleFor(item), item, item.dateRangePreviewValue);
    resultNode.dataset.ruleState = result.state;
    resultNode.textContent = result.message;
    setStatus(item.label + " · " + result.message + " · nur temporäre Vorschau.");
  }

  function fileTypeRuleFor(item) {
    const extensions = item.allowedFileTypes
      .split(",")
      .map((value) => value.trim().toLowerCase())
      .filter((value) => /^\.[a-z0-9]+$/.test(value));
    return {
      id: "draft-rule-file-type-" + item.id,
      kind: "allowed_file_types",
      targetFieldId: item.id,
      enabled: item.dataType === "file",
      parameters: { extensions },
    };
  }

  function evaluateFileTypeRule(rule, item, value) {
    const extensions = rule?.parameters?.extensions;
    if (
      rule === null
      || rule.kind !== "allowed_file_types"
      || item === undefined
      || item.kind !== "field"
      || item.dataType !== "file"
      || rule.targetFieldId !== item.id
      || !Array.isArray(extensions)
      || extensions.length === 0
    ) {
      return { state: "not_evaluable", message: "Die Dateityp-Regel ist ungültig. Gib mindestens eine Endung wie .pdf ein." };
    }
    const fileName = typeof value === "string" ? value.trim().toLowerCase() : "";
    if (fileName.length === 0 || !fileName.includes(".")) {
      return { state: "not_evaluable", message: "Gib einen Test-Dateinamen mit Endung ein." };
    }
    if (!extensions.some((extension) => fileName.endsWith(extension))) {
      return { state: "violated", message: "Dieser Dateityp ist nicht erlaubt." };
    }
    return { state: "satisfied", message: "Dieser Dateityp ist erlaubt." };
  }

  function updateFileTypePreview(id, typesInput, valueInput, resultNode) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field" || item.dataType !== "file") {
      resultNode.dataset.ruleState = "not_evaluable";
      resultNode.textContent = "Vorschau nicht möglich: Das Dateifeld ist ungültig.";
      return;
    }
    item.allowedFileTypes = typesInput.value;
    item.fileTypePreviewValue = valueInput.value;
    const result = evaluateFileTypeRule(fileTypeRuleFor(item), item, item.fileTypePreviewValue);
    resultNode.dataset.ruleState = result.state;
    resultNode.textContent = result.message;
    setStatus(item.label + " · " + result.message + " · nur temporäre Vorschau.");
  }

  function appendTooltip(container, id, label, text) {
    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "tooltip-trigger";
    trigger.textContent = "?";
    trigger.setAttribute("aria-label", label);
    trigger.setAttribute("aria-describedby", id);
    const tooltip = document.createElement("span");
    tooltip.className = "tooltip-text";
    tooltip.id = id;
    tooltip.setAttribute("role", "tooltip");
    tooltip.textContent = text;
    container.appendChild(trigger);
    container.appendChild(tooltip);
  }

  function toggleRequired(id) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined) {
      return;
    }
    item.isRequired = !item.isRequired;
    renderDraft();
    setStatus(
      item.label
      + (item.isRequired ? " · als Pflichtfeld markiert" : " · nicht mehr als Pflichtfeld markiert")
      + " · nur temporärer Browserentwurf."
    );
    focusRequiredControl(id);
  }

  function focusVisibilityControl(id) {
    const button = Array.from(placedLayer.querySelectorAll(".toggle-visibility"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (button !== undefined) {
      button.focus();
    }
  }

  function toggleVisibility(id) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined) {
      return;
    }
    item.isVisible = !item.isVisible;
    renderDraft();
    setStatus(
      item.label
      + (item.isVisible ? " · in der Vorschau sichtbar" : " · in der Vorschau ausgeblendet")
      + " · nur temporärer Browserentwurf."
    );
    focusVisibilityControl(id);
  }

  function focusWidthControl(id) {
    const select = Array.from(placedLayer.querySelectorAll(".width-select"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (select !== undefined) {
      select.focus();
    }
  }

  function changeDraftWidth(id, select) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined) {
      return;
    }
    const nextWidth = Number(select.value);
    if (!placementFitsGrid(item.column, nextWidth)) {
      select.value = String(item.width);
      setStatus(
        "Nicht übernommen: "
        + item.label
        + " passt ab Spalte "
        + String(item.column + 1)
        + " nicht mit Breite "
        + String(nextWidth)
        + " ins 12-Spalten-Raster."
      );
      select.focus();
      return;
    }
    item.width = nextWidth;
    renderDraft();
    updateTargetAvailability();
    setStatus(
      item.label
      + " · Breite "
      + String(item.width)
      + " Spalte(n) · nur temporärer Browserentwurf."
    );
    focusWidthControl(id);
  }

  function focusDataTypeControl(id) {
    const select = Array.from(placedLayer.querySelectorAll(".datatype-select"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (select !== undefined) {
      select.focus();
    }
  }

  function changeDataType(id, select) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field") {
      return;
    }
    const nextDataType = select.value;
    const prepared = defaultSelectionForDataType(item, nextDataType);
    if (!prepared.valid) {
      select.value = item.dataType;
      setStatus("Nicht übernommen: " + prepared.message);
      focusDataTypeControl(id);
      return;
    }
    item.dataType = nextDataType;
    if (isChoiceDataType(nextDataType)) {
      item.defaultSelection = prepared.value;
    }
    renderDraft();
    setStatus(
      item.label
      + " · Datentyp "
      + item.dataType
      + (isChoiceDataType(item.dataType)
        ? (item.options.length === 0
          ? " · Auswahltyp unvollständig: noch keine Optionen konfiguriert"
          : " · " + String(item.options.length) + " Auswahloption(en) konfiguriert")
        : "")
      + " · nur temporärer Browserentwurf."
    );
    focusDataTypeControl(id);
  }

  function isChoiceDataType(dataType) {
    return dataType === "single_choice" || dataType === "multi_choice";
  }

  function defaultSelectionIds(item) {
    if (item.defaultSelection === null) {
      return [];
    }
    return Array.isArray(item.defaultSelection)
      ? item.defaultSelection.slice()
      : [item.defaultSelection];
  }

  function defaultSelectionForDataType(item, nextDataType) {
    const ids = defaultSelectionIds(item);
    const known = new Set(item.options.map((option) => option.id));
    if (ids.some((id) => !known.has(id))) {
      return { valid: false, message: "Standardauswahl verweist auf eine nicht vorhandene Option." };
    }
    if (nextDataType === "single_choice") {
      if (ids.length > 1) {
        return {
          valid: false,
          message: "Mehrere Standardoptionen müssen vor dem Wechsel zur Einfachauswahl gelöst werden.",
        };
      }
      return { valid: true, value: ids.length === 0 ? null : ids[0] };
    }
    if (nextDataType === "multi_choice") {
      const selected = new Set(ids);
      return {
        valid: true,
        value: item.options.filter((option) => selected.has(option.id)).map((option) => option.id),
      };
    }
    return { valid: true, value: item.defaultSelection };
  }

  function focusDefaultSelectionControl(id, optionId = null) {
    const controls = Array.from(placedLayer.querySelectorAll(".default-selection-control"));
    const control = controls.find(
      (candidate) =>
        candidate.dataset.draftId === id
        && (optionId === null || candidate.dataset.optionId === optionId)
    );
    if (control !== undefined) {
      control.focus();
    }
  }

  function updateSingleDefaultSelection(id, select) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field" || item.dataType !== "single_choice") {
      return;
    }
    const optionId = select.value.length === 0 ? null : select.value;
    if (optionId !== null && !item.options.some((option) => option.id === optionId)) {
      setStatus("Nicht übernommen: Standardauswahl existiert nicht.");
      focusDefaultSelectionControl(id);
      return;
    }
    item.defaultSelection = optionId;
    renderDraft();
    setStatus(
      item.label
      + (optionId === null ? " · Standardauswahl gelöst" : " · Standardauswahl übernommen")
      + " · nur temporärer Browserentwurf."
    );
    focusDefaultSelectionControl(id);
  }

  function updateMultiDefaultSelection(id, optionId, checked) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field" || item.dataType !== "multi_choice") {
      return;
    }
    if (!item.options.some((option) => option.id === optionId)) {
      setStatus("Nicht übernommen: Standardauswahl existiert nicht.");
      return;
    }
    const selected = new Set(defaultSelectionIds(item));
    if (checked) {
      selected.add(optionId);
    } else {
      selected.delete(optionId);
    }
    item.defaultSelection = item.options
      .filter((option) => selected.has(option.id))
      .map((option) => option.id);
    renderDraft();
    setStatus(item.label + " · Standardauswahl aktualisiert · nur temporärer Browserentwurf.");
    focusDefaultSelectionControl(id, optionId);
  }

  function choiceDefaultSelectionPreview(item) {
    if (item.kind !== "field" || !isChoiceDataType(item.dataType)) {
      return "";
    }
    const selected = new Set(defaultSelectionIds(item));
    const labels = item.options
      .filter((option) => selected.has(option.id))
      .map((option) => option.label);
    return labels.length === 0
      ? "Standardauswahl: keine"
      : "Standardauswahl: " + labels.join(" | ");
  }

  function defaultValueCandidate(dataType, rawValue) {
    if (dataType === "text") {
      return { valid: true, value: rawValue };
    }
    const value = rawValue.trim();
    if (value.length === 0) {
      return { valid: true, value: "" };
    }
    if (dataType === "number") {
      const parsed = Number(value);
      return Number.isFinite(parsed)
        ? { valid: true, value }
        : { valid: false, message: "Standardwert muss eine gültige endliche Zahl sein." };
    }
    if (dataType === "date") {
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(value)) {
        return { valid: false, message: "Standardwert muss ein Datum im Format JJJJ-MM-TT sein." };
      }
      const parsed = new Date(value + "T00:00:00Z");
      const valid = !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
      return valid
        ? { valid: true, value }
        : { valid: false, message: "Standardwert enthält kein gültiges Kalenderdatum." };
    }
    if (dataType === "boolean") {
      return ["", "true", "false"].includes(value)
        ? { valid: true, value }
        : { valid: false, message: "Standardwert für Ja/Nein ist ungültig." };
    }
    return { valid: false, message: "Datentyp für Standardwert ist unbekannt." };
  }

  function focusDefaultValueControl(id) {
    const control = Array.from(placedLayer.querySelectorAll(".default-value-control"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (control !== undefined) {
      control.focus();
    }
  }

  function updateDefaultValue(id, control) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field") {
      return;
    }
    const candidate = defaultValueCandidate(item.dataType, control.value);
    if (!candidate.valid) {
      setStatus("Nicht übernommen: " + candidate.message);
      focusDefaultValueControl(id);
      return;
    }
    item.defaultValue = candidate.value;
    renderDraft();
    setStatus(
      item.label
      + (item.defaultValue.length === 0 ? " · Standardwert geleert" : " · Standardwert übernommen")
      + " · nur temporärer Browserentwurf."
    );
    focusDefaultValueControl(id);
  }

  function defaultValuePreview(item) {
    if (item.kind !== "field" || isChoiceDataType(item.dataType) || item.defaultValue.length === 0) {
      return "";
    }
    if (item.dataType === "boolean") {
      return item.defaultValue === "true" ? "Ja" : "Nein";
    }
    return item.defaultValue;
  }

  function focusOptionInput(id) {
    const input = Array.from(placedLayer.querySelectorAll(".option-editor-input"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (input !== undefined) {
      input.focus();
    }
  }

  function addDraftOption(id, input) {
    const item = draftElements.find((candidate) => candidate.id === id);
    if (item === undefined || item.kind !== "field" || !isChoiceDataType(item.dataType)) {
      return;
    }
    const label = input.value.trim();
    if (label.length === 0) {
      setStatus("Nicht übernommen: Auswahloption darf nicht leer sein.");
      input.focus();
      return;
    }
    const duplicate = item.options.some(
      (option) => option.label.toLowerCase() === label.toLowerCase()
    );
    if (duplicate) {
      setStatus("Nicht übernommen: Diese Auswahloption existiert bereits.");
      input.focus();
      return;
    }
    item.options.push({
      id: "draft-option-" + String(nextDraftOptionId++),
      label,
    });
    renderDraft();
    setStatus(
      item.label
      + " · Auswahloption „"
      + label
      + "“ hinzugefügt · nur temporärer Browserentwurf."
    );
    focusOptionInput(id);
  }

  function focusOptionControl(draftId, optionId, selector) {
    const control = Array.from(placedLayer.querySelectorAll(selector))
      .find(
        (candidate) =>
          candidate.dataset.draftId === draftId
          && candidate.dataset.optionId === optionId
      );
    if (control !== undefined) {
      control.focus();
    }
  }

  function removeDraftOption(draftId, optionId) {
    const item = draftElements.find((candidate) => candidate.id === draftId);
    if (item === undefined || item.kind !== "field" || !isChoiceDataType(item.dataType)) {
      return;
    }
    const index = item.options.findIndex((option) => option.id === optionId);
    if (index < 0) {
      return;
    }
    if (defaultSelectionIds(item).includes(optionId)) {
      setStatus(
        "Nicht entfernt: "
        + item.options[index].label
        + " ist als Standardauswahl aktiv. Zuerst Standardauswahl lösen."
      );
      focusDefaultSelectionControl(draftId, item.dataType === "multi_choice" ? optionId : null);
      return;
    }
    const removed = item.options[index];
    item.options.splice(index, 1);
    const focusOption = item.options[index] ?? item.options[index - 1] ?? null;
    renderDraft();
    setStatus(
      item.label
      + " · Auswahloption „"
      + removed.label
      + "“ entfernt · nur temporärer Browserentwurf."
    );
    if (focusOption === null) {
      focusOptionInput(draftId);
    } else {
      focusOptionControl(draftId, focusOption.id, ".remove-option");
    }
  }

  function moveDraftOption(draftId, optionId, direction) {
    const item = draftElements.find((candidate) => candidate.id === draftId);
    if (
      item === undefined
      || item.kind !== "field"
      || !isChoiceDataType(item.dataType)
      || ![-1, 1].includes(direction)
    ) {
      return;
    }
    const index = item.options.findIndex((option) => option.id === optionId);
    const targetIndex = index + direction;
    if (index < 0 || targetIndex < 0 || targetIndex >= item.options.length) {
      return;
    }
    const [option] = item.options.splice(index, 1);
    item.options.splice(targetIndex, 0, option);
    renderDraft();
    setStatus(
      item.label
      + " · Auswahloption „"
      + option.label
      + (direction < 0 ? "“ nach oben verschoben" : "“ nach unten verschoben")
      + " · nur temporärer Browserentwurf."
    );
    let focusSelector = direction < 0 ? ".move-option-up" : ".move-option-down";
    if (targetIndex === 0) {
      focusSelector = ".move-option-down";
    }
    if (targetIndex === item.options.length - 1) {
      focusSelector = ".move-option-up";
    }
    focusOptionControl(draftId, option.id, focusSelector);
  }

  function focusDraftOrderControl(id, direction) {
    const selector = direction < 0 ? ".move-draft-up" : ".move-draft-down";
    const button = Array.from(placedLayer.querySelectorAll(selector))
      .find((candidate) => candidate.dataset.draftId === id);
    if (button !== undefined && !button.disabled) {
      button.focus();
      return;
    }
    const fallbackSelector = direction < 0 ? ".move-draft-down" : ".move-draft-up";
    const fallback = Array.from(placedLayer.querySelectorAll(fallbackSelector))
      .find((candidate) => candidate.dataset.draftId === id);
    if (fallback !== undefined && !fallback.disabled) {
      fallback.focus();
    }
  }

  function moveDraftOrder(id, direction) {
    if (![-1, 1].includes(direction)) {
      return;
    }
    const index = draftElements.findIndex((item) => item.id === id);
    const targetIndex = index + direction;
    if (index < 0 || targetIndex < 0 || targetIndex >= draftElements.length) {
      return;
    }
    const [item] = draftElements.splice(index, 1);
    draftElements.splice(targetIndex, 0, item);
    syncTemporaryRowsToDraftOrder();
    renderDraft();
    setStatus(
      item.label
      + (direction < 0 ? " · in der Reihenfolge nach oben verschoben" : " · in der Reihenfolge nach unten verschoben")
      + " · nur temporärer Browserentwurf."
    );
    focusDraftOrderControl(id, direction);
  }

  function focusDuplicateControl(id) {
    const button = Array.from(placedLayer.querySelectorAll(".duplicate-draft"))
      .find((candidate) => candidate.dataset.draftId === id);
    if (button !== undefined) {
      button.focus();
    }
  }

  function duplicateDraft(id) {
    const source = draftElements.find((item) => item.id === id);
    if (source === undefined) {
      return;
    }

    const optionIdMap = new Map();
    const options = source.options === null
      ? null
      : source.options.map((option) => {
          const nextId = "draft-option-" + String(nextDraftOptionId++);
          optionIdMap.set(option.id, nextId);
          return { id: nextId, label: option.label };
        });

    let defaultSelection = source.defaultSelection;
    if (Array.isArray(source.defaultSelection)) {
      defaultSelection = source.defaultSelection
        .map((optionId) => optionIdMap.get(optionId))
        .filter((optionId) => optionId !== undefined);
    } else if (typeof source.defaultSelection === "string") {
      defaultSelection = optionIdMap.get(source.defaultSelection) ?? null;
    }

    const duplicate = {
      id: nextDraftElementId(),
      kind: source.kind,
      label: source.label,
      column: source.column,
      width: source.width,
      helpText: source.helpText,
      isRequired: source.isRequired,
      isVisible: source.isVisible,
      dataType: source.dataType,
      defaultValue: source.defaultValue,
      options,
      defaultSelection,
      requiredPreviewValue: source.requiredPreviewValue,
      numberRangeBoundType: source.numberRangeBoundType,
      numberRangeBoundaryValue: source.numberRangeBoundaryValue,
      numberRangePreviewValue: source.numberRangePreviewValue,
      dateRangeFrom: source.dateRangeFrom,
      dateRangeTo: source.dateRangeTo,
      dateRangePreviewValue: source.dateRangePreviewValue,
      allowedFileTypes: source.allowedFileTypes,
      fileTypePreviewValue: source.fileTypePreviewValue,
    };
    draftElements.push(duplicate);
    setTemporaryGridPosition(duplicate.id, draftElements.length, duplicate.column, duplicate.width);
    renderDraft();
    updateTargetAvailability();
    setStatus(
      source.label
      + " dupliziert als "
      + duplicate.id
      + " · nur temporärer Browserentwurf."
    );
    focusDuplicateControl(duplicate.id);
  }

  function removeDraft(id) {
    const index = draftElements.findIndex((item) => item.id === id);
    if (index < 0) {
      return;
    }
    const removed = draftElements[index];
    draftElements.splice(index, 1);
    collapsedSectionIds.delete(id);
    temporaryGridLayout.delete(id);
    syncTemporaryRowsToDraftOrder();
    renderDraft();
    setStatus(removed.label + " entfernt · nur temporärer Browserentwurf.");
    setTargetTabStop(removed.column);
    targetButtons[removed.column].focus();
  }

  function renderDraft() {
    placedLayer.replaceChildren();
    draftElements.forEach((item, index) => {
      const position = temporaryGridPosition(item, index + 1);
      const card = document.createElement("div");
      card.className = "placed-element";
      card.dataset.kind = item.kind;
      card.dataset.draftId = item.id;
      card.dataset.gridRow = String(position.row);
      card.dataset.gridColumn = String(position.column);
      card.setAttribute("role", "group");
      card.setAttribute("aria-label", item.label);
      card.style.gridColumn = String(position.column + 1) + " / span " + String(item.width);
      card.style.gridRow = String(position.row);

      const label = document.createElement("span");
      label.textContent = item.label;
      card.appendChild(label);

      const helpText = document.createElement("small");
      helpText.className = "draft-help-text";
      helpText.id = "draft-help-" + item.id;
      helpText.textContent = item.helpText;
      helpText.hidden = item.helpText.length === 0;
      if (item.helpText.length > 0) {
        card.setAttribute("aria-describedby", helpText.id);
      }
      card.appendChild(helpText);

      const editButton = document.createElement("button");
      editButton.type = "button";
      editButton.className = "edit-label";
      editButton.dataset.draftId = item.id;
      editButton.textContent = "Beschriftung ändern";
      editButton.setAttribute("aria-label", item.label + " · Beschriftung ändern");
      editButton.addEventListener("click", () => beginLabelEdit(item.id));
      card.appendChild(editButton);

      const helpButton = document.createElement("button");
      helpButton.type = "button";
      helpButton.className = "edit-help";
      helpButton.dataset.draftId = item.id;
      helpButton.textContent = "Hilfetext ändern";
      helpButton.setAttribute("aria-label", item.label + " · Hilfetext ändern");
      helpButton.addEventListener("click", () => beginHelpEdit(item.id));
      card.appendChild(helpButton);

      if (editingHelpDraftId === item.id) {
        const helpEditor = document.createElement("form");
        helpEditor.className = "help-editor";

        const helpInput = document.createElement("textarea");
        helpInput.className = "help-editor-input";
        helpInput.dataset.draftId = item.id;
        helpInput.rows = 2;
        helpInput.value = item.helpText;
        helpInput.setAttribute("aria-label", item.label + " · Hilfetext");
        helpInput.addEventListener("keydown", (event) => {
          if (event.key === "Escape") {
            event.preventDefault();
            cancelHelpEdit(item.id);
          }
        });
        helpEditor.appendChild(helpInput);

        const saveHelpButton = document.createElement("button");
        saveHelpButton.type = "submit";
        saveHelpButton.className = "save-help";
        saveHelpButton.textContent = "Übernehmen";
        helpEditor.appendChild(saveHelpButton);
        helpEditor.addEventListener("submit", (event) => {
          event.preventDefault();
          saveHelpEdit(item.id, helpInput);
        });
        card.appendChild(helpEditor);
      }

      if (editingDraftId === item.id) {
        const editor = document.createElement("form");
        editor.className = "label-editor";

        const input = document.createElement("input");
        input.type = "text";
        input.className = "label-editor-input";
        input.dataset.draftId = item.id;
        input.value = item.label;
        input.setAttribute("aria-label", item.label + " · neue Beschriftung");
        input.addEventListener("keydown", (event) => {
          if (event.key === "Escape") {
            event.preventDefault();
            cancelLabelEdit(item.id);
          }
        });
        editor.appendChild(input);

        const saveButton = document.createElement("button");
        saveButton.type = "submit";
        saveButton.className = "save-label";
        saveButton.textContent = "Übernehmen";
        editor.appendChild(saveButton);
        editor.addEventListener("submit", (event) => {
          event.preventDefault();
          saveLabelEdit(item.id, input);
        });
        card.appendChild(editor);
      }

      if (item.kind === "field") {
        const requiredState = document.createElement("span");
        requiredState.className = "required-state";
        requiredState.id = "draft-required-" + item.id;
        requiredState.textContent = item.isRequired ? "Pflichtfeld" : "Optional";
        card.appendChild(requiredState);

        const requiredButton = document.createElement("button");
        requiredButton.type = "button";
        requiredButton.className = "toggle-required";
        requiredButton.dataset.draftId = item.id;
        requiredButton.textContent = item.isRequired ? "Pflichtfeld: Ja" : "Pflichtfeld: Nein";
        requiredButton.setAttribute("aria-pressed", String(item.isRequired));
        requiredButton.setAttribute("aria-describedby", requiredState.id);
        requiredButton.setAttribute("aria-label", item.label + " · Pflichtfeld umschalten");
        requiredButton.addEventListener("click", () => toggleRequired(item.id));
        card.appendChild(requiredButton);
        appendTooltip(
          card,
          "required-toggle-help-" + item.id,
          item.label + " · Hilfe zur Pflichtwertregel",
          "Schaltet nur die temporäre Pflichtwert-Preview ein oder aus. Es wird keine Regel gespeichert."
        );

        if (item.isRequired) {
          const requiredPreviewLabel = document.createElement("label");
          requiredPreviewLabel.className = "required-preview-label";
          requiredPreviewLabel.id = "required-preview-label-" + item.id;
          requiredPreviewLabel.textContent = "Testwert für Pflichtfeld-Preview";

          const requiredPreviewInput = document.createElement("input");
          requiredPreviewInput.type = "text";
          requiredPreviewInput.className = "required-preview-input";
          requiredPreviewInput.id = "required-preview-input-" + item.id;
          requiredPreviewInput.dataset.draftId = item.id;
          requiredPreviewInput.value = item.requiredPreviewValue;
          requiredPreviewLabel.htmlFor = requiredPreviewInput.id;

          const requiredPreviewResult = document.createElement("span");
          const initialResult = evaluateRequiredRule(
            requiredRuleFor(item), item, item.requiredPreviewValue
          );
          requiredPreviewResult.className = "required-preview-result";
          requiredPreviewResult.id = "required-preview-result-" + item.id;
          requiredPreviewResult.dataset.ruleState = initialResult.state;
          requiredPreviewResult.setAttribute("role", "status");
          requiredPreviewResult.setAttribute("aria-live", "polite");
          requiredPreviewResult.textContent = initialResult.message;
          requiredPreviewInput.setAttribute(
            "aria-describedby",
            requiredPreviewResult.id + " required-preview-help-" + item.id
          );
          requiredPreviewInput.addEventListener(
            "input",
            () => updateRequiredPreview(item.id, requiredPreviewInput, requiredPreviewResult)
          );
          card.appendChild(requiredPreviewLabel);
          card.appendChild(requiredPreviewInput);
          appendTooltip(
            card,
            "required-preview-help-" + item.id,
            item.label + " · Hilfe zum Testwert",
            "Leer und nur Leerzeichen verletzen die Pflichtwertregel. Der Testwert bleibt ausschließlich im Browser."
          );
          card.appendChild(requiredPreviewResult);
        }

        const dataTypeLabel = document.createElement("label");
        dataTypeLabel.className = "datatype-label";
        dataTypeLabel.id = "draft-datatype-label-" + item.id;
        dataTypeLabel.textContent = "Datentyp";

        const dataTypeSelect = document.createElement("select");
        dataTypeSelect.className = "datatype-select";
        dataTypeSelect.dataset.draftId = item.id;
        dataTypeSelect.setAttribute("aria-labelledby", dataTypeLabel.id);
        [
          ["text", "Text"],
          ["number", "Zahl"],
          ["date", "Datum"],
          ["file", "Datei"],
          ["boolean", "Ja/Nein"],
          ["single_choice", "Einfachauswahl"],
          ["multi_choice", "Mehrfachauswahl"],
        ].forEach(([value, labelText]) => {
          const option = document.createElement("option");
          option.value = value;
          option.textContent = labelText;
          option.selected = item.dataType === value;
          dataTypeSelect.appendChild(option);
        });
        dataTypeLabel.htmlFor = "draft-datatype-" + item.id;
        dataTypeSelect.id = "draft-datatype-" + item.id;
        dataTypeSelect.addEventListener("change", () => changeDataType(item.id, dataTypeSelect));
        card.appendChild(dataTypeLabel);
        card.appendChild(dataTypeSelect);

        if (item.dataType === "number") {
          const rangeGroup = document.createElement("fieldset");
          rangeGroup.className = "number-range-preview";
          const rangeLegend = document.createElement("legend");
          rangeLegend.textContent = "Zahlenbereich testen";
          rangeGroup.appendChild(rangeLegend);

          const boundLabel = document.createElement("label");
          boundLabel.textContent = "Grenzart";
          const boundSelect = document.createElement("select");
          boundSelect.className = "number-range-bound";
          boundSelect.id = "number-range-bound-" + item.id;
          [["min", "Mindestens"], ["max", "Höchstens"]].forEach(([value, text]) => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = text;
            option.selected = item.numberRangeBoundType === value;
            boundSelect.appendChild(option);
          });
          boundLabel.htmlFor = boundSelect.id;

          const boundaryLabel = document.createElement("label");
          boundaryLabel.textContent = "Grenzwert";
          const boundaryInput = document.createElement("input");
          boundaryInput.type = "text";
          boundaryInput.inputMode = "decimal";
          boundaryInput.className = "number-range-boundary";
          boundaryInput.id = "number-range-boundary-" + item.id;
          boundaryInput.value = item.numberRangeBoundaryValue;
          boundaryLabel.htmlFor = boundaryInput.id;

          const valueLabel = document.createElement("label");
          valueLabel.textContent = "Testwert";
          const valueInput = document.createElement("input");
          valueInput.type = "text";
          valueInput.inputMode = "decimal";
          valueInput.className = "number-range-value";
          valueInput.id = "number-range-value-" + item.id;
          valueInput.value = item.numberRangePreviewValue;
          valueLabel.htmlFor = valueInput.id;

          const rangeResult = document.createElement("span");
          const initialRangeResult = evaluateNumberRangeRule(
            numberRangeRuleFor(item), item, item.numberRangePreviewValue
          );
          rangeResult.className = "number-range-result";
          rangeResult.id = "number-range-result-" + item.id;
          rangeResult.dataset.ruleState = initialRangeResult.state;
          rangeResult.setAttribute("role", "status");
          rangeResult.setAttribute("aria-live", "polite");
          rangeResult.textContent = initialRangeResult.message;
          const updateRange = () => updateNumberRangePreview(
            item.id, boundSelect, boundaryInput, valueInput, rangeResult
          );
          boundSelect.addEventListener("change", updateRange);
          boundaryInput.addEventListener("input", updateRange);
          valueInput.addEventListener("input", updateRange);
          const helpId = "number-range-help-" + item.id;
          boundaryInput.setAttribute("aria-describedby", helpId + " " + rangeResult.id);
          valueInput.setAttribute("aria-describedby", helpId + " " + rangeResult.id);

          rangeGroup.appendChild(boundLabel);
          rangeGroup.appendChild(boundSelect);
          rangeGroup.appendChild(boundaryLabel);
          rangeGroup.appendChild(boundaryInput);
          rangeGroup.appendChild(valueLabel);
          rangeGroup.appendChild(valueInput);
          appendTooltip(
            rangeGroup,
            helpId,
            item.label + " · Hilfe zur Zahlenbereichsregel",
            "Prüft genau eine Unter- oder Obergrenze. Regel und Testwert bleiben ausschließlich im Browser."
          );
          rangeGroup.appendChild(rangeResult);
          card.appendChild(rangeGroup);
        }

        if (item.dataType === "date") {
          const dateGroup = document.createElement("fieldset");
          dateGroup.className = "date-range-preview";
          const legend = document.createElement("legend");
          legend.textContent = "Datumsbereich testen";
          dateGroup.appendChild(legend);
          const controls = [
            ["Von", "date-range-from", item.dateRangeFrom],
            ["Bis", "date-range-to", item.dateRangeTo],
            ["Testtag", "date-range-value", item.dateRangePreviewValue],
          ].map(([text, className, currentValue]) => {
            const label = document.createElement("label");
            label.textContent = text;
            const input = document.createElement("input");
            input.type = "date";
            input.className = className;
            input.id = className + "-" + item.id;
            input.value = currentValue;
            label.htmlFor = input.id;
            dateGroup.appendChild(label);
            dateGroup.appendChild(input);
            return input;
          });
          const resultNode = document.createElement("span");
          const initial = evaluateDateRangeRule(dateRangeRuleFor(item), item, item.dateRangePreviewValue);
          resultNode.className = "date-range-result";
          resultNode.id = "date-range-result-" + item.id;
          resultNode.dataset.ruleState = initial.state;
          resultNode.setAttribute("role", "status");
          resultNode.setAttribute("aria-live", "polite");
          resultNode.textContent = initial.message;
          const helpId = "date-range-help-" + item.id;
          controls.forEach((control) => {
            control.setAttribute("aria-describedby", helpId + " " + resultNode.id);
            control.addEventListener("input", () => updateDateRangePreview(
              item.id, controls[0], controls[1], controls[2], resultNode
            ));
          });
          appendTooltip(dateGroup, helpId, item.label + " · Hilfe zum Datumsbereich", "Von, Bis und Testtag bleiben ausschließlich im Browser.");
          dateGroup.appendChild(resultNode);
          card.appendChild(dateGroup);
        }

        if (item.dataType === "file") {
          const fileGroup = document.createElement("fieldset");
          fileGroup.className = "file-type-preview";
          const legend = document.createElement("legend");
          legend.textContent = "Erlaubte Dateitypen testen";
          fileGroup.appendChild(legend);
          const typesLabel = document.createElement("label");
          typesLabel.textContent = "Erlaubte Endungen";
          const typesInput = document.createElement("input");
          typesInput.type = "text";
          typesInput.className = "file-type-extensions";
          typesInput.id = "file-type-extensions-" + item.id;
          typesInput.value = item.allowedFileTypes;
          typesLabel.htmlFor = typesInput.id;
          const valueLabel = document.createElement("label");
          valueLabel.textContent = "Test-Dateiname";
          const valueInput = document.createElement("input");
          valueInput.type = "text";
          valueInput.className = "file-type-value";
          valueInput.id = "file-type-value-" + item.id;
          valueInput.value = item.fileTypePreviewValue;
          valueLabel.htmlFor = valueInput.id;
          const resultNode = document.createElement("span");
          const initial = evaluateFileTypeRule(fileTypeRuleFor(item), item, item.fileTypePreviewValue);
          resultNode.className = "file-type-result";
          resultNode.id = "file-type-result-" + item.id;
          resultNode.dataset.ruleState = initial.state;
          resultNode.setAttribute("role", "status");
          resultNode.setAttribute("aria-live", "polite");
          resultNode.textContent = initial.message;
          const helpId = "file-type-help-" + item.id;
          [typesInput, valueInput].forEach((control) => {
            control.setAttribute("aria-describedby", helpId + " " + resultNode.id);
            control.addEventListener("input", () => updateFileTypePreview(item.id, typesInput, valueInput, resultNode));
          });
          fileGroup.appendChild(typesLabel);
          fileGroup.appendChild(typesInput);
          fileGroup.appendChild(valueLabel);
          fileGroup.appendChild(valueInput);
          appendTooltip(fileGroup, helpId, item.label + " · Hilfe zu Dateitypen", "Kommagetrennte Endungen wie .pdf, .jpg prüfen nur den Test-Dateinamen. Keine Datei wird gelesen oder gespeichert.");
          fileGroup.appendChild(resultNode);
          card.appendChild(fileGroup);
        }

        if (isChoiceDataType(item.dataType)) {
          const choiceState = document.createElement("span");
          choiceState.className = "choice-state";
          choiceState.id = "draft-choice-state-" + item.id;
          choiceState.textContent = item.options.length === 0
            ? "Auswahltyp unvollständig · noch keine Optionen konfiguriert."
            : String(item.options.length) + " Auswahloption(en) konfiguriert.";
          dataTypeSelect.setAttribute("aria-describedby", choiceState.id);
          card.appendChild(choiceState);

          const optionEditor = document.createElement("form");
          optionEditor.className = "option-editor";

          const optionLabel = document.createElement("label");
          optionLabel.className = "option-editor-label";
          optionLabel.id = "draft-option-label-" + item.id;
          optionLabel.textContent = "Option hinzufügen";
          optionEditor.appendChild(optionLabel);

          const optionInput = document.createElement("input");
          optionInput.type = "text";
          optionInput.className = "option-editor-input";
          optionInput.dataset.draftId = item.id;
          optionInput.id = "draft-option-input-" + item.id;
          optionInput.setAttribute("aria-labelledby", optionLabel.id);
          optionLabel.htmlFor = optionInput.id;
          optionEditor.appendChild(optionInput);

          const addOptionButton = document.createElement("button");
          addOptionButton.type = "submit";
          addOptionButton.className = "add-option";
          addOptionButton.textContent = "Hinzufügen";
          optionEditor.appendChild(addOptionButton);
          optionEditor.addEventListener("submit", (event) => {
            event.preventDefault();
            addDraftOption(item.id, optionInput);
          });
          card.appendChild(optionEditor);

          if (item.options.length > 0) {
            const optionList = document.createElement("ol");
            optionList.className = "choice-options-list";
            item.options.forEach((option, optionIndex) => {
              const optionRow = document.createElement("li");
              optionRow.className = "choice-option-row";
              optionRow.dataset.optionId = option.id;

              const optionText = document.createElement("span");
              optionText.className = "choice-option-label";
              optionText.textContent = option.label;
              optionRow.appendChild(optionText);

              const moveUpButton = document.createElement("button");
              moveUpButton.type = "button";
              moveUpButton.className = "move-option-up";
              moveUpButton.dataset.draftId = item.id;
              moveUpButton.dataset.optionId = option.id;
              moveUpButton.textContent = "Hoch";
              moveUpButton.disabled = optionIndex === 0;
              moveUpButton.setAttribute("aria-label", item.label + " · " + option.label + " nach oben");
              moveUpButton.addEventListener("click", () => moveDraftOption(item.id, option.id, -1));
              optionRow.appendChild(moveUpButton);

              const moveDownButton = document.createElement("button");
              moveDownButton.type = "button";
              moveDownButton.className = "move-option-down";
              moveDownButton.dataset.draftId = item.id;
              moveDownButton.dataset.optionId = option.id;
              moveDownButton.textContent = "Runter";
              moveDownButton.disabled = optionIndex === item.options.length - 1;
              moveDownButton.setAttribute("aria-label", item.label + " · " + option.label + " nach unten");
              moveDownButton.addEventListener("click", () => moveDraftOption(item.id, option.id, 1));
              optionRow.appendChild(moveDownButton);

              const removeOptionButton = document.createElement("button");
              removeOptionButton.type = "button";
              removeOptionButton.className = "remove-option";
              removeOptionButton.dataset.draftId = item.id;
              removeOptionButton.dataset.optionId = option.id;
              removeOptionButton.textContent = "Option entfernen";
              removeOptionButton.setAttribute("aria-label", item.label + " · " + option.label + " entfernen");
              removeOptionButton.addEventListener("click", () => removeDraftOption(item.id, option.id));
              optionRow.appendChild(removeOptionButton);

              optionList.appendChild(optionRow);
            });
            card.appendChild(optionList);
          }

          const defaultSelectionLabel = document.createElement("label");
          defaultSelectionLabel.className = "default-selection-label";
          defaultSelectionLabel.textContent = "Standardauswahl";
          card.appendChild(defaultSelectionLabel);

          if (item.dataType === "single_choice") {
            const defaultSelectionControl = document.createElement("select");
            defaultSelectionControl.className = "default-selection-control";
            defaultSelectionControl.dataset.draftId = item.id;
            defaultSelectionControl.id = "draft-default-selection-" + item.id;
            defaultSelectionLabel.id = "draft-default-selection-label-" + item.id;
            defaultSelectionLabel.htmlFor = defaultSelectionControl.id;
            defaultSelectionControl.setAttribute("aria-labelledby", defaultSelectionLabel.id);
            const noneOption = document.createElement("option");
            noneOption.value = "";
            noneOption.textContent = "Keine";
            noneOption.selected = item.defaultSelection === null;
            defaultSelectionControl.appendChild(noneOption);
            item.options.forEach((option) => {
              const defaultOption = document.createElement("option");
              defaultOption.value = option.id;
              defaultOption.textContent = option.label;
              defaultOption.selected = item.defaultSelection === option.id;
              defaultSelectionControl.appendChild(defaultOption);
            });
            defaultSelectionControl.disabled = item.options.length === 0;
            defaultSelectionControl.addEventListener(
              "change",
              () => updateSingleDefaultSelection(item.id, defaultSelectionControl)
            );
            card.appendChild(defaultSelectionControl);
          } else {
            const defaultSelectionGroup = document.createElement("fieldset");
            defaultSelectionGroup.className = "default-selection-group";
            defaultSelectionGroup.setAttribute("aria-label", item.label + " · Standardauswahl");
            const selected = new Set(defaultSelectionIds(item));
            item.options.forEach((option) => {
              const defaultSelectionRow = document.createElement("label");
              defaultSelectionRow.className = "default-selection-row";
              const checkbox = document.createElement("input");
              checkbox.type = "checkbox";
              checkbox.className = "default-selection-control";
              checkbox.dataset.draftId = item.id;
              checkbox.dataset.optionId = option.id;
              checkbox.checked = selected.has(option.id);
              checkbox.setAttribute("aria-label", item.label + " · " + option.label + " als Standardauswahl");
              checkbox.addEventListener(
                "change",
                () => updateMultiDefaultSelection(item.id, option.id, checkbox.checked)
              );
              defaultSelectionRow.appendChild(checkbox);
              const checkboxText = document.createElement("span");
              checkboxText.textContent = option.label;
              defaultSelectionRow.appendChild(checkboxText);
              defaultSelectionGroup.appendChild(defaultSelectionRow);
            });
            card.appendChild(defaultSelectionGroup);
          }
        }

        if (!isChoiceDataType(item.dataType)) {
          const defaultValueLabel = document.createElement("label");
          defaultValueLabel.className = "default-value-label";
          defaultValueLabel.id = "draft-default-value-label-" + item.id;
          defaultValueLabel.textContent = "Standardwert";
          card.appendChild(defaultValueLabel);

          let defaultValueControl;
          if (item.dataType === "boolean") {
            defaultValueControl = document.createElement("select");
            [
              ["", "Leer"],
              ["true", "Ja"],
              ["false", "Nein"],
            ].forEach(([value, labelText]) => {
              const option = document.createElement("option");
              option.value = value;
              option.textContent = labelText;
              option.selected = item.defaultValue === value;
              defaultValueControl.appendChild(option);
            });
          } else {
            defaultValueControl = document.createElement("input");
            defaultValueControl.type = "text";
            defaultValueControl.value = item.defaultValue;
            if (item.dataType === "number") {
              defaultValueControl.inputMode = "decimal";
            } else if (item.dataType === "date") {
              defaultValueControl.placeholder = "JJJJ-MM-TT";
            }
          }
          defaultValueControl.className = "default-value-control";
          defaultValueControl.dataset.draftId = item.id;
          defaultValueControl.id = "draft-default-value-" + item.id;
          defaultValueLabel.htmlFor = defaultValueControl.id;
          defaultValueControl.setAttribute("aria-labelledby", defaultValueLabel.id);
          defaultValueControl.addEventListener("change", () => updateDefaultValue(item.id, defaultValueControl));
          card.appendChild(defaultValueControl);
        }
      }

      const widthLabel = document.createElement("label");
      widthLabel.className = "width-label";
      widthLabel.id = "draft-width-label-" + item.id;
      widthLabel.textContent = "Breite (Spalten)";

      const widthSelect = document.createElement("select");
      widthSelect.className = "width-select";
      widthSelect.dataset.draftId = item.id;
      widthSelect.id = "draft-width-" + item.id;
      widthSelect.setAttribute("aria-labelledby", widthLabel.id);
      widthLabel.htmlFor = widthSelect.id;
      for (let width = 1; width <= gridColumns; width += 1) {
        const option = document.createElement("option");
        option.value = String(width);
        option.textContent = String(width);
        option.selected = item.width === width;
        option.disabled = !placementFitsGrid(item.column, width);
        widthSelect.appendChild(option);
      }
      widthSelect.addEventListener("change", () => changeDraftWidth(item.id, widthSelect));
      card.appendChild(widthLabel);
      card.appendChild(widthSelect);

      const visibilityState = document.createElement("span");
      visibilityState.className = "visibility-state";
      visibilityState.id = "draft-visibility-" + item.id;
      visibilityState.textContent = item.isVisible ? "Sichtbar" : "Ausgeblendet";
      card.appendChild(visibilityState);

      const visibilityButton = document.createElement("button");
      visibilityButton.type = "button";
      visibilityButton.className = "toggle-visibility";
      visibilityButton.dataset.draftId = item.id;
      visibilityButton.textContent = item.isVisible ? "Sichtbar: Ja" : "Sichtbar: Nein";
      visibilityButton.setAttribute("aria-pressed", String(item.isVisible));
      visibilityButton.setAttribute("aria-describedby", visibilityState.id);
      visibilityButton.setAttribute("aria-label", item.label + " · Sichtbarkeit umschalten");
      visibilityButton.addEventListener("click", () => toggleVisibility(item.id));
      card.appendChild(visibilityButton);

      const moveUpButton = document.createElement("button");
      moveUpButton.type = "button";
      moveUpButton.className = "move-draft-up";
      moveUpButton.dataset.draftId = item.id;
      moveUpButton.textContent = "Reihenfolge hoch";
      moveUpButton.disabled = index === 0;
      moveUpButton.setAttribute("aria-label", item.label + " · in der Reihenfolge nach oben");
      moveUpButton.addEventListener("click", () => moveDraftOrder(item.id, -1));
      card.appendChild(moveUpButton);

      const moveDownButton = document.createElement("button");
      moveDownButton.type = "button";
      moveDownButton.className = "move-draft-down";
      moveDownButton.dataset.draftId = item.id;
      moveDownButton.textContent = "Reihenfolge runter";
      moveDownButton.disabled = index === draftElements.length - 1;
      moveDownButton.setAttribute("aria-label", item.label + " · in der Reihenfolge nach unten");
      moveDownButton.addEventListener("click", () => moveDraftOrder(item.id, 1));
      card.appendChild(moveDownButton);

      const duplicateButton = document.createElement("button");
      duplicateButton.type = "button";
      duplicateButton.className = "duplicate-draft";
      duplicateButton.dataset.draftId = item.id;
      duplicateButton.textContent = "Duplizieren";
      duplicateButton.setAttribute("aria-label", item.label + " duplizieren");
      duplicateButton.addEventListener("click", () => duplicateDraft(item.id));
      card.appendChild(duplicateButton);

      const moveButton = document.createElement("button");
      moveButton.type = "button";
      moveButton.className = "move-draft";
      moveButton.dataset.draftId = item.id;
      moveButton.textContent = "Verschieben";
      moveButton.setAttribute("aria-label", item.label + " verschieben");
      moveButton.addEventListener("click", () => beginMove(item.id));
      card.appendChild(moveButton);

      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.className = "remove-draft";
      removeButton.textContent = "Entfernen";
      removeButton.setAttribute("aria-label", item.label + " entfernen");
      removeButton.addEventListener("click", () => removeDraft(item.id));
      card.appendChild(removeButton);
      placedLayer.appendChild(card);
    });

    emptyState.hidden = draftElements.length > 0;
    preview.replaceChildren();

    if (draftElements.length === 0) {
      const text = document.createElement("p");
      text.textContent = "Noch keine Komponenten platziert.";
      preview.appendChild(text);
      return;
    }

    const visibleDraftElements = draftElements.filter((item) => item.isVisible);
    if (visibleDraftElements.length === 0) {
      const text = document.createElement("p");
      text.textContent = "Alle platzierten Komponenten sind aktuell ausgeblendet.";
      preview.appendChild(text);
      return;
    }

    function appendPreviewRow(list, item) {
      const row = document.createElement("li");
      const itemIndex = draftElements.findIndex((candidate) => candidate.id === item.id);
      const position = temporaryGridPosition(item, itemIndex + 1);
      const firstColumn = position.column + 1;
      const lastColumn = position.column + item.width;
      row.dataset.draftId = item.id;
      row.textContent = (
        item.label
        + " · Spalten "
        + String(firstColumn)
        + "–"
        + String(lastColumn)
        + (item.helpText.length === 0 ? "" : " · Hilfe: " + item.helpText)
        + (item.isRequired ? " · Pflichtfeld" : "")
        + (item.kind === "field" ? " · Datentyp: " + item.dataType : "")
        + (
          item.kind === "field" && isChoiceDataType(item.dataType)
            ? (
              item.options.length === 0
                ? " · Auswahloptionen: noch nicht konfiguriert"
                : " · Auswahloptionen: " + item.options.map((option) => option.label).join(" | ")
            )
            : ""
        )
        + (
          item.kind === "field" && isChoiceDataType(item.dataType)
            ? " · " + choiceDefaultSelectionPreview(item)
            : ""
        )
        + (defaultValuePreview(item).length === 0 ? "" : " · Standard: " + defaultValuePreview(item))
      );
      list.appendChild(row);
    }

    let activeList = null;
    visibleDraftElements.forEach((item) => {
      if (item.kind === "section") {
        const section = document.createElement("section");
        section.className = "preview-section";
        section.dataset.draftId = item.id;

        const heading = document.createElement("h3");
        heading.id = "preview-section-" + item.id;
        section.setAttribute("aria-labelledby", heading.id);

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "preview-section-toggle";
        toggle.dataset.draftId = item.id;
        toggle.textContent = item.label;
        toggle.setAttribute("aria-expanded", String(!collapsedSectionIds.has(item.id)));
        const listId = "preview-section-items-" + item.id;
        toggle.setAttribute("aria-controls", listId);
        toggle.addEventListener("click", () => togglePreviewSection(item.id));
        heading.appendChild(toggle);
        section.appendChild(heading);

        activeList = document.createElement("ol");
        activeList.className = "preview-section-items";
        activeList.id = listId;
        activeList.hidden = collapsedSectionIds.has(item.id);
        section.appendChild(activeList);
        preview.appendChild(section);
        return;
      }

      if (activeList === null) {
        activeList = document.createElement("ol");
        activeList.className = "preview-unsectioned-items";
        preview.appendChild(activeList);
      }
      appendPreviewRow(activeList, item);
    });
  }

  function selectKind(button) {
    selectedKind = button.dataset.kind;
    selectedLabel = button.textContent.trim();
    selectedWidth = Number(button.dataset.width);
    paletteButtons.forEach((candidate) => {
      candidate.setAttribute("aria-pressed", String(candidate === button));
    });
    updateTargetAvailability();
    setStatus(
      selectedLabel
      + " gewählt · Breite "
      + String(selectedWidth)
      + " Spalte(n). Zielspalte wählen."
    );
  }

  function placeAt(column) {
    if (movingDraftId !== null) {
      const moving = draftElements.find((item) => item.id === movingDraftId);
      if (moving === undefined) {
        movingDraftId = null;
        updateTargetAvailability();
        return;
      }
      if (!placementFitsGrid(column, moving.width)) {
        setStatus(
          "Nicht verschoben: "
          + moving.label
          + " passt ab Spalte "
          + String(column + 1)
          + " nicht vollständig ins Raster."
        );
        return;
      }
      moving.column = column;
      const movingIndex = draftElements.findIndex((item) => item.id === moving.id);
      const movingPosition = temporaryGridPosition(moving, movingIndex + 1);
      setTemporaryGridPosition(moving.id, movingPosition.row, column, moving.width);
      movingDraftId = null;
      renderDraft();
      updateTargetAvailability();
      setStatus(
        moving.label
        + " nach Spalte "
        + String(column + 1)
        + " verschoben · nur temporärer Browserentwurf."
      );
      targetButtons[column].focus();
      return;
    }

    if (selectedKind === null || selectedLabel === null || selectedWidth === null) {
      setStatus("Zuerst eine Komponente auswählen.");
      return;
    }

    if (!placementFitsGrid(column, selectedWidth)) {
      setStatus(
        "Nicht platziert: "
        + selectedLabel
        + " passt ab Spalte "
        + String(column + 1)
        + " nicht vollständig ins Raster."
      );
      return;
    }

    const created = {
      id: nextDraftElementId(),
      kind: selectedKind,
      label: selectedLabel,
      column,
      width: selectedWidth,
      helpText: "",
      isRequired: false,
      isVisible: true,
      dataType: selectedKind === "field" ? "text" : null,
      defaultValue: selectedKind === "field" ? "" : null,
      options: selectedKind === "field" ? [] : null,
      defaultSelection: null,
      requiredPreviewValue: "",
      numberRangeBoundType: "min",
      numberRangeBoundaryValue: "",
      numberRangePreviewValue: "",
      dateRangeFrom: "",
      dateRangeTo: "",
      dateRangePreviewValue: "",
      allowedFileTypes: "",
      fileTypePreviewValue: "",
    };
    draftElements.push(created);
    setTemporaryGridPosition(created.id, draftElements.length, column, created.width);
    renderDraft();
    setStatus(
      selectedLabel
      + " in Spalte "
      + String(column + 1)
      + " platziert · nur temporärer Browserentwurf."
    );
  }

  function setTargetTabStop(index) {
    targetButtons.forEach((button, candidateIndex) => {
      button.tabIndex = candidateIndex === index ? 0 : -1;
    });
  }

  function focusSiblingTarget(index, direction) {
    const next = (index + direction + targetButtons.length) % targetButtons.length;
    setTargetTabStop(next);
    targetButtons[next].focus();
  }

  gridAssistantButton.addEventListener("click", showGridSuggestion);

  previewModeButtons.forEach((button) => {
    button.addEventListener("click", () => setPreviewMode(button.dataset.previewMode));
  });

  paletteButtons.forEach((button) => {
    button.addEventListener("click", () => selectKind(button));
  });

  targetButtons.forEach((button, index) => {
    button.addEventListener("focus", () => setTargetTabStop(index));
    button.addEventListener("click", () => {
      setTargetTabStop(index);
      placeAt(Number(button.dataset.column));
    });
    button.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        focusSiblingTarget(index, -1);
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        focusSiblingTarget(index, 1);
      } else if (event.key === "Escape" && movingDraftId !== null) {
        event.preventDefault();
        cancelMove();
      }
    });
  });

  if (
    !placementFitsGrid(0, gridColumns)
    || placementFitsGrid(1, gridColumns)
    || placementFitsGrid(-1, 1)
  ) {
    throw new Error("Masken-Baukasten Raster-Selbstprüfung fehlgeschlagen.");
  }

  setTargetTabStop(0);
  updateTargetAvailability();
})();