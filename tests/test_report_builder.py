from claude_usage_master.rating_engine import evaluate
from claude_usage_master.report_builder import render_html


def test_report_contains_source_breakdown_cards() -> None:
    dim_scores = {"D1": 70, "D2": 70, "D3": 70, "D4": 70, "D5": 70, "D6": 70}
    result = evaluate(dim_scores)
    result.source_breakdown["logs_correction"] = -1.5
    html = render_html(result)
    assert "来源占比" in html
    assert "问卷基础" in html
    assert "日志修正" in html
    assert "Hooks稳定" in html


def test_report_contains_conflict_metadata() -> None:
    dim_scores = {"D1": 70, "D2": 70, "D3": 85, "D4": 70, "D5": 70, "D6": 70}
    result = evaluate(dim_scores)
    result.conflict_adjustment.update({"tier": "mild", "gap": 12.0})
    html = render_html(result)
    assert "层级" in html
    assert "差值(gap)" in html
