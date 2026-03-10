RATING_DESC_BY_GRADE = {
    "SS": "Claude 大师",
    "S": "Claude 专家",
    "A": "Claude 进阶",
    "B": "Claude 熟练",
    "C": "Claude 入门",
    "D": "Claude 基础",
    "F": "Claude 初接触",
}


def build_ceiling_reason(rule: str, weakness: str, max_grade: str) -> str:
    return f"{rule}: {weakness}，最高 {max_grade}"


def build_conflict_reason(kind: str, low_confidence: bool = False) -> str:
    reasons = {
        "disabled": "冲突策略已关闭",
        "none": "问卷与日志未出现显著冲突",
        "mild": "问卷 D3 高于日志代理，执行保守下调",
        "strong": "问卷 D3 显著高于日志代理，执行反自评膨胀下调",
        "no_data": "日志样本不足，未启用冲突下调",
        "init": "日志冲突修正未启用",
    }
    reason = reasons[kind]
    if low_confidence:
        reason = f"{reason}（低置信度半幅执行）"
    return reason


SUGGESTION_FIX_CEILING = "优先补齐封顶相关短板，解除等级上限"
SUGGESTION_ALIGN_LOGS = "对齐问卷自评与实际日志行为，降低冲突下调风险"

