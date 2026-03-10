import json
import threading
from pathlib import Path
from urllib import request
from urllib.error import HTTPError

from claude_usage_master.local_web import create_server


def _start_server(questionnaire_path: Path, page_path: Path):
    server = create_server(
        host="127.0.0.1",
        port=0,
        questionnaire_path=questionnaire_path,
        page_path=page_path,
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_local_web_put_questionnaire_writes_file(tmp_path: Path) -> None:
    questionnaire_path = tmp_path / "questionnaire.json"
    page_path = tmp_path / "questionnaire.html"
    page_path.write_text("<html><body>ok</body></html>", encoding="utf-8")

    server, thread = _start_server(questionnaire_path, page_path)
    try:
        host, port = server.server_address
        payload = {
            "q1": 3,
            "q2": 3,
            "q3": 3,
            "q4": 3,
            "q5": 3,
            "q6": 3,
            "q7": 3,
            "q8": 3,
            "q9": 3,
            "q10_depth": {"api": 2, "claude_code": 2, "projects": 1},
            "q11": 3,
            "q12": 3,
            "q13": 3,
            "q14": 3,
            "q15": 3,
            "q16": 3,
            "q17": 3,
            "q18": 3,
            "q19": 3,
            "q20": 3,
            "q21": 3,
            "q22": 3,
        }

        req = request.Request(
            f"http://{host}:{port}/api/questionnaire",
            method="PUT",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            assert resp.status == 200
            assert body["ok"] is True

        written = json.loads(questionnaire_path.read_text(encoding="utf-8"))
        assert written["q10_depth"]["api"] == 2
        assert written["q22"] == 3
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def test_local_web_put_questionnaire_rejects_invalid_payload(tmp_path: Path) -> None:
    questionnaire_path = tmp_path / "questionnaire.json"
    page_path = tmp_path / "questionnaire.html"
    page_path.write_text("<html><body>ok</body></html>", encoding="utf-8")

    server, thread = _start_server(questionnaire_path, page_path)
    try:
        host, port = server.server_address
        bad_payload = {"q1": 99}

        req = request.Request(
            f"http://{host}:{port}/api/questionnaire",
            method="PUT",
            data=json.dumps(bad_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        try:
            request.urlopen(req)
            assert False, "expected HTTPError"
        except HTTPError as exc:
            assert exc.code == 400
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)

