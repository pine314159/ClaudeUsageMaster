import json
from pathlib import Path

import pytest

from claude_usage_master.dimension_scorer import score_dimensions
from claude_usage_master.explain_service import assemble_result
from claude_usage_master.fusion_service import fuse_sources
from claude_usage_master.models import QuestionnaireInput
from claude_usage_master.rating_engine import evaluate

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _load_case(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_between(value: float, bounds: list[float]) -> None:
    low, high = float(bounds[0]), float(bounds[1])
    assert low <= float(value) <= high


@pytest.mark.parametrize(
    "case_file",
    [
        "high_score.json",
        "median_neutral.json",
        "conflict_high_conf.json",
        "conflict_low_conf.json",
    ],
)
def test_scenario_fixtures(case_file: str) -> None:
    case = _load_case(FIXTURE_DIR / case_file)

    questionnaire = QuestionnaireInput.model_validate(case["questionnaire"])
    dim_scores = score_dimensions(questionnaire)
    result = evaluate(dim_scores)
    result = fuse_sources(
        result=result,
        questionnaire_d3=dim_scores["D3"],
        sample_size=int(case["fusion"]["sample_size"]),
        coverage_days=int(case["fusion"]["coverage_days"]),
    )
    result = assemble_result(result)

    expected = case["expected"]
    assert result.rating in set(expected["rating_in"])
    _assert_between(result.final_score, expected["final_score_range"])
    _assert_between(float(result.confidence["log_confidence"]), expected["log_confidence_range"])
    _assert_between(float(result.source_breakdown["logs_correction"]), expected["logs_correction_range"])
    assert bool(result.conflict_adjustment["detected"]) is bool(expected["conflict_detected"])
    assert str(result.conflict_adjustment["tier"]) == str(expected["conflict_tier"])

    if "conflict_delta_range" in expected:
        _assert_between(float(result.conflict_adjustment["delta"]), expected["conflict_delta_range"])
    if "reason_contains" in expected:
        assert str(expected["reason_contains"]) in str(result.conflict_adjustment["reason"])

