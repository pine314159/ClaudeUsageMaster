# Claude 使用熟练度评级系统

评估开发者对 Claude 的使用熟练度，输出 `F / D / C / B / A / S / SS` 等级，并给出分项说明与改进建议。

**三源策略：问卷定基础、日志做校正、Hooks 做长期稳定性补充。**

---

## 安装

```bash
python -m pip install -e .[dev]
```

---

## 快速上手

### 1. 填写问卷

启动本地问卷服务：

```bash
rate serve --host 127.0.0.1 --port 8765
```

浏览器打开 `http://127.0.0.1:8765/`，填写 Q1~Q22 并提交，结果写入 `data/questionnaire.json`。

### 2. 运行评级

```bash
rate run --input data/questionnaire.json --logs data/logs --report reports/index.html
```

运行后生成：

| 文件 | 说明 |
|---|---|
| `data/rating_result.json` | 最新评级结果（含分项明细） |
| `data/ratings_history.json` | 历史评级记录 |
| `data/log_checkpoint.json` | 日志读取进度（增量） |
| `data/claude_scan_checkpoint.json` | Claude Code 日志扫描进度（增量） |
| `reports/index.html` | 本地静态 HTML 报告 |

### 3. 查看报告

直接用浏览器打开 `reports/index.html`，离线可用。

---

## Claude Code 日志自动扫描

`rate run` 在评分前会自动扫描本机 Claude Code 的使用日志（`~/.claude/projects/**/*.jsonl`），无需手动维护 `data/logs/` 目录。

**行为说明：**
- 只读取上次扫描后新增的行（增量），进度保存在 `data/claude_scan_checkpoint.json`
- 将用户发送消息的行为转换为 `session_start` / `prompt_submit` 事件，追加写入 `data/logs/events.jsonl`
- 日志数据越丰富（会话数多、覆盖天数长），评分的置信度与 Hooks 稳定性奖励越高

**跳过自动扫描：**

```bash
rate run --input data/questionnaire.json --logs data/logs --report reports/index.html --no-scan
```

**手动放置日志（可选）：**

也可直接向 `data/logs/` 目录追加 `.jsonl` 文件，每行格式：

```json
{"ts": "2026-03-11T09:00:00Z", "event": "session_start"}
{"ts": "2026-03-11T09:01:00Z", "event": "prompt_submit"}
```

---

## 融合策略配置

复制 `.env.example` 为 `.env`，通过环境变量调整融合阈值，无需修改代码：

```bash
cp .env.example .env
```

| 前缀 | 说明 |
|---|---|
| `CUM_LOG_CAP_*` | 日志修正幅度上限（按置信度分层） |
| `CUM_ASI_*` | 反自评膨胀冲突策略阈值与惩罚幅度 |
| `CUM_HOOKS_*` | Hooks 稳定性奖励门槛与上限 |

---

## CLI 参数一览

### `rate run`

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--input` | （必填） | 问卷 JSON 文件路径 |
| `--logs` | `data/logs` | 日志目录 |
| `--output` | `data/rating_result.json` | 评级结果输出路径 |
| `--history` | `data/ratings_history.json` | 历史记录路径 |
| `--report` | `reports/index.html` | HTML 报告路径 |
| `--checkpoint` | `data/log_checkpoint.json` | 日志读取进度文件 |
| `--scan-checkpoint` | `data/claude_scan_checkpoint.json` | Claude 日志扫描进度文件 |
| `--no-scan` | `False` | 跳过自动扫描 Claude Code 本地日志 |

### `rate serve`

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--host` | `127.0.0.1` | 绑定地址 |
| `--port` | `8765` | 绑定端口 |
| `--questionnaire` | `data/questionnaire.json` | 问卷结果写入路径 |
| `--page` | `reports/questionnaire.html` | 问卷页面路径 |

---

## 运行测试

```bash
pytest
```

---

## 文档

| 文件 | 说明 |
|---|---|
| `docs/architecture.md` | 架构设计、模块划分、数据契约、设计思路 |
| `docs/acceptance_checklist.md` | 规则一致性验收清单（含测试映射） |
| `plan.md` | 技术决策记录与阶段开发 Todo |
| `CHANGELOG.md` | 版本变更记录 |

---

## 当前版本（0.1.0）已知限制

- 日志深度仍使用活动代理信号（`sample_size` + `coverage_days`），未接入细粒度行为特征
- 融合策略配置以 `.env` 覆盖为主，暂无配置 UI
- 报告为单页静态 HTML，暂无历史趋势可视化
