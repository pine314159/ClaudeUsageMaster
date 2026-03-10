from .explain_copy import build_conflict_reason
from .log_analyzer import (
    calc_log_confidence,
    calc_log_depth_proxy,
    clamp_log_correction,
    compute_raw_log_correction,
    evaluate_conflict,
)
from .models import RatingResult
from .rating_engine import apply_source_corrections


def fuse_sources(
    result: RatingResult,
    questionnaire_d3: float,
    sample_size: int,
    coverage_days: int,
    hooks_stability: float = 0.0,
) -> RatingResult:
    """Fuse questionnaire baseline with logs/Hooks and apply conflict policy."""
    log_confidence = calc_log_confidence(sample_size, coverage_days)
    raw_delta = compute_raw_log_correction(sample_size, coverage_days)
    log_proxy = calc_log_depth_proxy(sample_size, coverage_days)

    if sample_size > 0:
        conflict = evaluate_conflict(
            questionnaire_score=questionnaire_d3,
            log_score_proxy=log_proxy,
            log_confidence=log_confidence,
        )
    else:
        conflict = {
            "detected": False,
            "policy": "anti_self_inflation",
            "delta": 0.0,
            "reason": build_conflict_reason("no_data"),
            "gap": 0.0,
            "tier": "no_data",
            "questionnaire_score": round(questionnaire_d3, 2),
            "log_score_proxy": round(log_proxy, 2),
        }

    logs_correction = clamp_log_correction(raw_delta + float(conflict["delta"]), log_confidence)

    result.confidence["sample_size"] = sample_size
    result.confidence["coverage_days"] = coverage_days
    result.confidence["log_confidence"] = log_confidence

    result.source_breakdown["logs_correction"] = logs_correction
    result.source_breakdown["hooks_stability"] = round(hooks_stability, 2)

    result.conflict_adjustment.update(conflict)
    return apply_source_corrections(result)
