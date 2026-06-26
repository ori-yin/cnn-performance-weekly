"""
export.py - 导出看板为独立 HTML 文件
"""

import base64
import json
from pathlib import Path
from datetime import date

import plotly.graph_objects as go

from components import _fmt_number


def _get_css() -> str:
    """导出用的 CSS（暖色纸质主题）"""
    return """
<style>
  :root {
    --mcd-red: #DA291C;
    --mcd-dark: #a8001a;
    --mcd-gold: #FFC72C;
    --ink: #2b2620;
    --ink2: #5a5048;
    --line: #e4d9bf;
    --bg: #f4efe6;
    --paper: #fffdf8;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, sans-serif;
    background: var(--bg);
    color: var(--ink);
    font-size: 13.5px;
    line-height: 1.7;
  }
  a { color: inherit; text-decoration: none; }

  /* ─── 顶部栏 ─── */
  .topbar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: linear-gradient(135deg, #DB0007, #a8001a);
    border-bottom: 3px solid var(--mcd-gold);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 26px;
    box-shadow: 0 2px 14px rgba(0,0,0,.18);
  }
  .topbar-left { display: flex; align-items: center; gap: 14px; }
  .topbar-logo { height: 40px; width: auto; }
  .topbar-title h1 { font-size: 17px; font-weight: 800; color: #fff; letter-spacing: .3px; }
  .topbar-title .sub { font-size: 11px; color: rgba(255,255,255,.85); margin-top: 1px; }
  .topbar-right { text-align: right; color: rgba(255,255,255,.92); font-size: 10.5px; line-height: 1.6; }
  .topbar-badge {
    display: inline-block;
    background: var(--mcd-gold);
    color: #5a1a00;
    font-weight: 800;
    font-size: 10.5px;
    padding: 2px 11px;
    border-radius: 20px;
    margin-bottom: 3px;
  }

  /* ─── 导航栏 ─── */
  .nav-bar {
    position: sticky;
    top: 57px;
    z-index: 90;
    background: rgba(255,253,248,.96);
    backdrop-filter: blur(6px);
    border-bottom: 1px solid var(--line);
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 8px 20px;
  }
  .nav-link {
    font-size: 11.5px;
    font-weight: 700;
    color: var(--ink2);
    padding: 4px 11px;
    border-radius: 16px;
    text-decoration: none;
    transition: .15s;
    white-space: nowrap;
  }
  .nav-link:hover { background: #fde9ea; color: var(--mcd-red); }

  /* ─── 内容区 ─── */
  .wrap { max-width: 1160px; margin: 0 auto; padding: 26px 24px 60px; }
  section {
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 22px;
    box-shadow: 0 1px 3px rgba(120,90,30,.05);
  }
  .sec-head { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
  .sec-num {
    background: var(--mcd-red);
    color: #fff;
    font-weight: 800;
    font-size: 15px;
    min-width: 34px;
    height: 34px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .sec-head h2 { font-size: 19px; font-weight: 800; color: var(--mcd-dark); letter-spacing: .3px; }

  /* ─── KPI 卡片 ─── */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin: 12px 0;
  }
  .kpi-card {
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(120,90,30,.05);
  }
  .kpi-card::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: var(--mcd-red);
  }
  .kpi-card.green::before { background: #5a8a50; }
  .kpi-card.yellow::before { background: var(--mcd-gold); }
  .kpi-card.red::before { background: var(--mcd-red); }
  .kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--ink2);
    margin-bottom: 6px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }
  .kpi-value {
    font-size: 26px;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
  }
  .kpi-sub { font-size: 12px; color: var(--ink2); }

  /* ─── 表格 ─── */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 16px;
    background: #fff;
    border-radius: 9px;
    overflow: hidden;
    font-size: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,.04);
  }
  th {
    background: var(--mcd-dark);
    color: #fff;
    padding: 9px 11px;
    text-align: left;
    font-weight: 700;
    font-size: 11.5px;
  }
  td { padding: 8px 11px; border-bottom: 1px solid #f0e8d6; vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tr:nth-child(even) td { background: #fcfaf3; }

  /* ─── 子标题 ─── */
  .section-subheader {
    font-size: 14px;
    font-weight: 600;
    color: var(--ink2);
    margin: 14px 0 8px 0;
    letter-spacing: 0.02em;
  }

  /* ─── Plotly 图表 ─── */
  .plotly-graph-div {
    width: 100% !important;
    min-height: 300px;
  }

  /* ─── 锚点跳转偏移（补偿固定 header 高度）─── */
  [id^="sec-"] {
    scroll-margin-top: 110px;
  }

  /* ─── 分隔线 ─── */
  .divider {
    border: none;
    border-top: 1px solid var(--line);
    margin: 28px 0;
  }

  /* ─── Plan 卡片 ─── */
  .plan-card {
    background: #fff;
    border: 1px solid #E8E8E8;
    border-left: 3px solid var(--mcd-red);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
  }
  .plan-card.good { border-left-color: #5a8a50; }
  .plan-card .plan-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .plan-card .plan-tag {
    font-size: 11px;
    font-weight: 600;
  }
  .plan-card .plan-tag.good { color: #5a8a50; }
  .plan-card .plan-tag.bad { color: var(--mcd-red); }
  .plan-card .plan-score {
    font-size: 18px;
    font-weight: 800;
  }
  .plan-card .plan-name {
    font-size: 13px;
    font-weight: 600;
    margin: 6px 0 2px;
  }
  .plan-card .plan-metrics {
    font-size: 12px;
    color: #666;
  }
  .plan-card .plan-msg {
    margin-top: 8px;
    padding: 8px 10px;
    background: #FAFAFA;
    border-radius: 6px;
    border-left: 2px solid #E0E0E0;
    font-size: 12px;
    line-height: 1.5;
  }
  .plan-card .plan-msg-title {
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 2px;
  }
  .plan-card .plan-msg-text { color: #666; }

  /* ─── Plan Tab 切换（纯 CSS，支持双层嵌套）─── */
  .plan-ch-tabs, .plan-dim-tabs { margin-bottom: 16px; }
  .plan-ch-input, .plan-dim-input { display: none; }
  .plan-tab-label {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    color: var(--ink2);
    padding: 5px 14px;
    border-radius: 16px;
    cursor: pointer;
    transition: .15s;
    margin-right: 4px;
    margin-bottom: 4px;
  }
  .plan-tab-label:hover { background: #fde9ea; color: var(--mcd-red); }
  .plan-ch-input:checked + .plan-tab-label,
  .plan-dim-input:checked + .plan-tab-label {
    background: var(--mcd-red);
    color: #fff;
  }
  .plan-ch-panel, .plan-dim-panel { display: none; }
  /* 渠道：第N个radio checked → 第N个panel显示 */
  .plan-ch-input:nth-of-type(1):checked ~ .plan-ch-panel:nth-of-type(1),
  .plan-ch-input:nth-of-type(2):checked ~ .plan-ch-panel:nth-of-type(2),
  .plan-ch-input:nth-of-type(3):checked ~ .plan-ch-panel:nth-of-type(3),
  .plan-ch-input:nth-of-type(4):checked ~ .plan-ch-panel:nth-of-type(4) { display: block; }
  /* 维度：同理 */
  .plan-dim-input:nth-of-type(1):checked ~ .plan-dim-panel:nth-of-type(1),
  .plan-dim-input:nth-of-type(2):checked ~ .plan-dim-panel:nth-of-type(2),
  .plan-dim-input:nth-of-type(3):checked ~ .plan-dim-panel:nth-of-type(3) { display: block; }

  /* ─── AI 折叠 ─── */
  details { margin-top: 8px; }
  details summary {
    font-size: 12px;
    font-weight: 600;
    color: var(--mcd-dark);
    cursor: pointer;
    padding: 4px 0;
  }
  details summary:hover { color: var(--mcd-red); }
  details[open] summary { margin-bottom: 4px; }

  /* ─── Plan 药丸豆腐块 ─── */
  .plan-metrics { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
  .plan-metric-tag {
    background: #F8F7F5;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    color: #888;
    font-weight: 500;
  }

  /* ─── 页脚 ─── */
  .footer {
    text-align: center;
    color: #9a8a68;
    font-size: 11px;
    padding: 20px;
  }
</style>
"""


