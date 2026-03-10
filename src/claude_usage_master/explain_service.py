from .explain_copy import SUGGESTION_ALIGN_LOGS, SUGGESTION_FIX_CEILING
from .models import RatingResult
from .rating_engine import build_suggestions, score_to_rating


def _merge_suggestions(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            if item not in seen:
                merged.append(item)
                seen.add(item)
    return merged


def assemble_result(result: RatingResult) -> RatingResult:
    """Finalize explainable output fields for external consumers."""
    rating, rating_desc = score_to_rating(result.final_score)

    explain_suggestions = build_suggestions(result.dim_scores)
    if result.ceiling_detail:
        explain_suggestions.append(SUGGESTION_FIX_CEILING)

    if bool(result.conflict_adjustment.get("detected", False)):
        explain_suggestions.append(SUGGESTION_ALIGN_LOGS)

    result.rating = rating
    result.rating_desc = rating_desc
    result.suggestions = _merge_suggestions(explain_suggestions, result.suggestions)
    return result
