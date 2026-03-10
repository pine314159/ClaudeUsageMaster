import pytest

from claude_usage_master.hooks_tracker import calc_hooks_stability
from claude_usage_master.settings import clear_fusion_settings_cache


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> None:
    clear_fusion_settings_cache()
    yield
    clear_fusion_settings_cache()


def test_hooks_stability_requires_minimum_signal() -> None:
    assert calc_hooks_stability(sample_size=9, coverage_days=10) == 0.0
    assert calc_hooks_stability(sample_size=30, coverage_days=4) == 0.0


def test_hooks_stability_is_small_and_capped() -> None:
    mid = calc_hooks_stability(sample_size=20, coverage_days=10)
    high = calc_hooks_stability(sample_size=200, coverage_days=60)

    assert 0.0 < mid <= 1.5
    assert high == 1.5


def test_hooks_stability_respects_config_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CUM_HOOKS_MIN_SAMPLE_SIZE", "2")
    monkeypatch.setenv("CUM_HOOKS_MIN_COVERAGE_DAYS", "1")
    monkeypatch.setenv("CUM_HOOKS_BONUS_CAP", "1.0")

    assert calc_hooks_stability(sample_size=2, coverage_days=1) > 0.0
    assert calc_hooks_stability(sample_size=200, coverage_days=60) == 1.0
