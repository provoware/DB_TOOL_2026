from __future__ import annotations

from html import escape
from wsgiref.simple_server import WSGIServer, make_server

from provoware_db.mask_builder.model import GRID_COLUMNS, MaskElementKind


_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})

_INTERACTION_SCRIPT = r"""
<script>
(() => {
  "use strict";

  const paletteButtons = Array.from(document.querySelectorAll(".palette-item"));
  const targetButtons = Array.from(document.querySelectorAll(".placement-target"));
  const canvas = document.querySelector(".canvas");
  const placedLayer = document.getElementById("placed-elements");
  const emptyState = document.querySelector(".canvas-empty");
  const preview = document.getElementById("preview");
  const status = document.getElementById("interaction-status");
  const gridColumns = Number(canvas.dataset.gridColumns);
  const draftElements = [];
  let nextDraftId = 1;
  let nextDraftOptionId = 1;
  let selectedKind = null;
  let selectedLabel = null;
  let selectedWidth = null;
  let movingDraftId = null;
  let editingDraftId = null;
  let editingHelpDraftId = null;

  function setStatus(message) {
    status.textContent = message;
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
    item.dataType = select.value;
    renderDraft();
    setStatus(
      item.label
      + " · Datentyp "
      + item.dataType
      + (isChoiceDataType(item.dataType)\n        ? (item.options.length === 0\n          ? " · Auswahltyp unvollständig: noch keine Optionen konfiguriert"\n          : " · " + String(item.options.length) + " Auswahloption(en) konfiguriert")\n        : "")
      + " · nur temporärer Browserentwurf."
    );
    focusDataTypeControl(id);
  }

  function isChoiceDataType(dataType) {
    return dataType === "single_choice" || dataType === "multi_choice";
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

  function removeDraft(id) {
    const index = draftElements.findIndex((item) => item.id === id);
    if (index < 0) {
      return;
    }
    const removed = draftElements[index];
    draftElements.splice(index, 1);
    renderDraft();
    setStatus(removed.label + " entfernt · nur temporärer Browserentwurf.");
    targetButtons[removed.column].focus();
  }

  function renderDraft() {
    placedLayer.replaceChildren();
    draftElements.forEach((item, index) => {
      const card = document.createElement("div");
      card.className = "placed-element";
      card.dataset.kind = item.kind;
      card.dataset.draftId = item.id;
      card.setAttribute("role", "group");
      card.setAttribute("aria-label", item.label);
      card.style.gridColumn = String(item.column + 1) + " / span " + String(item.width);
      card.style.gridRow = String(index + 1);

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
            item.options.forEach((option) => {
              const optionRow = document.createElement("li");
              optionRow.dataset.optionId = option.id;
              optionRow.textContent = option.label;
              optionList.appendChild(optionRow);
            });
            card.appendChild(optionList);
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

    const list = document.createElement("ol");
    draftElements.forEach((item) => {
      const row = document.createElement("li");
      const firstColumn = item.column + 1;
      const lastColumn = item.column + item.width;
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
        + (defaultValuePreview(item).length === 0 ? "" : " · Standard: " + defaultValuePreview(item))
      );
      list.appendChild(row);
    });
    preview.appendChild(list);
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

    draftElements.push({
      id: "draft-" + String(nextDraftId++),
      kind: selectedKind,
      label: selectedLabel,
      column,
      width: selectedWidth,
      helpText: "",
      isRequired: false,
      dataType: selectedKind === "field" ? "text" : null,
      defaultValue: selectedKind === "field" ? "" : null,
      options: selectedKind === "field" ? [] : null,
    });
    renderDraft();
    setStatus(
      selectedLabel
      + " in Spalte "
      + String(column + 1)
      + " platziert · nur temporärer Browserentwurf."
    );
  }

  function focusSiblingTarget(index, direction) {
    const next = (index + direction + targetButtons.length) % targetButtons.length;
    targetButtons[next].focus();
  }

  paletteButtons.forEach((button) => {
    button.addEventListener("click", () => selectKind(button));
  });

  targetButtons.forEach((button, index) => {
    button.addEventListener("click", () => placeAt(Number(button.dataset.column)));
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

  updateTargetAvailability();
})();
</script>
"""


