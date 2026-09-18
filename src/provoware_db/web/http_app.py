from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from .read_adapter import CatalogReadPort, WebCatalogReadAdapter
from .render import render_page

StartResponse = Callable[[str, list[tuple[str, str]]], Any]


def _one(params: dict[str, list[str]], name: str) -> str | None:
    values = params.get(name)
    if not values:
        return None
    value = values[0].strip()
    return value or None


def make_app(catalog: CatalogReadPort) -> Callable[[dict[str, Any], StartResponse], Iterable[bytes]]:
    """Build a GET-only WSGI application over the read-only catalog port."""
    adapter = WebCatalogReadAdapter(catalog)

    def app(environ: dict[str, Any], start_response: StartResponse) -> Iterable[bytes]:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        if method != "GET":
            body = b"Nur lesender GET-Zugriff ist erlaubt."
            start_response(
                "405 Method Not Allowed",
                [
                    ("Content-Type", "text/plain; charset=utf-8"),
                    ("Content-Length", str(len(body))),
                    ("Allow", "GET"),
                ],
            )
            return [body]

        if str(environ.get("PATH_INFO", "/")) != "/":
            body = b"Nicht gefunden."
            start_response(
                "404 Not Found",
                [
                    ("Content-Type", "text/plain; charset=utf-8"),
                    ("Content-Length", str(len(body))),
                ],
            )
            return [body]

        params = parse_qs(str(environ.get("QUERY_STRING", "")), keep_blank_values=False)
        category_id = _one(params, "category_id")
        entry_id = _one(params, "entry_id")

        page = render_page(
            adapter,
            category_id=category_id,
            entry_id=entry_id,
        ).encode("utf-8")

        start_response(
            "200 OK",
            [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(page))),
                ("Cache-Control", "no-store"),
                ("X-Content-Type-Options", "nosniff"),
            ],
        )
        return [page]

    return app


def serve(catalog: CatalogReadPort, *, host: str = "127.0.0.1", port: int = 8765) -> None:
    """Serve the read-only UI locally on loopback only by default."""
    with make_server(host, port, make_app(catalog)) as server:
        server.serve_forever()
