# Claude 使用熟练度评级系统 — 需求说明

## Context
本系统仅用于评估**开发者对 Claude 的使用熟练度**，不直接评估以下内容：
- 业务结果/岗位绩效
- 纯编程水平
- 团队协作产出

当前版本保留六维结构 `D1~D6` 与等级体系 `F / D / C / B / A / S / SS`，并在不推翻原框架的前提下统一规则一致性与融合策略。

---

## 一、评分架构总览（统一口径）

```
问卷原始答案
    ↓
六维度分数 [0-100]
    ↓ 加权求和
基础分 base_score [0-100]
    ↓ 规则加减分
修正分 adjusted_score [0-100]
    ↓ 天花板修正
最终分 final_score [0-100]
    ↓ × 10
1000 分制 scaled_score
    ↓ 等级映射
F / D / C / B / A / S / SS
```

### 评估边界
- 评估对象：开发者在真实任务中使用 Claude 的习惯、策略与集成深度。
- 非目标：业务价值评分、代码质量评分、组织绩效评分。
- 输入源职责：**问卷定基础、日志做校正、Hooks 做长期稳定性补充**。

---

## 二、六维度题目与评分细则

### D1：提示词工程（权重 25%，满分 100）

**计算方式：** `Q1~Q5`，每题 `0-5` 分，共 25 原始分，按比例映射到 100。

**D1 计算：** `D1_score = (Q1+Q2+Q3+Q4+Q5) / 25 * 100`

**题目口径（熟练度导向）**
- Q1：是否先定义 Claude 角色、任务目标、成功标准
- Q2：是否明确约束输出格式（JSON/表格/结构化 Markdown）
- Q3：是否使用 few-shot 示例提升稳定性
- Q4：是否设置限制与排除条件（不要做什么）
- Q5：首轮不理想时是否结构化重写 Prompt

**评分锚点（适用于 Q1~Q5）**
- `0`：基本不做或无意识
- `3`：部分场景会做，稳定性一般
- `5`：稳定执行并形成可复用方法

---

### D2：上下文管理（权重 15%，满分 100）

**计算方式：** `Q6~Q9`，每题 `0-5` 分，共 20 原始分，按比例映射到 100。

**D2 计算：** `D2_score = (Q6+Q7+Q8+Q9) / 20 * 100`

**题目口径（熟练度导向）**
- Q6：是否主动提供项目背景（技术栈/约束/上下游）
- Q7：长对话中是否做阶段总结与校准
- Q8：是否管理上下文长度（删冗余/提关键/分段推进）
- Q9：是否沉淀跨会话复用信息（Projects/系统提示/知识卡片）

**评分锚点（适用于 Q6~Q9）**
- `0`：基本不做
- `3`：偶尔做或仅复杂场景做
- `5`：有稳定策略并持续执行

---

### D3：工具与功能使用深度（权重 20%，满分 100）

> 说明：由“是否用过”改为“使用深度分层”，避免把浅尝误判为熟练。

#### Q10. 你在下列能力上的使用深度如何？（分项分层）

每个能力项按四档打分：
- `0 = 未用过`
- `1 = 试过（偶发）`
- `2 = 常用（任务中稳定使用）`
- `3 = 深度依赖（已融入固定工作流）`

| 能力项 | 权重基值 | 说明 |
|---|---:|---|
| 代码生成与调试 `code_gen` | 5 | 开发任务常规能力 |
| 文件分析 `file_analysis` | 8 | PDF/CSV/图片等 |
| Artifacts `artifacts` | 5 | 结构化可视化输出 |
| Projects + Memory `projects` | 10 | 持久上下文管理 |
| System Prompt `system_prompt` | 8 | 系统级提示管理 |
| Claude API `api` | 20 | 程序化调用 |
| Claude Code CLI `claude_code` | 20 | 工程内工作流整合 |
| MCP `mcp` | 25 | 外部工具生态扩展 |

分层系数：`{0: 0.0, 1: 0.35, 2: 0.7, 3: 1.0}`。

**D3 计算：**

`D3_score = min(100, sum(能力项权重基值 × 分层系数))`

---

### D4：任务拆解能力（权重 15%，满分 100）

**计算方式：** `Q11~Q14`，每题 `0-5` 分，共 20 原始分，按比例映射到 100。

**D4 计算：** `D4_score = (Q11+Q12+Q13+Q14) / 20 * 100`

**题目口径（熟练度导向）**
- Q11：复杂需求是否先拆解再执行
- Q12：是否分阶段推进（分析→方案→实现→验证）
- Q13：是否定义每一步验收标准
- Q14：是否管理依赖关系与优先级

**评分锚点（适用于 Q11~Q14）**
- `0`：无拆解与阶段意识
- `3`：有基础拆解，但不稳定
- `5`：系统拆解、阶段推进并可回查

---

### D5：迭代优化能力（权重 15%，满分 100）

**计算方式：** `Q15~Q18`，每题 `0-5` 分，共 20 原始分，按比例映射到 100。

