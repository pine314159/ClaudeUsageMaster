from .explain_copy import build_conflict_reason
from .settings import get_fusion_settings


def calc_log_confidence(session_count: int, coverage_days: int) -> float:
    """Confidence from sample size and day coverage.

    Uses 0.6 * sessions + 0.4 * days with normalized inputs.
    """
    s = min(1.0, max(0, session_count) / 30)
    d = min(1.0, max(0, coverage_days) / 14)
    return round(0.6 * s + 0.4 * d, 2)


def log_correction_cap(confidence: float) -> float:
    cfg = get_fusion_settings()
    if confidence < cfg.log_cap_low_conf_threshold:
        return cfg.log_cap_low
    if confidence < cfg.log_cap_mid_conf_threshold:
        return cfg.log_cap_mid
    return cfg.log_cap_high


def compute_raw_log_correction(session_count: int, coverage_days: int) -> float:
    """Conservative correction proxy.

    With no logs, keep neutral correction. Otherwise derive a small signed
    correction from volume/coverage signal and let cap control final amplitude.
    """
    if session_count <= 0:
        return 0.0

    activity = min(1.0, session_count / 30)
    coverage = min(1.0, coverage_days / 14)
    signal = 0.7 * activity + 0.3 * coverage
    return round((signal - 0.5) * 6, 2)


def clamp_log_correction(raw_delta: float, confidence: float) -> float:
    cap = log_correction_cap(confidence)
    return round(max(-cap, min(cap, raw_delta)), 2)


def calc_log_depth_proxy(session_count: int, coverage_days: int) -> float:
    """Approximate D3-like usage depth from local activity signals."""
    activity = min(1.0, max(0, session_count) / 30)
    coverage = min(1.0, max(0, coverage_days) / 14)
    return round((0.7 * activity + 0.3 * coverage) * 100, 2)


def evaluate_conflict(
    questionnaire_score: float,
    log_score_proxy: float,
    log_confidence: float,
) -> dict[str, bool | float | str]:
    """Structured anti-self-inflation decision used by fusion layer."""
    cfg = get_fusion_settings()
    gap = round(questionnaire_score - log_score_proxy, 2)

    if not cfg.conflict_enabled:
        return {
            "detected": False,
            "policy": "anti_self_inflation",
            "delta": 0.0,
            "reason": build_conflict_reason("disabled"),
            "gap": gap,
            "tier": "disabled",
            "questionnaire_score": round(questionnaire_score, 2),
            "log_score_proxy": round(log_score_proxy, 2),
        }

    mild_gap = cfg.asi_mild_gap_threshold
    strong_gap = cfg.asi_strong_gap_threshold
    mild_penalty = cfg.asi_mild_penalty
    strong_penalty = cfg.asi_strong_penalty
    low_conf_threshold = cfg.asi_low_conf_threshold
    low_conf_scale = cfg.asi_low_conf_scale

    if gap <= mild_gap:
        return {
            "detected": False,
            "policy": "anti_self_inflation",
            "delta": 0.0,
            "reason": build_conflict_reason("none"),
            "gap": gap,
            "tier": "none",
            "questionnaire_score": round(questionnaire_score, 2),
            "log_score_proxy": round(log_score_proxy, 2),
        }

    if gap <= strong_gap:
        tier = "mild"
        delta = mild_penalty
        reason = build_conflict_reason("mild")
    else:
        tier = "strong"
        delta = strong_penalty
        reason = build_conflict_reason("strong")

    if log_confidence < low_conf_threshold:
        # Low-confidence logs still influence score, but only with reduced intensity.
        delta = round(delta * low_conf_scale, 2)
        reason = build_conflict_reason(tier, low_confidence=True)

    return {
        "detected": True,
        "policy": "anti_self_inflation",
        "delta": delta,
        "reason": reason,
        "gap": gap,
        "tier": tier,
        "questionnaire_score": round(questionnaire_score, 2),
        "log_score_proxy": round(log_score_proxy, 2),
    }


def apply_conflict_policy(questionnaire_score: float, log_score_proxy: float) -> tuple[bool, float, str]:
    """Backward-compatible tuple API used by existing callers/tests."""
    decision = evaluate_conflict(questionnaire_score, log_score_proxy, log_confidence=1.0)
    return bool(decision["detected"]), float(decision["delta"]), str(decision["reason"])
