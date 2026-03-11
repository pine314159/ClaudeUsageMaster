# 架构设计

## 一、总体架构（分层设计）

```text
[输入采集层]
  - 问卷答案
  - 行为日志（data/logs/*.jsonl）
  - Claude Code 本地日志（~/.claude/projects/**/*.jsonl）
        |
        v
[标准化与校验层]
  - 字段校验
  - 维度映射
  - 数据质量检查
        |
        v
[评分核心层]
  - 维度计算(D1~D6)
  - 基础分(base_score)
  - 规则加减分(adjusted_score)
  - 天花板封顶(final_score)
  - 等级映射(rating)
        |
        v
[融合与校正层]
  - 日志置信度
  - 弱修正策略
  - 反自评膨胀冲突处理
  - Hooks 稳定性补充
        |
        v
[解释与输出层]
  - 分数来源拆解
  - 命中规则与封顶原因
  - 冲突修正说明
  - 改进建议
```

该架构是"主干稳定、侧向可扩展"的组织方式：评分主链保证一致性，日志/Hooks 作为可插拔增强层。

---

## 二、功能模块划分

### `questionnaire_adapter`
负责接收与标准化问卷输入。

- 输入：`Q1~Q22`、`Q10` 分层能力项
- 输出：标准化问卷数据结构（缺省补值、合法值范围）
- 关键职责：避免脏数据直接进入评分核心

### `dimension_scorer`
负责六维度分数计算。

- `D1` 提示词工程
- `D2` 上下文管理
- `D3` 工具与功能使用深度（分层系数）
- `D4` 任务拆解
- `D5` 迭代优化
- `D6` 工作流集成

输出 `dim_scores`（每维 0-100）。

### `rating_engine`
负责评分主链，保证口径统一。

- 按权重计算 `base_score`
- 应用 `BONUS_RULES` 得到 `adjusted_score`
- 应用 `CEILING_RULES` 得到 `final_score`
- 映射 `RATING_TIERS` 产出等级

输出核心评分结果并保留规则命中明细。

### `claude_log_scanner`
负责从 Claude Code 本地日志目录自动采集使用行为。

- 扫描 `~/.claude/projects/**/*.jsonl`
- 增量读取，避免重复处理（checkpoint：`data/claude_scan_checkpoint.json`）
- 将 `type=user` 消息转换为 `session_start` / `prompt_submit` 事件
- 输出追加至 `data/logs/events.jsonl`

### `log_ingestor`
负责从 `data/logs/*.jsonl` 增量读取，输出 `sample_size` 与 `coverage_days`。

checkpoint 保存在 `data/log_checkpoint.json`，与扫描 checkpoint 独立。

### `log_analyzer`
负责日志侧校正能力。

- 计算日志置信度（样本量 + 覆盖天数）
- 根据置信度限制修正幅度（弱修正）
- 生成 `logs_correction` 与可信度说明

### `hooks_tracker`
负责长期稳定性补充。

- 追踪长期使用习惯指标
- 仅提供小幅稳定性奖励（上限 +1.5 分）
- 不参与基础评分主干

输出 `hooks_stability` 增量与依据。

### `fusion_service`
负责三源融合与冲突处理。

- 合并问卷主干、日志修正、Hooks 补充
- 执行反自评膨胀策略（冲突时优先保守下调）
- 输出 `source_breakdown` 与 `conflict_adjustment`

### `explain_service`
负责可解释输出组装。

- 汇总规则命中、封顶原因、修正原因
- 生成针对维度短板的改进建议
- 输出符合契约的 `RatingResult`

---

## 三、核心数据流

```text
问卷输入
  -> questionnaire_adapter
  -> dimension_scorer
  -> rating_engine (base -> adjusted -> final -> rating)

Claude Code 本地日志
  -> claude_log_scanner (增量扫描, 写入 data/logs/events.jsonl)

data/logs/*.jsonl
  -> log_ingestor (confidence + correction)

Hooks 输入
  -> hooks_tracker (stability)

主链结果 + 两侧补充
  -> fusion_service (含冲突策略)
  -> explain_service
  -> 最终评级结果(JSON + HTML)
```

无问卷时不输出正式评级；日志与 Hooks 只对主链做有限校正与补充。

---

## 四、输出数据契约

最终输出至少包含以下字段：

```json
{
  "base_score": 62.4,
  "adjusted_score": 67.4,
  "final_score": 65.0,
  "scaled_score": 650,
  "rating": "A",
  "dim_scores": {"D1": 58, "D2": 70, "D3": 66, "D4": 60, "D5": 72, "D6": 55},
  "bonus_detail": {},
  "ceiling_detail": [],
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
    "tier": "mild",
    "gap": 12.0,
    "delta": -1.5,
    "reason": "问卷D3高于日志代理，保守下调"
  },
  "suggestions": [
    "[D1] 强化约束式 prompt 与 few-shot",
    "[D6] 把 Claude 固化到开发工作流节点"
  ]
}
```

---

## 五、设计思路

### 先稳定评分主链，再引入侧向校正
核心任务是口径统一与可解释性，因此把问卷评分链路作为唯一主干，避免被外部噪声破坏一致性。

### 分层解耦，便于独立迭代
日志、Hooks、解释输出都通过独立模块接入，不和评分计算强耦合，后续可单独优化而不重写主链。

### 把"冲突处理"显式化
将反自评膨胀策略写成独立能力而不是隐式规则，便于审计和复盘，减少"看不懂分数变化"的风险。

### 以数据契约驱动实现
先定义输出字段和解释要求，再反推模块输入输出，保证前后端和算法逻辑能并行开发。

---

## 六、非目标声明

本系统不输出以下结论：

- 业务价值评分
- 代码能力评分
- 团队绩效评分

系统输出仅表示用户对 Claude 的使用熟练度等级。
