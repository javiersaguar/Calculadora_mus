from __future__ import annotations

import argparse
import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .mus_rules import make_deck
from .simulator import SimulationError, calculate_probabilities


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_ROOT = PROJECT_ROOT / "static"


class MusRequestHandler(BaseHTTPRequestHandler):
    server_version = "MusProbabilidades/0.1"

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_default_headers("application/json")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_default_headers("image/x-icon")
            self.end_headers()
            return

        if parsed.path == "/health":
            self.write_json({"ok": True})
            return

        if parsed.path == "/api/deck":
            deck = [
                {"code": card.code, "rank": card.rank, "suit": card.suit, "label": card.label}
                for card in make_deck()
            ]
            self.write_json({"cards": deck})
            return

        if parsed.path in ("", "/", "/index.html"):
            self.serve_file(STATIC_ROOT / "index.html")
            return

        if parsed.path.startswith("/static/"):
            relative = unquote(parsed.path.removeprefix("/static/"))
            candidate = (STATIC_ROOT / relative).resolve()
            try:
                candidate.relative_to(STATIC_ROOT.resolve())
            except ValueError:
                self.write_json({"error": "Ruta no permitida"}, status=HTTPStatus.FORBIDDEN)
                return
            self.serve_file(candidate)
            return

        self.write_json({"error": "No encontrado"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/calculate":
            self.write_json({"error": "No encontrado"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.write_json({"error": "Content-Length no valido"}, status=HTTPStatus.BAD_REQUEST)
            return

        if content_length > 1_000_000:
            self.write_json({"error": "Peticion demasiado grande"}, status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return

        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise SimulationError("La peticion debe ser un objeto JSON.")
            result = calculate_probabilities(payload)
        except json.JSONDecodeError:
            self.write_json({"error": "JSON no valido"}, status=HTTPStatus.BAD_REQUEST)
            return
        except SimulationError as exc:
            self.write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:  # pragma: no cover - defensive API boundary
            self.write_json({"error": f"Error interno: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self.write_json(result)

    def serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.write_json({"error": "No encontrado"}, status=HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        content = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_default_headers(content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def write_json(self, data: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_default_headers("application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_default_headers(self, content_type: str) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor local para la calculadora de probabilidades de mus.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), MusRequestHandler)
    print(f"Mus Probabilidades disponible en http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
