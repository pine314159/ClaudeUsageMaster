from typing import Any

from pydantic import BaseModel, Field, field_validator

from .constants import D3_BASE


class QuestionnaireInput(BaseModel):
    q1: int = Field(ge=0, le=5)
    q2: int = Field(ge=0, le=5)
    q3: int = Field(ge=0, le=5)
    q4: int = Field(ge=0, le=5)
    q5: int = Field(ge=0, le=5)
    q6: int = Field(ge=0, le=5)
    q7: int = Field(ge=0, le=5)
    q8: int = Field(ge=0, le=5)
    q9: int = Field(ge=0, le=5)
    q10_depth: dict[str, int] = Field(default_factory=dict)
    q11: int = Field(ge=0, le=5)
    q12: int = Field(ge=0, le=5)
    q13: int = Field(ge=0, le=5)
    q14: int = Field(ge=0, le=5)
    q15: int = Field(ge=0, le=5)
    q16: int = Field(ge=0, le=5)
    q17: int = Field(ge=0, le=5)
    q18: int = Field(ge=0, le=5)
    q19: int = Field(ge=0, le=5)
    q20: int = Field(ge=0, le=5)
    q21: int = Field(ge=0, le=5)
    q22: int = Field(ge=0, le=5)

    @field_validator("q10_depth")
    @classmethod
    def validate_q10_depth(cls, value: dict[str, int]) -> dict[str, int]:
        for feature, level in value.items():
            if feature not in D3_BASE:
                raise ValueError(f"Unsupported q10 feature: {feature}")
            if level < 0 or level > 3:
                raise ValueError(f"Invalid depth level for {feature}: {level}")
        return value


class RatingResult(BaseModel):
    base_score: float
    adjusted_score: float
    final_score: float
    scaled_score: int
    rating: str
    rating_desc: str
    dim_scores: dict[str, float]
    bonus_detail: dict[str, Any]
    ceiling_detail: list[dict[str, Any]]
    source_breakdown: dict[str, float]
    confidence: dict[str, float | int]
    conflict_adjustment: dict[str, Any]
    suggestions: list[str]