def _draft_width(kind: MaskElementKind) -> int:
    return {
        MaskElementKind.FIELD: 4,
        MaskElementKind.HEADING: GRID_COLUMNS,
        MaskElementKind.SECTION: GRID_COLUMNS,
        MaskElementKind.NOTE: 6,
        MaskElementKind.SEPARATOR: GRID_COLUMNS,
    }[kind]


def render_editor_shell() -> str:
    palette = "".join(
        (
            f'<button type="button" class="palette-item" '
            f'data-kind="{escape(kind.value)}" data-width="{_draft_width(kind)}" '
            f'aria-pressed="false">{escape(_label(kind))}</button>'
        )
        for kind in MaskElementKind
    )
    columns = "".join(
        f'<span class="grid-column" aria-hidden="true" data-column="{column}"></span>'
        for column in range(1, GRID_COLUMNS + 1)
    )
    targets = "".join(
        (
            f'<button type="button" class="placement-target" data-column="{column}" '
            f'aria-label="In Spalte {column + 1} platzieren" '
            f'aria-keyshortcuts="Enter Space ArrowLeft ArrowRight Escape" aria-disabled="false">'
            f'{column + 1}</button>'
        )
        for column in range(GRID_COLUMNS)
    )
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PROVOWARE · Masken-Baukasten</title>
<style>
:root {{ color-scheme: dark; font-family: system-ui, sans-serif; background:#11131a; color:#f4f6fb; }}
* {{ box-sizing:border-box; }} body {{ margin:0; min-height:100vh; }}
header {{ padding:1.25rem 1.5rem; border-bottom:1px solid #34384a; }}
header p {{ margin:.35rem 0 0; color:#b8bfd2; }}
button:focus-visible, select:focus-visible, input:focus-visible {{ outline:3px solid #ffe66d; outline-offset:2px; }}
.editor {{ display:grid; grid-template-columns:minmax(14rem,20rem) minmax(32rem,1fr) minmax(18rem,26rem); gap:1rem; padding:1rem; }}
.panel {{ border:1px solid #34384a; border-radius:14px; background:#191c26; padding:1rem; min-width:0; }}
.panel h2 {{ margin-top:0; font-size:1.05rem; }}
.palette {{ display:grid; gap:.65rem; }}
.palette-item {{ width:100%; padding:.8rem; text-align:left; border:1px solid #4a526b; border-radius:10px; background:#232838; color:inherit; font:inherit; }}
.palette-item[aria-pressed="true"] {{ border-color:#8ca5ff; box-shadow:0 0 0 2px #8ca5ff33; }}
.canvas {{ position:relative; min-height:32rem; border:1px dashed #68708c; border-radius:12px; overflow:hidden; }}
.grid-guides {{ position:absolute; inset:0; display:grid; grid-template-columns:repeat(12,1fr); pointer-events:none; }}
.grid-column {{ border-right:1px solid #303548; min-width:0; }} .grid-column:last-child {{ border-right:0; }}
.placement-targets {{ position:relative; z-index:2; display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:.25rem; padding:.5rem; }}
.placement-target {{ min-width:0; min-height:2.5rem; border:1px solid #4a526b; border-radius:7px; background:#202536; color:#f4f6fb; font:inherit; }}
.placement-target[aria-disabled="true"] {{ border-color:#5d4650; color:#9a8790; background:#211b20; }}
.placed-elements {{ position:relative; z-index:1; display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); grid-auto-rows:minmax(3rem,auto); gap:.4rem; padding:1rem .5rem 3rem; }}
.placed-element {{ display:flex; align-items:center; justify-content:space-between; gap:.5rem; min-width:0; padding:.6rem; border:1px solid #6978a4; border-radius:8px; background:#242a3c; }}
.edit-label, .edit-help, .save-label, .save-help, .toggle-required, .datatype-select, .move-draft, .remove-draft {{ flex:0 0 auto; padding:.35rem .5rem; border:1px solid #6978a4; border-radius:6px; background:#191c26; color:inherit; font:inherit; }}
.label-editor, .help-editor, .option-editor {{ display:flex; gap:.4rem; min-width:0; }}
.label-editor-input, .help-editor-input, .option-editor-input {{ min-width:0; max-width:12rem; padding:.35rem .45rem; border:1px solid #6978a4; border-radius:6px; background:#11131a; color:inherit; font:inherit; }}
.draft-help-text {{ color:#b8bfd2; overflow-wrap:anywhere; }}
.required-state, .datatype-label, .default-value-label {{ color:#d7def5; font-weight:600; }}
.choice-state {{ color:#b8bfd2; font-weight:600; overflow-wrap:anywhere; }}
.option-editor-label {{ color:#d7def5; font-weight:600; }}
.choice-options-list {{ width:100%; margin:.2rem 0 .4rem; padding-left:1.5rem; }}
.default-value-control {{ min-width:0; max-width:12rem; padding:.35rem .45rem; border:1px solid #6978a4; border-radius:6px; background:#11131a; color:inherit; font:inherit; }}
.canvas-empty {{ position:absolute; inset:4rem 0 0; display:grid; place-items:center; padding:2rem; text-align:center; color:#aeb6ca; pointer-events:none; }}
.canvas-empty[hidden] {{ display:none; }}
.preview-card {{ min-height:12rem; border:1px solid #303548; border-radius:10px; padding:1rem; background:#141720; }}
.status {{ display:inline-block; margin-top:.75rem; padding:.35rem .6rem; border:1px solid #4a526b; border-radius:999px; color:#b8bfd2; }}
@media (max-width:1000px) {{ .editor {{ grid-template-columns:1fr; }} .canvas {{ min-height:24rem; }} .placed-element {{ align-items:stretch; flex-direction:column; }} .placed-element > span, .datatype-label, .default-value-label, .choice-state {{ min-width:0; overflow-wrap:anywhere; }} .label-editor, .help-editor, .option-editor {{ align-items:stretch; flex-direction:column; width:100%; }} .label-editor-input, .help-editor-input, .option-editor-input {{ max-width:none; width:100%; }} .edit-label, .edit-help, .save-label, .save-help, .toggle-required, .datatype-select, .default-value-control, .add-option, .move-draft, .remove-draft {{ align-self:stretch; width:100%; }} }}
</style>
</head>
<body>
<header><strong>PROVOWARE · Masken-Baukasten</strong><p>Entwurf ohne Speichern und ohne Datenbankzugriff.</p></header>
<main class="editor">
<section class="panel" aria-labelledby="palette-title"><h2 id="palette-title">Komponenten</h2><div class="palette">{palette}</div></section>
<section class="panel" aria-labelledby="canvas-title"><h2 id="canvas-title">12-Spalten-Arbeitsfläche</h2><p>Komponente wählen, dann eine Zielspalte anklicken. Mit ← und → zwischen Zielspalten wechseln; Enter oder Leertaste platziert.</p><div class="canvas" data-grid-columns="{GRID_COLUMNS}"><div class="grid-guides">{columns}</div><div class="placement-targets" aria-label="Zielspalten">{targets}</div><div class="placed-elements" id="placed-elements"></div><p class="canvas-empty">Noch keine Komponenten platziert.</p></div><span class="status" id="interaction-status" role="status" aria-live="polite">Nur Entwurf · nicht gespeichert</span></section>
<section class="panel" aria-labelledby="preview-title"><h2 id="preview-title">Vorschau</h2><div class="preview-card" id="preview"><p>Noch keine Komponenten platziert.</p></div></section>
</main>
{_INTERACTION_SCRIPT}
</body>
</html>"""


def _label(kind: MaskElementKind) -> str:
    return {
        MaskElementKind.FIELD: "Eingabefeld",
        MaskElementKind.HEADING: "Überschrift",
        MaskElementKind.SECTION: "Bereich",
        MaskElementKind.NOTE: "Hinweis",
        MaskElementKind.SEPARATOR: "Trennlinie",
    }[kind]


def application(environ: dict[str, object], start_response):
    method = str(environ.get("REQUEST_METHOD", "GET")).upper()
    path = str(environ.get("PATH_INFO", "/"))
    if method != "GET":
        start_response("405 Method Not Allowed", [("Content-Type", "text/plain; charset=utf-8"), ("Allow", "GET")])
        return [b"Nur GET ist in diesem Editor-Slice erlaubt.\n"]
    if path != "/":
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Nicht gefunden.\n"]
    body = render_editor_shell().encode("utf-8")
    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body))), ("Cache-Control", "no-store")])
    return [body]


def make_editor_server(host: str = "127.0.0.1", port: int = 0) -> WSGIServer:
    if host not in _LOOPBACK_HOSTS:
        raise ValueError("Der Masken-Baukasten darf nur an eine Loopback-Adresse gebunden werden.")
    return make_server(host, port, application)