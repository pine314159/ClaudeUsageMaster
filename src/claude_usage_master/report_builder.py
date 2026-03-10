from pathlib import Path
import json

from .models import RatingResult


def _render_bonus_cards(result: RatingResult) -> str:
    if not result.bonus_detail:
        return '<div class="card muted">无加减分命中</div>'
    cards: list[str] = []
    for key, detail in result.bonus_detail.items():
        cards.append(
            (
                '<div class="card">'
                f'<h4>{key}</h4>'
                f'<p>变化: {detail.get("value", 0)}</p>'
                f'<p>{detail.get("desc", "")}</p>'
                '</div>'
            )
        )
    return "".join(cards)


def _render_ceiling_cards(result: RatingResult) -> str:
    if not result.ceiling_detail:
        return '<div class="card muted">未触发封顶规则</div>'
    cards: list[str] = []
    for item in result.ceiling_detail:
        cards.append(
            (
                '<div class="card">'
                f'<h4>{item.get("rule", "")}</h4>'
                f'<p>封顶: {item.get("cap", "")}</p>'
                f'<p>{item.get("reason", "")}</p>'
                '</div>'
            )
        )
    return "".join(cards)


def _render_source_breakdown_cards(result: RatingResult) -> str:
    parts = {
        "问卷基础": float(result.source_breakdown.get("questionnaire", 0.0)),
        "日志修正": float(result.source_breakdown.get("logs_correction", 0.0)),
        "Hooks稳定": float(result.source_breakdown.get("hooks_stability", 0.0)),
    }
    total = sum(abs(v) for v in parts.values())
    cards: list[str] = []
    for label, value in parts.items():
        pct = 0.0 if total == 0 else round(abs(value) / total * 100, 1)
        cards.append(
            (
                '<div class="card">'
                f'<h4>{label}</h4>'
                f'<p>分值: {value}</p>'
                f'<p>占比: {pct}%</p>'
                '</div>'
            )
        )
    return "".join(cards)


def render_html(result: RatingResult) -> str:
    rows = "".join(
        f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in result.dim_scores.items()
    )
    suggestions = "".join(f"<li>{item}</li>" for item in result.suggestions)
    bonus_cards = _render_bonus_cards(result)
    ceiling_cards = _render_ceiling_cards(result)
    source_cards = _render_source_breakdown_cards(result)
    dim_json = json.dumps(result.dim_scores, ensure_ascii=False)

    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\" />
  <title>Claude 使用熟练度报告</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif; margin: 24px; color: #1f2937; }}
    table {{ border-collapse: collapse; width: 420px; background: #fff; }}
    td, th {{ border: 1px solid #e5e7eb; padding: 8px; }}
    h2 {{ margin-top: 28px; }}
    .pill {{ display: inline-block; padding: 6px 12px; background: #eef4ff; border-radius: 8px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }}
    .card {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; background: #fff; }}
    .card h4 {{ margin: 0 0 8px 0; font-size: 14px; }}
    .card p {{ margin: 6px 0; font-size: 13px; }}
    .muted {{ color: #6b7280; }}
    .wrap {{ display: grid; grid-template-columns: 480px 1fr; gap: 24px; align-items: start; }}
    @media (max-width: 980px) {{ .wrap {{ grid-template-columns: 1fr; }} }}
    .box {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px; background: #fff; }}
    svg text {{ font-size: 12px; fill: #374151; }}
  </style>
</head>
<body>
  <h1>Claude 使用熟练度评级结果</h1>
  <p class=\"pill\">等级: {result.rating} ({result.rating_desc})</p>
  <p>基础分: <strong>{result.base_score}</strong> / 100</p>
  <p>最终分: <strong>{result.final_score}</strong> / 100</p>

  <div class=\"wrap\">
    <section class=\"box\">
      <h2>维度雷达图</h2>
      <svg id=\"radar\" width=\"440\" height=\"360\" viewBox=\"0 0 440 360\" role=\"img\" aria-label=\"维度雷达图\"></svg>
      <p class=\"muted\">显示 D1~D6 的相对强弱分布（0-100）。</p>
    </section>

    <section>
      <h2>维度分数</h2>
      <table>
        <tr><th>维度</th><th>分数</th></tr>
        {rows}
      </table>
    </section>
  </div>

  <h2>规则命中卡片</h2>
  <h3>加减分规则</h3>
  <div class=\"grid\">{bonus_cards}</div>

  <h3>封顶规则</h3>
  <div class=\"grid\">{ceiling_cards}</div>

  <h2>来源占比</h2>
  <div class=\"grid\">{source_cards}</div>

  <h2>冲突修正</h2>
  <div class="card">
    <p>是否检测冲突: {result.conflict_adjustment.get("detected", False)}</p>
    <p>策略: {result.conflict_adjustment.get("policy", "")}</p>
    <p>层级: {result.conflict_adjustment.get("tier", "")}</p>
    <p>差值(gap): {result.conflict_adjustment.get("gap", 0)}</p>
    <p>变化: {result.conflict_adjustment.get("delta", 0)}</p>
    <p>{result.conflict_adjustment.get("reason", "")}</p>
  </div>

  <h2>改进建议</h2>
  <ul>{suggestions}</ul>

  <script>
    const data = {dim_json};
    const labels = Object.keys(data);
    const values = labels.map((k) => data[k]);
    const svg = document.getElementById("radar");
    const cx = 190;
    const cy = 180;
    const radius = 130;
    const axis = labels.length;

    function point(index, scale) {{
      const angle = (-Math.PI / 2) + (index * 2 * Math.PI / axis);
      return {{
        x: cx + Math.cos(angle) * radius * scale,
        y: cy + Math.sin(angle) * radius * scale,
      }};
    }}

    function polygon(points, cls, fill, stroke) {{
      const p = points.map((pt) => `${{pt.x}},${{pt.y}}`).join(" ");
      return `<polygon class="${{cls}}" points="${{p}}" fill="${{fill}}" stroke="${{stroke}}"/>`;
    }}

    let html = "";
    [0.2, 0.4, 0.6, 0.8, 1.0].forEach((level) => {{
      const pts = labels.map((_, i) => point(i, level));
      html += polygon(pts, "grid", "none", "#e5e7eb");
    }});

    labels.forEach((label, i) => {{
      const p = point(i, 1);
      html += `<line x1="${{cx}}" y1="${{cy}}" x2="${{p.x}}" y2="${{p.y}}" stroke="#d1d5db"/>`;
      const lp = point(i, 1.13);
      html += `<text x="${{lp.x}}" y="${{lp.y}}" text-anchor="middle">${{label}}</text>`;
    }});

    const valuePts = values.map((v, i) => point(i, Math.max(0, Math.min(100, v)) / 100));
    html += polygon(valuePts, "value", "rgba(59,130,246,0.25)", "#2563eb");
    valuePts.forEach((p) => {{
      html += `<circle cx="${{p.x}}" cy="${{p.y}}" r="3" fill="#2563eb"/>`;
    }});

    svg.innerHTML = html;
  </script>
</body>
</html>
"""


def write_report(path: Path, result: RatingResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(result), encoding="utf-8")