**D5 计算：** `D5_score = (Q15+Q16+Q17+Q18) / 20 * 100`

**题目口径（熟练度导向）**
- Q15：是否进行事实与逻辑校验
- Q16：是否多轮优化并记录改动依据与效果
- Q17：是否提供纠错上下文进行高质量修复
- Q18：是否维护可复用 Prompt/工作流库

**评分锚点（适用于 Q15~Q18）**
- `0`：基本不迭代
- `3`：会迭代但缺少方法沉淀
- `5`：有闭环（校验-优化-复盘-复用）

---

### D6：工作流集成能力（权重 10%，满分 100）

> 说明：由“系统集成能力”收敛为“开发者日常工作流集成能力”。

**计算方式：** `Q19~Q22`，每题 `0-5` 分，共 20 原始分，按比例映射到 100。

#### D6 题意口径（用于问卷文案）
- Q19：Claude 在开发流程中的角色（临时辅助 -> 核心节点）
- Q20：自动化接入深度（手动 -> 脚本/API -> 流程化自动化）
- Q21：与工具链联动程度（IDE/Git/测试/文档等）
- Q22：能力边界认知与风险控制策略

**评分锚点（适用于 Q19~Q22）**
- `0`：孤立使用，基本无集成
- `3`：有部分集成与联动
- `5`：形成稳定工作流闭环并可扩展

---

## 三、完整评分算法（Python 口径草案）

```python
from dataclasses import dataclass

WEIGHTS = {
    "D1": 0.25,
    "D2": 0.15,
    "D3": 0.20,
    "D4": 0.15,
    "D5": 0.15,
    "D6": 0.10,  # 工作流集成能力
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

@dataclass
class RatingResult:
    # 核心分数
    base_score: float
    adjusted_score: float
    final_score: float
    scaled_score: int
    rating: str

    # 可解释输出
    dim_scores: dict
    bonus_detail: dict
    ceiling_detail: list
    source_breakdown: dict
    confidence: dict
    conflict_adjustment: dict
    suggestions: list[str]


def calc_D3(q: dict) -> float:
    # q["q10_depth"] 示例: {"api": 2, "claude_code": 3, ...}
    total = 0.0
    for feature, base in D3_BASE.items():
        level = int(q["q10_depth"].get(feature, 0))
        level = max(0, min(3, level))
        total += base * DEPTH_FACTOR[level]
    return min(100.0, total)


def calc_base_score(dim_scores: dict) -> float:
    return sum(dim_scores[d] * WEIGHTS[d] for d in WEIGHTS)


BONUS_RULES = [
    # (key, condition, delta, desc)
    ("api_regular",      lambda d: d["D3"] >= 55, +4, "工具使用深度达到 API/CLI 常用层"),
    ("workflow_balanced",lambda d: all(d[k] >= 60 for k in ["D1", "D4", "D5"]), +6, "核心三维均衡"),
    ("iteration_strong", lambda d: d["D5"] >= 80, +4, "迭代优化习惯优秀"),
    ("d6_strong",        lambda d: d["D6"] >= 80, +3, "工作流集成成熟"),
    ("weak_d1",          lambda d: d["D1"] < 20, -8, "提示词基础严重不足"),
    ("weak_d2",          lambda d: d["D2"] < 15, -4, "上下文管理缺失"),
    ("weak_d5",          lambda d: d["D5"] < 15, -5, "几乎不迭代优化"),
]


def calc_bonus(dim_scores: dict) -> tuple[float, dict]:
    total, detail = 0.0, {}
    for key, cond, delta, desc in BONUS_RULES:
        if cond(dim_scores):
            total += delta
            detail[key] = {"value": delta, "desc": desc}
    return total, detail


CEILING_RULES = [
    # 由重到轻，先命中更严格上限
    ("D1", 20, 45, "D1<20：提示词工程极弱，最高 C"),
    ("D4", 20, 60, "D4<20：任务拆解极弱，最高 B"),
    ("D1", 40, 65, "20<=D1<40：提示词基础薄弱，最高 A"),
    ("D2", 15, 70, "D2<15：上下文管理严重不足，最高 A"),
]


def apply_ceiling(score: float, dim_scores: dict) -> tuple[float, list]:
    applied = []
    capped = score
    for dim, threshold, cap, reason in CEILING_RULES:
        if dim_scores[dim] < threshold and capped > cap:
            capped = cap
            applied.append({
                "rule": f"{dim}<{threshold}",
                "cap": cap,
                "reason": reason,
            })
    return capped, applied


RATING_TIERS = [
    (95, "SS", "Claude 大师 — 可稳定构建 AI 驱动开发工作流"),
    (80, "S",  "Claude 专家 — 可设计并维护复杂自动化流程"),
    (65, "A",  "Claude 进阶 — 能熟练构建多步 prompt 链"),
    (45, "B",  "Claude 熟练 — 掌握核心技巧并形成流程意识"),
    (25, "C",  "Claude 入门 — 可完成常见任务但效率不稳定"),
    (10, "D",  "Claude 基础 — 以单轮问答为主"),
    (0,  "F",  "Claude 初接触 — 基础概念阶段"),
]


def score_to_rating(score: float) -> tuple[str, str]:
    # 无断档边界：>=95, >=80, ...
    for cutoff, grade, desc in RATING_TIERS:
        if score >= cutoff:
            return grade, desc
    return "F", "Claude 初接触"
```

