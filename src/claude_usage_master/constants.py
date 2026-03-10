from .explain_copy import RATING_DESC_BY_GRADE, build_ceiling_reason

WEIGHTS = {
    "D1": 0.25,
    "D2": 0.15,
    "D3": 0.20,
    "D4": 0.15,
    "D5": 0.15,
    "D6": 0.10,
}

DEPTH_FACTOR = {0: 0.0, 1: 0.35, 2: 0.7, 3: 1.0}

D3_BASE = {
    "code_gen": 5,
    "file_analysis": 8,
    "artifacts": 5,
    "projects": 10,
    "system_prompt": 8,
    "api": 20,
    "claude_code": 20,
    "mcp": 25,
}

BONUS_RULES = [
    ("api_regular", lambda d: d["D3"] >= 55, +4, "工具使用深度达到 API/CLI 常用层"),
    ("workflow_balanced", lambda d: all(d[k] >= 60 for k in ["D1", "D4", "D5"]), +6, "核心三维均衡"),
    ("iteration_strong", lambda d: d["D5"] >= 80, +4, "迭代优化习惯优秀"),
    ("d6_strong", lambda d: d["D6"] >= 80, +3, "工作流集成成熟"),
    ("weak_d1", lambda d: d["D1"] < 20, -8, "提示词基础严重不足"),
    ("weak_d2", lambda d: d["D2"] < 15, -4, "上下文管理缺失"),
    ("weak_d5", lambda d: d["D5"] < 15, -5, "几乎不迭代优化"),
]

CEILING_RULES = [
    ("D1", 20, 45, build_ceiling_reason("D1<20", "提示词工程极弱", "C")),
    ("D4", 20, 60, build_ceiling_reason("D4<20", "任务拆解极弱", "B")),
    ("D1", 40, 65, build_ceiling_reason("20<=D1<40", "提示词基础薄弱", "A")),
    ("D2", 15, 70, build_ceiling_reason("D2<15", "上下文管理严重不足", "A")),
]

RATING_TIERS = [
    (95, "SS", RATING_DESC_BY_GRADE["SS"]),
    (80, "S", RATING_DESC_BY_GRADE["S"]),
    (65, "A", RATING_DESC_BY_GRADE["A"]),
    (45, "B", RATING_DESC_BY_GRADE["B"]),
    (25, "C", RATING_DESC_BY_GRADE["C"]),
    (10, "D", RATING_DESC_BY_GRADE["D"]),
    (0, "F", RATING_DESC_BY_GRADE["F"]),
]
