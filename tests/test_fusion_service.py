import pytest

from claude_usage_master.explain_copy import build_conflict_reason
from claude_usage_master.fusion_service import fuse_sources
from claude_usage_master.rating_engine import evaluate
from claude_usage_master.settings import clear_fusion_settings_cache


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> None:
    clear_fusion_settings_cache()
    yield
    clear_fusion_settings_cache()


def _base_result():
    dim_scores = {"D1": 70, "D2": 70, "D3": 85, "D4": 70, "D5": 70, "D6": 70}
    return evaluate(dim_scores), dim_scores


def test_fuse_sources_adds_conflict_metadata() -> None:
    result, dim_scores = _base_result()
    fused = fuse_sources(
        result=result,
        questionnaire_d3=dim_scores["D3"],
        sample_size=1,
        coverage_days=1,
    )

    assert "gap" in fused.conflict_adjustment
    assert "tier" in fused.conflict_adjustment
    assert fused.conflict_adjustment["policy"] == "anti_self_inflation"
    assert 0.0 <= float(fused.confidence["log_confidence"]) <= 1.0


def test_fuse_sources_without_logs_keeps_conflict_disabled() -> None:
    result, dim_scores = _base_result()
    fused = fuse_sources(
        result=result,
        questionnaire_d3=dim_scores["D3"],
        sample_size=0,
        coverage_days=0,
    )

    assert fused.conflict_adjustment["detected"] is False
    assert fused.conflict_adjustment["tier"] == "no_data"
    assert fused.source_breakdown["logs_correction"] == 0.0
    assert fused.conflict_adjustment["reason"] == build_conflict_reason("no_data")


def test_fuse_sources_can_disable_conflict_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUM_CONFLICT_ENABLED", "false")
    result, dim_scores = _base_result()
    fused = fuse_sources(
        result=result,
        questionnaire_d3=dim_scores["D3"],
        sample_size=30,
        coverage_days=14,
    )

    assert fused.conflict_adjustment["detected"] is False
    assert fused.conflict_adjustment["tier"] == "disabled"
    assert fused.conflict_adjustment["reason"] == build_conflict_reason("disabled")
