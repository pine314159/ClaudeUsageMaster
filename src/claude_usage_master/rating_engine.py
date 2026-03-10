from .constants import BONUS_RULES, CEILING_RULES, RATING_TIERS, WEIGHTS
from .explain_copy import RATING_DESC_BY_GRADE, build_conflict_reason
from .models import RatingResult


def calc_base_score(dim_scores: dict[str, float]) -> float:
    return round(sum(dim_scores[d] * WEIGHTS[d] for d in WEIGHTS), 2)


def calc_bonus(dim_scores: dict[str, float]) -> tuple[float, dict[str, dict[str, float | str]]]:
    total = 0.0
    detail: dict[str, dict[str, float | str]] = {}
    for key, cond, delta, desc in BONUS_RULES:
        if cond(dim_scores):
            total += delta
            detail[key] = {"value": float(delta), "desc": desc}
    return total, detail


def apply_ceiling(score: float, dim_scores: dict[str, float]) -> tuple[float, list[dict[str, float | str]]]:
    capped = score
    applied: list[dict[str, float | str]] = []
    for dim, threshold, cap, reason in CEILING_RULES:
        if dim_scores[dim] < threshold and capped > cap:
            capped = float(cap)
            applied.append({"rule": f"{dim}<{threshold}", "cap": float(cap), "reason": reason})
    return capped, applied


def score_to_rating(score: float) -> tuple[str, str]:
    for cutoff, grade, desc in RATING_TIERS:
        if score >= cutoff:
            return grade, desc
    return "F", RATING_DESC_BY_GRADE["F"]


def build_suggestions(dim_scores: dict[str, float]) -> list[str]:
    labels = {
        "D1": "提示词工程",
        "D2": "上下文管理",
        "D3": "工具使用深度",
        "D4": "任务拆解",
        "D5": "迭代优化",
        "D6": "工作流集成",
    }
    weak_dims = sorted(dim_scores.items(), key=lambda x: x[1])[:2]
    suggestions: list[str] = []
    for dim, score in weak_dims:
        if score < 60:
            suggestions.append(f"[{dim}] 优先提升{labels[dim]}能力")
    if not suggestions:
        suggestions.append("保持当前使用习惯，逐步提升自动化与稳定性")
    return suggestions


def apply_source_corrections(result: RatingResult) -> RatingResult:
    delta = result.source_breakdown.get("logs_correction", 0.0) + result.source_breakdown.get(
        "hooks_stability", 0.0
    )
    corrected = max(0.0, min(100.0, round(result.final_score + delta, 2)))
    grade, desc = score_to_rating(corrected)
    result.final_score = corrected
    result.scaled_score = int(round(corrected * 10))
    result.rating = grade
    result.rating_desc = desc
    return result


def evaluate(dim_scores: dict[str, float]) -> RatingResult:
    base_score = calc_base_score(dim_scores)
    bonus_delta, bonus_detail = calc_bonus(dim_scores)
    adjusted_score = max(0.0, min(100.0, round(base_score + bonus_delta, 2)))
    final_score, ceiling_detail = apply_ceiling(adjusted_score, dim_scores)
    final_score = round(final_score, 2)
    rating, rating_desc = score_to_rating(final_score)

    result = RatingResult(
        base_score=base_score,
        adjusted_score=adjusted_score,
        final_score=final_score,
        scaled_score=int(round(final_score * 10)),
        rating=rating,
        rating_desc=rating_desc,
        dim_scores=dim_scores,
        bonus_detail=bonus_detail,
        ceiling_detail=ceiling_detail,
        source_breakdown={
            "questionnaire": base_score,
            "logs_correction": 0.0,
            "hooks_stability": 0.0,
        },
        confidence={
            "log_confidence": 0.0,
            "sample_size": 0,
            "coverage_days": 0,
        },
        conflict_adjustment={
            "detected": False,
            "policy": "anti_self_inflation",
            "delta": 0.0,
            "reason": build_conflict_reason("init"),
        },
        suggestions=build_suggestions(dim_scores),
    )
    return apply_source_corrections(result)
