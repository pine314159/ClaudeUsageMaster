# Claude 使用熟练度评级系统 - 架构开发 ToDo

## 执行说明

- 目标：按 `README.md` 的架构分层推进，实现可解释、可复现、可验收的评级流水线。
- 原则：先稳定评分主链，再引入日志/Hooks 校正，最后完善解释输出与验收发布。

## 技术栈决定

### 已确认技术决策（冻结）

- `storage_format`: **全 JSON**（输入、输出、历史、checkpoint）
- `log_input_mode`: **B**（读取本地目录增量）
- `interaction_entry`: **B**（`Typer` CLI + 本地静态页面报告）

- **语言与运行时**：`Python 3.12`
  - 原因：适合规则引擎与数据处理，开发速度快，和当前文档中的 Python 评分草案一致。

- **交互入口**：`Typer`（CLI）+ 本地静态报告生成器
  - 原因：贴合个人自评场景，不需要后端服务，支持一键生成可分享的本地报告。

- **数据模型与校验**：`Pydantic v2`
  - 原因：可直接定义 `RatingResult` 契约与输入校验规则，字段约束清晰且可生成 Schema。

- **配置管理**：`pydantic-settings` + `.env`
  - 原因：阈值、修正上限、开关配置化，避免硬编码，便于 P1 调参。

- **日志处理与可观测性**：`structlog` + 标准 `logging`
  - 原因：结构化日志便于审计 `source_breakdown`、`conflict_adjustment` 与规则命中。

- **测试框架**：`pytest` + `pytest-cov`
  - 原因：适合规则边界和参数化用例，覆盖主链、冲突修正、封顶与等级映射。

- **代码质量**：`ruff`（lint+format）+ `mypy`（静态类型）
  - 原因：单工具链低维护成本；类型检查减少规则实现歧义。

- **打包与依赖**：`uv`（依赖与运行）+ `pyproject.toml`
  - 原因：安装与锁定速度快，单仓开发体验好。

- **本地数据文件约定（JSON）**：
  - `data/questionnaire.json`：问卷原始输入
  - `data/logs/*.jsonl`：行为日志目录（增量读取）
  - `data/log_checkpoint.json`：日志读取进度
  - `data/rating_result.json`：最近一次评级结果
  - `data/ratings_history.json`：历史评级记录

### 备选方案与切换条件（当前不启用）

- **持久化备选**：若后续需要更强查询能力，可升级 `SQLite`；多人并发再升 `PostgreSQL`。
- **任务调度备选**：当前使用 `cron/CI` 即可；若需要复杂编排再引入 `Celery`。

---

## 阶段一：基础主链（P0）

- [x] **[P0 | 1天] 定义核心数据契约与常量**
  - 交付物：`RatingResult` 字段表、`WEIGHTS`、`RATING_TIERS`、规则边界说明
  - 验收标准：字段和边界与 `README.md` 完全一致；无歧义命名

- [x] **[P0 | 1天] 实现问卷标准化与输入校验（`questionnaire_adapter`）**
  - 交付物：Q1~Q22 与 Q10 分层值校验逻辑
  - 验收标准：缺省、越界、非法类型均有确定处理策略

- [x] **[P0 | 1天] 实现六维计算（`dimension_scorer`）**
  - 交付物：`D1~D6` 计算函数（含 `calc_D3` 分层系数）
  - 验收标准：维度分值稳定落在 0~100，D3 封顶行为可复现

- [x] **[P0 | 1天] 实现评分主链（`rating_engine`）**
  - 交付物：`base_score -> adjusted_score -> final_score -> rating`
  - 验收标准：`BONUS_RULES`、`CEILING_RULES`、等级映射一致且可重复

---

## 阶段二：校正融合（日志/Hooks）

- [x] **[P0 | 1天] 实现日志置信度与弱修正（`log_analyzer`）**
  - 交付物：`log_confidence` 与修正幅度上限逻辑
  - 验收标准：样本不足仅弱修正；可追溯 `sample_size` 和 `coverage_days`

- [x] **[P1 | 半天] 实现 Hooks 长期稳定性补充（`hooks_tracker`）**
  - 交付物：稳定性奖励计算逻辑
  - 验收标准：仅小幅增量，不改写问卷主链基础评分

- [x] **[P0 | 1天] 实现三源融合与冲突策略（`fusion_service`）**
  - 交付物：`source_breakdown`、`conflict_adjustment` 输出
  - 验收标准：冲突可触发 `anti_self_inflation` 保守下调，结果可解释

- [x] **[P1 | 半天] 融合策略配置化（阈值/上限/开关）**
  - 交付物：策略配置及说明文档
  - 验收标准：关键阈值调整不需要改核心代码

- [x] **[P0 | 半天] 实现本地目录增量读取（`log_ingestor`）**
  - 交付物：按文件偏移/时间戳读取 `data/logs/*.jsonl`，并写入 `data/log_checkpoint.json`
  - 验收标准：重复执行不重复计入同一日志；新增日志可被稳定识别

---

## 阶段三：解释输出

- [x] **[P0 | 1天] 实现可解释结果组装（`explain_service`）**
  - 交付物：完整 `RatingResult` 输出组装
  - 验收标准：`bonus_detail`、`ceiling_detail`、`suggestions` 字段完整

- [x] **[P1 | 半天] 统一解释文案规范**
  - 交付物：等级描述、封顶原因、冲突说明模板
  - 验收标准：同类场景文案一致，无“分数变化无法解释”情况

- [x] **[P1 | 1天] 建立典型样例库（fixtures）**
  - 交付物：高分/中位/冲突/低置信度输入样例
  - 验收标准：覆盖主链、封顶、冲突、弱修正、建议生成关键路径

- [x] **[P0 | 半天] 生成本地静态报告（`report_builder`）**
  - 交付物：`reports/index.html`（读取 `rating_result.json` 渲染）
  - 验收标准：离线可打开，展示等级、分数来源、封顶原因、改进建议

---

## 阶段四：验收与发布

- [x] **[P0 | 1天] 建立规则一致性验收清单**
  - 交付物：边界、封顶、等级映射一致性清单
  - 验收标准：无等级断档、无“最高等级限制”冲突

- [x] **[P0 | 1天] 端到端验收与回归测试**
  - 交付物：E2E 用例与验收记录
  - 验收标准：关键场景通过；输出契约字段类型正确

- [x] **[P1 | 半天] 发布说明与版本记录**
  - 交付物：`README.md` 发布说明、`CHANGELOG.md`
  - 验收标准：明确边界、输入源职责、已知限制和下一步方向

- [ ] **[P2 | 半天] 规划后续 Backlog**
  - 交付物：后续待办列表
  - 验收标准：演进项不影响主链稳定性

- [x] **[P1 | 半天] 提供 CLI 一键入口**
  - 交付物：`rate run --input data/questionnaire.json --logs data/logs --report reports/`
  - 验收标准：单命令完成评分、融合、输出 JSON 和静态报告

---

## 优先执行顺序（建议）

1. 阶段一全部完成（主链先稳定）
2. 阶段二先做 `log_ingestor`、`log_analyzer` 和 `fusion_service`
3. 阶段三完成解释输出并生成本地静态报告
4. 阶段四执行验收、回归与 CLI 一键发布流程
