from .constants import D3_BASE, DEPTH_FACTOR
from .models import QuestionnaireInput


def calc_d3(q10_depth: dict[str, int]) -> float:
    total = 0.0
    for feature, base in D3_BASE.items():
        level = int(q10_depth.get(feature, 0))
        level = max(0, min(3, level))
        total += base * DEPTH_FACTOR[level]
    return min(100.0, total)


def score_dimensions(q: QuestionnaireInput) -> dict[str, float]:
    d1 = (q.q1 + q.q2 + q.q3 + q.q4 + q.q5) / 25 * 100
    d2 = (q.q6 + q.q7 + q.q8 + q.q9) / 20 * 100
    d3 = calc_d3(q.q10_depth)
    d4 = (q.q11 + q.q12 + q.q13 + q.q14) / 20 * 100
    d5 = (q.q15 + q.q16 + q.q17 + q.q18) / 20 * 100
    d6 = (q.q19 + q.q20 + q.q21 + q.q22) / 20 * 100
    return {
        "D1": round(d1, 2),
        "D2": round(d2, 2),
        "D3": round(d3, 2),
        "D4": round(d4, 2),
        "D5": round(d5, 2),
        "D6": round(d6, 2),
    }