def _get_logo_base64() -> str:
    """获取 logo 的 base64 编码（SVG 格式）"""
    logo_path = Path(__file__).parent / "mcdonalds.svg"
    return base64.b64encode(logo_path.read_bytes()).decode()


def _render_topbar(period_str: str) -> str:
    """渲染顶部栏 HTML"""
    logo_b64 = _get_logo_base64()
    return f"""
<div class="topbar">
  <div class="topbar-left">
    <img src="data:image/svg+xml;base64,{logo_b64}" class="topbar-logo" alt="McDonald's">
    <div class="topbar-title">
      <h1>Performance Review</h1>
      <div class="sub">周度数据复盘看板</div>
    </div>
  </div>
  <div class="topbar-right">
    <span class="topbar-badge">{period_str}</span><br>
    McDonald's China &middot; IT Operating &middot; Traffic
  </div>
</div>
"""


def _render_nav() -> str:
    """渲染导航栏 HTML"""
    return """
<div class="nav-bar">
  <a class="nav-link" href="#sec-summary">Executive Summary</a>
  <a class="nav-link" href="#sec-operational">Operational Analysis</a>
  <a class="nav-link" href="#sec-bu">BU Analysis</a>
  <a class="nav-link" href="#sec-plan">Plan Analysis</a>
</div>
"""


def _render_kpi_card(label: str, value, sub: str = "", status: str = "", unit: str = "") -> str:
    """渲染 KPI 卡片"""
    status_cls = f" {status}" if status else ""

    # Target 为 0 时显示 "/"
    if isinstance(value, (int, float)) and value == 0 and "Target" in label:
        value_str = "/"
    elif isinstance(value, (int, float)):
        value_str = _fmt_number(value, unit=unit)
    else:
        value_str = str(value)

    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f"""
<div class="kpi-card{status_cls}">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value_str}</div>
  {sub_html}
</div>
"""


