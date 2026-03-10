import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .local_store import write_json
from .models import QuestionnaireInput


def create_server(
    host: str,
    port: int,
    questionnaire_path: Path,
    page_path: Path,
) -> ThreadingHTTPServer:
    questionnaire_path = questionnaire_path.resolve()
    page_path = page_path.resolve()

    class Handler(BaseHTTPRequestHandler):
        server_version = "ClaudeUsageMasterLocalWeb/1.0"

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, path: Path) -> None:
            if not path.exists():
                self.send_error(HTTPStatus.NOT_FOUND, "questionnaire page not found")
                return
            body = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path in {"/", "/questionnaire.html"}:
                self._send_html(page_path)
                return
            self.send_error(HTTPStatus.NOT_FOUND, "not found")

        def do_PUT(self) -> None:  # noqa: N802
            if self.path != "/api/questionnaire":
                self.send_error(HTTPStatus.NOT_FOUND, "not found")
                return

            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
                normalized = QuestionnaireInput.model_validate(payload).model_dump()
            except Exception as exc:
                self._send_json(HTTPStatus.BAD_REQUEST, {"ok": False, "error": str(exc)})
                return

            write_json(questionnaire_path, normalized)
            self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "path": str(questionnaire_path),
                },
            )

        def log_message(self, fmt: str, *args: object) -> None:
            # Keep local service output concise.
            return

    return ThreadingHTTPServer((host, port), Handler)


def serve_questionnaire(
    host: str,
    port: int,
    questionnaire_path: Path,
    page_path: Path,
) -> None:
    server = create_server(
        host=host,
        port=port,
        questionnaire_path=questionnaire_path,
        page_path=page_path,
    )
    try:
        server.serve_forever()
    finally:
        server.server_close()

