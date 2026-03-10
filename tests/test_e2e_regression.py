import json
from pathlib import Path

from typer.testing import CliRunner

from claude_usage_master.cli import app


def _make_questionnaire(path: Path, value: int = 3) -> None:
    payload = {f"q{i}": value for i in range(1, 23)}
    payload["q10_depth"] = {"api": 2, "claude_code": 2}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_e2e_run_without_logs_has_neutral_corrections(tmp_path: Path) -> None:
    runner = CliRunner()
    input_file = tmp_path / "questionnaire.json"
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True)
    _make_questionnaire(input_file)

    output_file = tmp_path / "rating_result.json"
    history_file = tmp_path / "ratings_history.json"
    report_file = tmp_path / "report.html"
    checkpoint_file = tmp_path / "log_checkpoint.json"

    result = runner.invoke(
        app,
        [
            "run",
            "--input",
            str(input_file),
            "--logs",
            str(logs_dir),
            "--output",
            str(output_file),
            "--history",
            str(history_file),
            "--report",
            str(report_file),
            "--checkpoint",
            str(checkpoint_file),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(output_file.read_text(encoding="utf-8"))
    assert payload["source_breakdown"]["logs_correction"] == 0.0
    assert payload["source_breakdown"]["hooks_stability"] == 0.0
    assert payload["conflict_adjustment"]["tier"] == "no_data"


def test_e2e_history_appends_on_repeated_runs(tmp_path: Path) -> None:
    runner = CliRunner()
    input_file = tmp_path / "questionnaire.json"
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True)
    (logs_dir / "events.jsonl").write_text('{"ts":"2026-03-01T10:00:00Z"}\n', encoding="utf-8")
    _make_questionnaire(input_file, value=4)

    output_file = tmp_path / "rating_result.json"
    history_file = tmp_path / "ratings_history.json"
    report_file = tmp_path / "report.html"
    checkpoint_file = tmp_path / "log_checkpoint.json"

    args = [
        "run",
        "--input",
        str(input_file),
        "--logs",
        str(logs_dir),
        "--output",
        str(output_file),
        "--history",
        str(history_file),
        "--report",
        str(report_file),
        "--checkpoint",
        str(checkpoint_file),
    ]

    assert runner.invoke(app, args).exit_code == 0
    assert runner.invoke(app, args).exit_code == 0

    history = json.loads(history_file.read_text(encoding="utf-8"))
    assert len(history) == 2
    assert all("final_score" in item for item in history)

