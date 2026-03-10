from claude_usage_master.dimension_scorer import calc_d3, score_dimensions
from claude_usage_master.models import QuestionnaireInput


def test_calc_d3_caps_at_100() -> None:
    q10 = {
        "code_gen": 3,
        "file_analysis": 3,
        "artifacts": 3,
        "projects": 3,
        "system_prompt": 3,
        "api": 3,
        "claude_code": 3,
        "mcp": 3,
    }
    assert calc_d3(q10) == 100.0


def test_score_dimensions_range() -> None:
    data = {f"q{i}": 3 for i in range(1, 23)}
    data["q10_depth"] = {"api": 2, "claude_code": 2}
    q = QuestionnaireInput(**data)
    scores = score_dimensions(q)
    assert set(scores.keys()) == {"D1", "D2", "D3", "D4", "D5", "D6"}
    assert all(0 <= v <= 100 for v in scores.values())

