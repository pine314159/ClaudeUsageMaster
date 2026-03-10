import json
from pathlib import Path

from typer.testing import CliRunner

from claude_usage_master.cli import app
from claude_usage_master.log_analyzer import log_correction_cap


def test_cli_run_writes_result_and_report(tmp_path: Path) -> None:
    runner = CliRunner()
    input_file = tmp_path / "questionnaire.json"
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True)
    (logs_dir / "events.jsonl").write_text('{"event":"a"}\n', encoding="utf-8")

    payload = {f"q{i}": 3 for i in range(1, 23)}
    payload["q10_depth"] = {"api": 2, "claude_code": 2}
    input_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

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
    assert output_file.exists()
    assert report_file.exists()

    out = json.loads(output_file.read_text(encoding="utf-8"))
    assert out["rating"] in {"F", "D", "C", "B", "A", "S", "SS"}
    assert out["confidence"]["sample_size"] == 1
    assert 0.0 <= out["confidence"]["log_confidence"] <= 1.0
    cap = log_correction_cap(out["confidence"]["log_confidence"])
    assert abs(out["source_breakdown"]["logs_correction"]) <= cap
    assert 0.0 <= out["source_breakdown"]["hooks_stability"] <= 1.5
    assert out["conflict_adjustment"]["policy"] == "anti_self_inflation"
    assert "tier" in out["conflict_adjustment"]
    assert "gap" in out["conflict_adjustment"]

    report_html = report_file.read_text(encoding="utf-8")
    assert "维度雷达图" in report_html
    assert "规则命中卡片" in report_html
    assert "来源占比" in report_html
    assert "id=\"radar\"" in report_html
