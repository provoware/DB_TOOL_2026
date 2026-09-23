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
    assert 'id: "draft-" + String(draftElements.length + 1)' in html
    assert 'placedLayer.appendChild(card);' in html
    assert 'preview.appendChild(list);' in html


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
    test_temporary_interaction_has_no_persistence_or_network_write_path()
    test_root_is_get_only_and_unknown_paths_are_not_found()
    test_server_rejects_non_loopback_binding()
    test_browser_shell_has_no_database_or_store_dependency()
    print("MASK BUILDER TEMPORARY INTERACTION STEP 1: GRÜN")


if __name__ == "__main__":
    main()
