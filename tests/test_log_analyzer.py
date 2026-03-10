import pytest

from claude_usage_master.log_analyzer import (
    calc_log_confidence,
    clamp_log_correction,
    compute_raw_log_correction,
    evaluate_conflict,
    log_correction_cap,
)
from claude_usage_master.settings import clear_fusion_settings_cache


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> None:
    clear_fusion_settings_cache()
    yield
    clear_fusion_settings_cache()


def test_log_confidence_boundaries() -> None:
    assert calc_log_confidence(0, 0) == 0.0
    assert calc_log_confidence(30, 14) == 1.0


def test_log_correction_cap_tiers() -> None:
    assert log_correction_cap(0.1) == 2.0
    assert log_correction_cap(0.4) == 4.0
    assert log_correction_cap(0.8) == 6.0


def test_clamp_log_correction_respects_cap() -> None:
    assert clamp_log_correction(9.0, 0.2) == 2.0
    assert clamp_log_correction(-9.0, 0.2) == -2.0


def test_compute_raw_log_correction_zero_logs_is_neutral() -> None:
    assert compute_raw_log_correction(0, 0) == 0.0


def test_evaluate_conflict_tiers() -> None:
    no_conflict = evaluate_conflict(70.0, 63.0, log_confidence=0.8)
    assert no_conflict["detected"] is False
    assert no_conflict["delta"] == 0.0
    assert no_conflict["tier"] == "none"

    mild = evaluate_conflict(70.0, 56.0, log_confidence=0.8)
    assert mild["detected"] is True
    assert mild["delta"] == -1.5
    assert mild["tier"] == "mild"

    strong = evaluate_conflict(70.0, 40.0, log_confidence=0.8)
    assert strong["detected"] is True
    assert strong["delta"] == -3.0
    assert strong["tier"] == "strong"


def test_evaluate_conflict_low_confidence_halves_penalty() -> None:
    decision = evaluate_conflict(80.0, 60.0, log_confidence=0.2)
    assert decision["detected"] is True
    assert decision["delta"] == -1.5
    assert "低置信度半幅执行" in str(decision["reason"])


def test_evaluate_conflict_threshold_boundaries() -> None:
    gap_8 = evaluate_conflict(68.0, 60.0, log_confidence=0.8)
    assert gap_8["detected"] is False
    assert gap_8["tier"] == "none"

    gap_15 = evaluate_conflict(75.0, 60.0, log_confidence=0.8)
    assert gap_15["detected"] is True
    assert gap_15["tier"] == "mild"
    assert gap_15["delta"] == -1.5


def test_evaluate_conflict_respects_config_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUM_ASI_MILD_GAP_THRESHOLD", "5")
    monkeypatch.setenv("CUM_ASI_STRONG_GAP_THRESHOLD", "10")
    monkeypatch.setenv("CUM_ASI_MILD_PENALTY", "-1")
    monkeypatch.setenv("CUM_ASI_STRONG_PENALTY", "-2")
    monkeypatch.setenv("CUM_ASI_LOW_CONF_THRESHOLD", "0.5")
    monkeypatch.setenv("CUM_ASI_LOW_CONF_SCALE", "0.25")

    mild = evaluate_conflict(70.0, 63.0, log_confidence=0.8)
    assert mild["detected"] is True
    assert mild["delta"] == -1.0

    strong_low_conf = evaluate_conflict(70.0, 55.0, log_confidence=0.2)
    assert strong_low_conf["tier"] == "strong"
    assert strong_low_conf["delta"] == -0.5


def test_log_cap_respects_config_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUM_LOG_CAP_LOW_CONF_THRESHOLD", "0.2")
    monkeypatch.setenv("CUM_LOG_CAP_MID_CONF_THRESHOLD", "0.5")
    monkeypatch.setenv("CUM_LOG_CAP_LOW", "1")
    monkeypatch.setenv("CUM_LOG_CAP_MID", "3")
    monkeypatch.setenv("CUM_LOG_CAP_HIGH", "5")

    assert log_correction_cap(0.1) == 1.0
    assert log_correction_cap(0.3) == 3.0
    assert log_correction_cap(0.8) == 5.0