---

## 四、规则一致性约束（必须同时满足）

- `BONUS_RULES` 不依赖模糊条件，不以“误代理指标”触发高分奖励。
- `CEILING_RULES` 命中时必须在结果中写明封顶原因与命中规则。
- `RATING_TIERS` 与 `score_to_rating` 采用同一边界定义（统一 `>= cutoff`）。
- 等级文案与封顶上限不冲突（例如“最高 C”不允许落到 B/A）。

---

## 五、可解释输出契约（必选字段）

评分结果至少包含以下字段：

```json
{
  "base_score": 62.4,
  "adjusted_score": 67.4,
  "final_score": 65.0,
  "scaled_score": 650,
  "rating": "A",
  "dim_scores": {"D1": 58, "D2": 70, "D3": 66, "D4": 60, "D5": 72, "D6": 55},
  "bonus_detail": {
    "workflow_balanced": {"value": 6, "desc": "核心三维均衡"},
    "weak_d1": {"value": -8, "desc": "提示词基础严重不足"}
  },
  "ceiling_detail": [
    {"rule": "D1<40", "cap": 65, "reason": "20<=D1<40：提示词基础薄弱，最高 A"}
  ],
  "source_breakdown": {
    "questionnaire": 65.0,
    "logs_correction": -1.5,
    "hooks_stability": 1.5
  },
  "confidence": {
    "log_confidence": 0.42,
    "sample_size": 18,
    "coverage_days": 9
  },
  "conflict_adjustment": {
    "detected": true,
    "policy": "anti_self_inflation",
    "delta": -2.0,
    "reason": "问卷 D3 高估，日志工具深度不足"
  },
  "suggestions": [
    "[D1] 强化约束式 prompt 与 few-shot",
    "[D6] 把 Claude 固化到开发工作流节点"
  ]
}
```

---

## 六、三源融合策略（正式版）

### 6.1 职责分工

- **问卷（基础层）**：提供完整维度覆盖，是总分主干。
- **日志（校正层）**：用于修正自评偏差，默认仅做小幅调整。
- **Hooks（稳定性层）**：用于长期习惯奖励，不承担基础评分职责。

### 6.2 融合原则

- **原则 1：问卷定基础**
  - 没有问卷，不输出正式评级。
- **原则 2：日志弱修正（与置信度绑定）**
  - 样本不足时（如会话数 < 10）只允许弱修正。
- **原则 3：反自评膨胀**
  - 问卷高分与日志冲突时，优先下调可疑高分，不轻易上调。
- **原则 4：Hooks 只做长期补充**
  - Hooks 奖励占比低，避免短期行为刷分。

### 6.3 置信度与修正幅度建议

```python
def calc_log_confidence(session_count: int, coverage_days: int) -> float:
    # 简化方案：样本数量与覆盖天数共同决定置信度
    s = min(1.0, session_count / 30)
    d = min(1.0, coverage_days / 14)
    return round(0.6 * s + 0.4 * d, 2)


def log_correction_cap(confidence: float) -> float:
    if confidence < 0.3:
        return 2.0   # 极弱修正
    if confidence < 0.6:
        return 4.0   # 中等修正
    return 6.0       # 高置信修正上限
```

### 6.4 冲突处理（反自评膨胀）

```python
def apply_conflict_policy(questionnaire_score: float, log_score_proxy: float) -> float:
    # 仅演示原则：冲突时保守下调，不做激进上调
    gap = questionnaire_score - log_score_proxy
    if gap <= 8:
        return 0.0
    if gap <= 15:
        return -1.5
    return -3.0
```

---

## 七、验收标准（对齐 plan.md）

- 所有核心表述都指向“Claude 使用熟练度”，无业务绩效/编程水平混入。
- `D6` 已统一为“工作流集成能力”，题意与代码注释保持一致。
- `Q10` 已改为“未用过/试过/常用/深度依赖”的分层设计。
- `BONUS_RULES`、`CEILING_RULES`、`RATING_TIERS`、`score_to_rating` 无断档、无冲突。
- 三源融合明确“问卷定基础、日志做校正、Hooks 做长期稳定性补充”。
- 日志置信度与反自评膨胀策略已写入正式规则。
- 输出契约能解释分数来源、封顶原因、加减项与改进方向。

---

## 八、后续实现建议

1. 落地 `rating_engine.py`：实现统一规则与输出契约。
2. 落地 `log_analyzer.py`：先实现置信度与弱修正，不做复杂推断。
3. 落地 `hooks_tracker.py`：仅追踪长期稳定性指标。
4. 在前端展示中新增“封顶原因”和“冲突修正说明”卡片。
