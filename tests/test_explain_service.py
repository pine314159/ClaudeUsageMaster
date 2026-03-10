from claude_usage_master.explain_copy import SUGGESTION_ALIGN_LOGS, SUGGESTION_FIX_CEILING
from claude_usage_master.explain_service import assemble_result
from claude_usage_master.rating_engine import evaluate


def test_assemble_result_adds_contextual_suggestions() -> None:
    dim_scores = {"D1": 15, "D2": 70, "D3": 90, "D4": 70, "D5": 70, "D6": 70}
    result = evaluate(dim_scores)
    result.conflict_adjustment["detected"] = True

    assembled = assemble_result(result)

    assert SUGGESTION_FIX_CEILING in assembled.suggestions
    assert SUGGESTION_ALIGN_LOGS in assembled.suggestions


def test_assemble_result_refreshes_rating_desc() -> None:
    dim_scores = {"D1": 95, "D2": 95, "D3": 95, "D4": 95, "D5": 95, "D6": 95}
    result = evaluate(dim_scores)
    result.final_score = 70.0

    assembled = assemble_result(result)
    assert assembled.rating == "A"
    assert assembled.rating_desc == "Claude 进阶"
