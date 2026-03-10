from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class FusionStrategySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="CUM_", extra="ignore")

    # Log correction cap tiers
    log_cap_low_conf_threshold: float = 0.3
    log_cap_mid_conf_threshold: float = 0.6
    log_cap_low: float = 2.0
    log_cap_mid: float = 4.0
    log_cap_high: float = 6.0

    # Anti-self-inflation policy
    conflict_enabled: bool = True
    asi_mild_gap_threshold: float = 8.0
    asi_strong_gap_threshold: float = 15.0
    asi_mild_penalty: float = -1.5
    asi_strong_penalty: float = -3.0
    asi_low_conf_threshold: float = 0.3
    asi_low_conf_scale: float = 0.5

    # Hooks stability bonus
    hooks_enabled: bool = True
    hooks_min_sample_size: int = 10
    hooks_min_coverage_days: int = 5
    hooks_session_norm: int = 60
    hooks_day_norm: int = 30
    hooks_session_weight: float = 0.4
    hooks_day_weight: float = 0.6
    hooks_bonus_cap: float = 1.5


@lru_cache(maxsize=1)
def get_fusion_settings() -> FusionStrategySettings:
    return FusionStrategySettings()


def clear_fusion_settings_cache() -> None:
    get_fusion_settings.cache_clear()

