from claude_usage_master.rating_engine import apply_ceiling, apply_source_corrections, evaluate, score_to_rating


def test_apply_ceiling_hits_d1_rule() -> None:
    dim_scores = {"D1": 10, "D2": 80, "D3": 80, "D4": 80, "D5": 80, "D6": 80}
    final, detail = apply_ceiling(92.0, dim_scores)
    assert final == 45.0
    assert detail
    assert "最高 C" in str(detail[0]["reason"])


def test_evaluate_output_shape() -> None:
    dim_scores = {"D1": 70, "D2": 70, "D3": 70, "D4": 70, "D5": 70, "D6": 70}
    result = evaluate(dim_scores)
    assert result.final_score >= 0
    assert result.rating in {"F", "D", "C", "B", "A", "S", "SS"}
    assert "questionnaire" in result.source_breakdown
    assert result.source_breakdown["questionnaire"] == result.base_score


def test_apply_source_corrections_recomputes_rating() -> None:
    dim_scores = {"D1": 95, "D2": 95, "D3": 95, "D4": 95, "D5": 95, "D6": 95}
    result = evaluate(dim_scores)
    result.source_breakdown["logs_correction"] = -30.0
    adjusted = apply_source_corrections(result)
    assert adjusted.final_score <= 100
    assert adjusted.final_score >= 0
    assert adjusted.rating in {"F", "D", "C", "B", "A", "S", "SS"}


def test_score_to_rating_boundaries_have_no_gaps() -> None:
    assert score_to_rating(95.0)[0] == "SS"
    assert score_to_rating(94.99)[0] == "S"
    assert score_to_rating(80.0)[0] == "S"
    assert score_to_rating(79.99)[0] == "A"
    assert score_to_rating(65.0)[0] == "A"
    assert score_to_rating(64.99)[0] == "B"
    assert score_to_rating(45.0)[0] == "B"
    assert score_to_rating(44.99)[0] == "C"
    assert score_to_rating(25.0)[0] == "C"
    assert score_to_rating(24.99)[0] == "D"
    assert score_to_rating(10.0)[0] == "D"
    assert score_to_rating(9.99)[0] == "F"


def test_apply_ceiling_respects_rule_caps() -> None:
    # D1 very low should cap at 45 even when higher score is provided.
    dim_scores = {"D1": 10, "D2": 90, "D3": 90, "D4": 90, "D5": 90, "D6": 90}
    capped, detail = apply_ceiling(99.0, dim_scores)
    assert capped == 45.0
    assert any(item["rule"] == "D1<20" for item in detail)
    assert all("最高 " in str(item["reason"]) for item in detail)
