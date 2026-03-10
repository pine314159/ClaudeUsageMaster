from .settings import get_fusion_settings


def calc_hooks_stability(sample_size: int, coverage_days: int) -> float:
    """Small stability bonus derived from long-term usage consistency.

    The bonus is intentionally tiny and capped so it cannot override
    questionnaire baseline decisions.
    """
    cfg = get_fusion_settings()
    if not cfg.hooks_enabled:
        return 0.0

    if sample_size < cfg.hooks_min_sample_size or coverage_days < cfg.hooks_min_coverage_days:
        return 0.0

    session_score = min(1.0, max(0, sample_size) / cfg.hooks_session_norm)
    day_score = min(1.0, max(0, coverage_days) / cfg.hooks_day_norm)
    bonus = (cfg.hooks_session_weight * session_score + cfg.hooks_day_weight * day_score) * cfg.hooks_bonus_cap
    return round(min(cfg.hooks_bonus_cap, bonus), 2)
