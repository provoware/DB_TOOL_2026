from __future__ import annotations

from html import escape
from pathlib import Path
from wsgiref.simple_server import WSGIServer, make_server

from provoware_db.mask_builder.model import GRID_COLUMNS, MaskElementKind


_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})

_INTERACTION_SCRIPT = "\n<script>\n" + Path(__file__).with_name("interaction_script.js").read_text(encoding="utf-8") + "\n</script>\n"


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
            f'aria-keyshortcuts="Enter Space ArrowLeft ArrowRight Escape" '
            f'tabindex="{"0" if column == 0 else "-1"}" aria-disabled="false">'
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
.placed-element {{ position:relative; }}
.edit-label, .edit-help, .save-label, .save-help, .toggle-required, .toggle-visibility, .width-select, .datatype-select, .move-draft-up, .move-draft-down, .move-draft, .remove-draft {{ flex:0 0 auto; padding:.35rem .5rem; border:1px solid #6978a4; border-radius:6px; background:#191c26; color:inherit; font:inherit; }}
.tooltip-trigger {{ flex:0 0 auto; width:1.8rem; height:1.8rem; border:1px solid #8ca5ff; border-radius:50%; background:#202536; color:#f4f6fb; font:inherit; font-weight:700; }}
.tooltip-text {{ position:absolute; z-index:5; max-width:20rem; margin-top:2.25rem; padding:.55rem .65rem; border:1px solid #8ca5ff; border-radius:7px; background:#11131a; color:#f4f6fb; box-shadow:0 .4rem 1rem #0008; opacity:0; pointer-events:none; }}
.tooltip-trigger:hover + .tooltip-text, .tooltip-trigger:focus-visible + .tooltip-text {{ opacity:1; }}
.label-editor, .help-editor, .option-editor {{ display:flex; gap:.4rem; min-width:0; }}
.label-editor-input, .help-editor-input, .option-editor-input {{ min-width:0; max-width:12rem; padding:.35rem .45rem; border:1px solid #6978a4; border-radius:6px; background:#11131a; color:inherit; font:inherit; }}
.draft-help-text {{ color:#b8bfd2; overflow-wrap:anywhere; }}
.required-state, .visibility-state, .width-label, .datatype-label, .default-value-label, .default-selection-label {{ color:#d7def5; font-weight:600; }}
.required-preview-label {{ color:#d7def5; font-weight:600; }}
.required-preview-input {{ min-width:0; max-width:12rem; padding:.35rem .45rem; border:1px solid #6978a4; border-radius:6px; background:#11131a; color:inherit; font:inherit; }}
.required-preview-result {{ width:100%; padding:.45rem .55rem; border:1px solid #4a526b; border-radius:7px; color:#d7def5; }}
.required-preview-result[data-rule-state="violated"] {{ border-color:#ff9c9c; color:#ffd0d0; }}
.required-preview-result[data-rule-state="satisfied"] {{ border-color:#76d7a0; color:#bff2d2; }}
.number-range-preview {{ display:flex; flex-wrap:wrap; align-items:center; gap:.45rem; width:100%; padding:.55rem; border:1px solid #4a526b; border-radius:7px; }}
.number-range-preview legend {{ color:#d7def5; font-weight:600; }}
.number-range-bound, .number-range-boundary, .number-range-value {{ min-width:0; max-width:10rem; padding:.35rem .45rem; border:1px solid #6978a4; border-radius:6px; background:#11131a; color:inherit; font:inherit; }}
.number-range-result {{ width:100%; padding:.45rem .55rem; border:1px solid #4a526b; border-radius:7px; color:#d7def5; }}
.number-range-result[data-rule-state="violated"] {{ border-color:#ff9c9c; color:#ffd0d0; }}
.number-range-result[data-rule-state="satisfied"] {{ border-color:#76d7a0; color:#bff2d2; }}
.date-range-preview, .file-type-preview {{ display:flex; flex-wrap:wrap; align-items:center; gap:.45rem; width:100%; padding:.55rem; border:1px solid #4a526b; border-radius:7px; }}
.date-range-preview legend, .file-type-preview legend {{ color:#d7def5; font-weight:600; }}
.date-range-preview input, .file-type-preview input {{ min-width:0; max-width:12rem; padding:.35rem .45rem; border:1px solid #6978a4; border-radius:6px; background:#11131a; color:inherit; font:inherit; }}
.date-range-result, .file-type-result {{ width:100%; padding:.45rem .55rem; border:1px solid #4a526b; border-radius:7px; color:#d7def5; }}
.date-range-result[data-rule-state="violated"], .file-type-result[data-rule-state="violated"] {{ border-color:#ff9c9c; color:#ffd0d0; }}
.date-range-result[data-rule-state="satisfied"], .file-type-result[data-rule-state="satisfied"] {{ border-color:#76d7a0; color:#bff2d2; }}
.choice-state {{ color:#b8bfd2; font-weight:600; overflow-wrap:anywhere; }}
.option-editor-label {{ color:#d7def5; font-weight:600; }}
.choice-options-list {{ width:100%; margin:.2rem 0 .4rem; padding-left:1.5rem; }}
.choice-option-row {{ display:flex; align-items:center; gap:.4rem; flex-wrap:wrap; margin:.25rem 0; }}
.choice-option-label {{ flex:1 1 12rem; min-width:0; overflow-wrap:anywhere; }}
.default-selection-group {{ width:100%; margin:.2rem 0 .4rem; padding:.45rem; border:1px solid #4a526b; border-radius:8px; }}
.default-selection-row {{ display:flex; align-items:center; gap:.45rem; margin:.25rem 0; overflow-wrap:anywhere; }}
.default-selection-control {{ min-width:0; }}
.default-value-control {{ min-width:0; max-width:12rem; padding:.35rem .45rem; border:1px solid #6978a4; border-radius:6px; background:#11131a; color:inherit; font:inherit; }}
.canvas-empty {{ position:absolute; inset:4rem 0 0; display:grid; place-items:center; padding:2rem; text-align:center; color:#aeb6ca; pointer-events:none; }}
.canvas-empty[hidden] {{ display:none; }}
.preview-viewport-shell {{ max-width:100%; overflow-x:auto; padding:.25rem; border:1px solid #303548; border-radius:10px; background:#0f1118; }}
.preview-mode-controls {{ display:flex; gap:.5rem; flex-wrap:wrap; margin:0 0 .6rem; }}
.preview-mode-button {{ padding:.35rem .6rem; border:1px solid #6978a4; border-radius:999px; background:#191c26; color:inherit; font:inherit; }}
.preview-mode-button[aria-pressed="true"] {{ border-color:#8ca5ff; box-shadow:0 0 0 2px #8ca5ff33; }}
.preview-mode-label {{ display:inline-block; margin:0 0 .6rem; padding:.25rem .5rem; border:1px solid #4a526b; border-radius:999px; color:#d7def5; font-size:.9rem; font-weight:600; }}
.preview-card {{ min-height:32rem; max-width:none; border:1px solid #303548; border-radius:10px; padding:1.25rem; background:#141720; }}
.preview-card[data-preview-mode="desktop"] {{ width:72rem; box-shadow:inset 0 0 0 1px #242a3c; }}
.preview-card[data-preview-mode="tablet"] {{ width:48rem; box-shadow:inset 0 0 0 1px #2d3448; }}
.preview-card[data-preview-mode="narrow"] {{ width:22.5rem; box-shadow:inset 0 0 0 1px #37405a; }}
.preview-section {{ margin:0 0 1rem; padding:.75rem; border:1px solid #303548; border-radius:8px; }}
.preview-section h3 {{ margin:.1rem 0 .65rem; font-size:1rem; }}
.preview-section-toggle {{ width:100%; text-align:left; padding:.45rem .6rem; border:1px solid #6978a4; border-radius:6px; background:#191c26; color:inherit; font:inherit; font-weight:700; }}
.preview-section-toggle[aria-expanded="false"]::after {{ content:" · eingeklappt"; font-weight:400; }}
.preview-section-items, .preview-unsectioned-items {{ margin:.35rem 0 .75rem; padding-left:1.5rem; }}
.grid-assistant {{ margin-top:1rem; padding:.85rem; border:1px solid #4a526b; border-radius:10px; background:#151925; }}
.grid-assistant h3 {{ margin:.1rem 0 .45rem; font-size:1rem; }}
.grid-assistant p {{ margin:.35rem 0; color:#b8bfd2; }}
.grid-assistant-button, .grid-assistant-apply {{ padding:.45rem .7rem; border:1px solid #6978a4; border-radius:7px; background:#202536; color:inherit; font:inherit; }}
.grid-assistant-apply {{ margin-top:.65rem; }}
.grid-assistant-list {{ margin:.65rem 0 0; padding-left:1.5rem; }}
.grid-assistant-list li {{ margin:.25rem 0; overflow-wrap:anywhere; }}
.grid-assistant-summary, .grid-assistant-contract-note {{ margin:.65rem 0; }}
.grid-assistant-comparison {{ width:100%; border-collapse:collapse; margin-top:.65rem; font-size:.9rem; }}
.grid-assistant-comparison caption {{ text-align:left; font-weight:700; margin-bottom:.45rem; }}
.grid-assistant-comparison th, .grid-assistant-comparison td {{ padding:.45rem; border:1px solid #4a526b; text-align:left; vertical-align:top; overflow-wrap:anywhere; }}
.grid-assistant-comparison th {{ background:#202536; }}
.status {{ display:inline-block; margin-top:.75rem; padding:.35rem .6rem; border:1px solid #4a526b; border-radius:999px; color:#b8bfd2; }}
@media (max-width:1000px) {{ .editor {{ grid-template-columns:1fr; }} .canvas {{ min-height:24rem; }} .placed-element {{ align-items:stretch; flex-direction:column; }} .placed-element > span, .width-label, .datatype-label, .default-value-label, .default-selection-label, .choice-state, .visibility-state {{ min-width:0; overflow-wrap:anywhere; }} .required-preview-label {{ min-width:0; overflow-wrap:anywhere; }} .label-editor, .help-editor, .option-editor, .default-selection-group {{ align-items:stretch; flex-direction:column; width:100%; }} .number-range-preview, .date-range-preview, .file-type-preview {{ align-items:stretch; flex-direction:column; width:100%; }} .label-editor-input, .help-editor-input, .option-editor-input {{ max-width:none; width:100%; }} .required-preview-input, .number-range-bound, .number-range-boundary, .number-range-value, .date-range-preview input, .file-type-preview input {{ max-width:none; width:100%; }} .choice-option-row {{ align-items:stretch; flex-direction:column; }} .default-selection-row .default-selection-control {{ width:auto; align-self:flex-start; }} .edit-label, .edit-help, .save-label, .save-help, .toggle-required, .toggle-visibility, .width-select, .datatype-select, .default-value-control, .default-selection-control, .add-option, .move-option-up, .move-option-down, .remove-option, .move-draft-up, .move-draft-down, .duplicate-draft, .move-draft, .remove-draft {{ align-self:stretch; width:100%; }} }}
</style>
</head>
<body>
<header><strong>PROVOWARE · Masken-Baukasten</strong><p>Entwurf ohne Speichern und ohne Datenbankzugriff.</p></header>
<main class="editor">
<section class="panel" aria-labelledby="palette-title" data-focus-stage="1"><h2 id="palette-title">Komponenten</h2><div class="palette">{palette}</div></section>
<section class="panel" aria-labelledby="canvas-title" data-focus-stage="2"><h2 id="canvas-title">12-Spalten-Arbeitsfläche</h2><p id="canvas-keyboard-help">Komponente wählen, dann eine Zielspalte anklicken. Tab erreicht genau eine Zielspalte; mit ← und → zwischen Zielspalten wechseln; Enter oder Leertaste platziert. Danach folgen die Controls der platzierten Elemente.</p><div class="canvas" data-grid-columns="{GRID_COLUMNS}"><div class="grid-guides">{columns}</div><div class="placement-targets" aria-label="Zielspalten" aria-describedby="canvas-keyboard-help">{targets}</div><div class="placed-elements" id="placed-elements"></div><p class="canvas-empty">Noch keine Komponenten platziert.</p></div><aside class="grid-assistant" aria-labelledby="grid-assistant-title"><h3 id="grid-assistant-title">Raster-Assistent · Vorher/Nachher</h3><p>Vergleicht das aktuelle Layout mit dem berechneten Vorschlag und nennt jede geplante Zeilen-/Spaltenänderung. Reihenfolge und Breiten bleiben unverändert. Es wird nichts übernommen.</p><button type="button" class="grid-assistant-button" id="grid-assistant-button" aria-describedby="grid-assistant-title">Vorher/Nachher berechnen</button><div id="grid-assistant-output" aria-live="polite"><p>Noch kein Vergleich berechnet.</p></div></aside><span class="status" id="interaction-status" role="status" aria-live="polite">Nur Entwurf · nicht gespeichert</span></section>
<section class="panel" aria-labelledby="preview-title" data-focus-stage="3"><h2 id="preview-title">Vorschau</h2><div class="preview-mode-controls" role="group" aria-label="Vorschaugröße"><button type="button" class="preview-mode-button" data-preview-mode="desktop" aria-pressed="true">Desktop</button><button type="button" class="preview-mode-button" data-preview-mode="tablet" aria-pressed="false">Tablet</button><button type="button" class="preview-mode-button" data-preview-mode="narrow" aria-pressed="false">Schmal</button></div><p class="preview-mode-label" id="preview-mode-label">Desktop · 1152 px</p><div class="preview-viewport-shell" aria-label="Desktop-Vorschau, 1152 Pixel breit" aria-describedby="preview-mode-label"><div class="preview-card" id="preview" data-preview-mode="desktop" data-preview-width="1152"><p>Noch keine Komponenten platziert.</p></div></div></section>
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
    if path == "/favicon.ico":
        start_response("204 No Content", [("Content-Length", "0"), ("Cache-Control", "no-store")])
        return [b""]
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