def _render_kpi_row(cards_html: list) -> str:
    """渲染 KPI 行"""
    return f'<div class="kpi-grid">{"".join(cards_html)}</div>'


def _fig_to_html(fig_json: str) -> str:
    """将 Plotly 图表 JSON 转为 HTML 片段（不含 Plotly JS，由 head 统一引入）"""
    # 从 JSON 重建图表
    fig = go.Figure(json.loads(fig_json))

    # 确保图表有明确的尺寸
    if fig.layout.height is None:
        fig.update_layout(height=300)

    # 生成 HTML（不含 plotlyjs，由 head 统一引入 CDN）
    return fig.to_html(include_plotlyjs=False, full_html=False)


def _render_section(num: int, title: str, content: str) -> str:
    """渲染一个 section"""
    return f"""
<div id="sec-{['summary', 'operational', 'bu', 'plan'][num-1]}"></div>
<section>
  <div class="sec-head">
    <span class="sec-num">{num}</span>
    <h2>{title}</h2>
  </div>
  {content}
</section>
"""


def generate_html(df, target: int, figs: dict, tables: dict, kpis: dict, period_str: str = "", channel_summary: dict = None) -> str:
    """
    生成完整的 HTML 文件。

    参数:
        df: 数据 DataFrame
        target: Target DAU
        figs: 各 tab 的图表字典 {"summary": [fig1, fig2], "operational": [fig1, fig2], ...}
        tables: 各 tab 的表格 HTML 字典
        kpis: 各 tab 的 KPI 数据字典
        period_str: 日期范围显示文本
        channel_summary: 渠道总结字典
    """
    if not period_str:
        period_str = date.today().strftime("%Y-%m-%d")
    today_str = date.today().strftime("%Y-%m-%d")

    # ─── Section 1: Executive Summary ───
    summary_kpis = kpis.get("summary", {})
    ach_rate = summary_kpis.get("achievement_rate", 0)
    ach_sub = f"{ach_rate:.1f}% 达成" if ach_rate > 0 else ""
    days_count = summary_kpis.get("days_count", 0)
    comp_str = summary_kpis.get("completion_str", "—")
    comp_sub = f"完成 {comp_str}（共 {days_count} 天）" if days_count > 0 else ""

    dau_label = "DAU Actual（日均·去重）" if summary_kpis.get("use_dau_sheet") else "DAU Actual（日均）"
    cards = [
        _render_kpi_card("DAU Target（日均）", target, sub=comp_sub),
        _render_kpi_card(dau_label, summary_kpis.get("avg_dau", 0), sub=ach_sub, status=summary_kpis.get("status", "")),
        _render_kpi_card("触达成功（日均）", summary_kpis.get("avg_reach", 0)),
        _render_kpi_card("订单Sales（日均）", summary_kpis.get("avg_sales", 0)),
    ]

    summary_content = _render_kpi_row(cards)
    for fig in figs.get("summary", []):
        summary_content += _fig_to_html(fig)

    # ─── Section 2: Operational ───
    op_kpis = kpis.get("operational", {})
    op_cards = [
        _render_kpi_card("触达成功（日均）", op_kpis.get("avg_reach", 0)),
        _render_kpi_card("点击人次（日均）", op_kpis.get("avg_clicks", 0)),
        _render_kpi_card("AARR 占比", op_kpis.get("aarr_pct", 0), unit="%"),
        _render_kpi_card("常规 占比", op_kpis.get("normal_pct", 0), unit="%"),
    ]
    op_content = _render_kpi_row(op_cards)
    op_figs = figs.get("operational", [])
    # 第一个图：AARR + 常规 堆积
    if len(op_figs) > 0:
        op_content += _fig_to_html(op_figs[0])
    # 分渠道明细表格
    op_content += tables.get("operational", "")
    # 第二个图：分渠道堆积（vs Target）
    if len(op_figs) > 1:
        op_content += '<div class="section-subheader">分渠道堆积（vs Target）</div>'
        op_content += _fig_to_html(op_figs[1])

    # ─── Section 3: BU ───
    bu_content = tables.get("bu", "")
    for fig in figs.get("bu", []):
        bu_content += _fig_to_html(fig)

    # ─── Section 4: Plan ───
    plan_content = tables.get("plan", "")

    # ─── 拼接完整 HTML ───
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Performance Review - {today_str}</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
{_get_css()}
</head>
<body>

{_render_topbar(period_str)}
{_render_nav()}

<div class="wrap">
  {_render_section(1, "Executive Summary", summary_content)}
  {_render_section(2, "Operational 分析", op_content)}
  {_render_section(3, "BU 分析", bu_content)}
  {_render_section(4, "Plan 分析", plan_content)}
</div>

<div class="footer">
  Generated by CNN Performance Weekly · {today_str}
</div>

</body>
</html>"""

    return html
