from __future__ import annotations

from html import escape
from wsgiref.simple_server import WSGIServer, make_server

from provoware_db.mask_builder.model import GRID_COLUMNS, MaskElementKind


_LOOPBACK_HOSTS = frozenset({"127.0.0.1", "::1", "localhost"})


def render_editor_shell() -> str:
    palette = "".join(
        f'<button type="button" class="palette-item" data-kind="{escape(kind.value)}">{escape(_label(kind))}</button>'
        for kind in MaskElementKind
    )
    columns = "".join(
        f'<span class="grid-column" aria-hidden="true" data-column="{column}"></span>'
        for column in range(1, GRID_COLUMNS + 1)
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
.editor {{ display:grid; grid-template-columns:minmax(14rem,20rem) minmax(32rem,1fr) minmax(18rem,26rem); gap:1rem; padding:1rem; }}
.panel {{ border:1px solid #34384a; border-radius:14px; background:#191c26; padding:1rem; min-width:0; }}
.panel h2 {{ margin-top:0; font-size:1.05rem; }}
.palette {{ display:grid; gap:.65rem; }}
.palette-item {{ width:100%; padding:.8rem; text-align:left; border:1px solid #4a526b; border-radius:10px; background:#232838; color:inherit; font:inherit; }}
.canvas {{ position:relative; min-height:32rem; display:grid; grid-template-columns:repeat(12,1fr); border:1px dashed #68708c; border-radius:12px; overflow:hidden; }}
.grid-column {{ border-right:1px solid #303548; min-width:0; }} .grid-column:last-child {{ border-right:0; }}
.canvas-empty {{ position:absolute; inset:0; display:grid; place-items:center; padding:2rem; text-align:center; color:#aeb6ca; pointer-events:none; }}
.preview-card {{ min-height:12rem; border:1px solid #303548; border-radius:10px; padding:1rem; background:#141720; }}
.status {{ display:inline-block; margin-top:.75rem; padding:.35rem .6rem; border:1px solid #4a526b; border-radius:999px; color:#b8bfd2; }}
@media (max-width:1000px) {{ .editor {{ grid-template-columns:1fr; }} .canvas {{ min-height:24rem; }} }}
</style>
</head>
<body>
<header><strong>PROVOWARE · Masken-Baukasten</strong><p>Entwurf ohne Speichern und ohne Datenbankzugriff.</p></header>
<main class="editor">
<section class="panel" aria-labelledby="palette-title"><h2 id="palette-title">Komponenten</h2><div class="palette">{palette}</div></section>
<section class="panel" aria-labelledby="canvas-title"><h2 id="canvas-title">12-Spalten-Arbeitsfläche</h2><div class="canvas" data-grid-columns="{GRID_COLUMNS}">{columns}<p class="canvas-empty">Komponenten werden in einem späteren Slice per Drag &amp; Drop platziert.</p></div><span class="status">Nur Entwurf · nicht gespeichert</span></section>
<section class="panel" aria-labelledby="preview-title"><h2 id="preview-title">Vorschau</h2><div class="preview-card" id="preview"><p>Noch keine Komponenten platziert.</p></div></section>
</main>
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
