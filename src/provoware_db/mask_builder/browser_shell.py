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
  let selectedKind = null;
  let selectedLabel = null;
  let selectedWidth = null;

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
    targetButtons.forEach((button) => {
      const column = Number(button.dataset.column);
      const invalid = (
        selectedWidth !== null
        && !placementFitsGrid(column, selectedWidth)
      );
      button.setAttribute("aria-disabled", String(invalid));
      button.title = invalid
        ? "Diese Komponente passt ab hier nicht vollständig ins 12-Spalten-Raster."
        : "";
    });
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
      card.style.gridColumn = String(item.column + 1) + " / span " + String(item.width);
      card.style.gridRow = String(index + 1);

      const label = document.createElement("span");
      label.textContent = item.label;
      card.appendChild(label);

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
            f'aria-keyshortcuts="Enter Space ArrowLeft ArrowRight" aria-disabled="false">'
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
button:focus-visible {{ outline:3px solid #ffe66d; outline-offset:2px; }}
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
.remove-draft {{ flex:0 0 auto; padding:.35rem .5rem; border:1px solid #6978a4; border-radius:6px; background:#191c26; color:inherit; font:inherit; }}
.canvas-empty {{ position:absolute; inset:4rem 0 0; display:grid; place-items:center; padding:2rem; text-align:center; color:#aeb6ca; pointer-events:none; }}
.canvas-empty[hidden] {{ display:none; }}
.preview-card {{ min-height:12rem; border:1px solid #303548; border-radius:10px; padding:1rem; background:#141720; }}
.status {{ display:inline-block; margin-top:.75rem; padding:.35rem .6rem; border:1px solid #4a526b; border-radius:999px; color:#b8bfd2; }}
@media (max-width:1000px) {{ .editor {{ grid-template-columns:1fr; }} .canvas {{ min-height:24rem; }} .placed-element {{ align-items:stretch; flex-direction:column; }} .placed-element > span {{ min-width:0; overflow-wrap:anywhere; }} .remove-draft {{ align-self:stretch; width:100%; }} }}
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
