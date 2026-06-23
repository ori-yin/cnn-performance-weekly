"""
components.py - CNN Performance Weekly：可复用 UI 组件
参考 mcd-reach-trend 的 KPI Card 组件
"""

from config import MCD_RED, MCD_GOLD, MCD_GREEN, MCD_CARD_BG, MCD_BORDER, MCD_TEXT, MCD_TEXT_SUB


def _fmt_number(val, unit=""):
    """格式化数字：大数用 K/M，百分比保留 1 位"""
    if unit == "%":
        return f"{val:.1f}%"
    if abs(val) >= 1_000_000:
        return f"{val / 1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        return f"{val / 1_000:.1f}K"
    return f"{val:,.0f}"


def _status_color(status: str) -> str:
    return {"green": MCD_GREEN, "yellow": MCD_GOLD, "red": MCD_RED}.get(status, "#999")


def kpi_card(label: str, value, sub: str = "", status: str = "", unit: str = "") -> str:
    """
    KPI 卡片组件。
    - label: 指标名
    - value: 主数值
    - sub: 副文本（环比等）
    - status: green/yellow/red（左侧色条）
    - unit: 数值单位（如 "%"），传入时格式化为百分比
    """
    status_class = status if status in ("green", "yellow", "red") else ""
    if unit:
        val_str = _fmt_number(value, unit=unit)
    elif isinstance(value, (int, float)):
        val_str = _fmt_number(value)
    else:
        val_str = str(value)

    sub_html = ""
    if sub:
        # 自动标记 ↑↓ 颜色
        if "↑" in sub:
            sub_html = f'<div class="kpi-sub"><span class="up">{sub}</span></div>'
        elif "↓" in sub:
            sub_html = f'<div class="kpi-sub"><span class="down">{sub}</span></div>'
        else:
            sub_html = f'<div class="kpi-sub">{sub}</div>'

    fallback_sub = '<div class="kpi-sub">&nbsp;</div>'
    return (
        f'<div class="kpi-card {status_class}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{val_str}</div>'
        f'{sub_html if sub_html else fallback_sub}'
        f'</div>'
    )


def kpi_row(cards: list) -> str:
    """将多个 KPI Card 排成一行，CSS Grid 等宽等高"""
    n = len(cards)
    items = "".join(f"<div>{c}</div>" for c in cards)
    return (
        f'<div style="display:grid;grid-template-columns:repeat({n},1fr);gap:10px;margin-bottom:12px;">'
        f'{items}'
        f'</div>'
    )


def section_header(title: str, subtitle: str = "") -> str:
    """Section 标题"""
    sub = f'<div class="section-subheader">{subtitle}</div>' if subtitle else ""
    return f'<div class="section-header">{title}</div>{sub}'


def status_badge(status: str) -> str:
    """状态色块标记"""
    color = _status_color(status)
    label = {"green": "达成", "yellow": "偏弱", "red": "承压"}.get(status, "—")
    return (
        f'<span style="display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:600;color:{color};">'
        f'<span style="width:6px;height:6px;border-radius:50%;background:{color};"></span>'
        f'{label}</span>'
    )


def styled_table(df, columns: list = None, highlight_col: str = None):
    """
    生成带样式的 HTML 表格。
    - columns: 显示的列（默认全部）
    - highlight_col: 需要状态高亮的列名
    """
    if columns:
        df = df[columns]

    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for col in df.columns:
            val = row[col]
            style = ""
            if col == highlight_col:
                color = _status_color(str(val).lower())
                style = f'color:{color};font-weight:600;'
            if isinstance(val, float):
                val = f"{val:.1f}"
            cells += f'<td style="{style}">{val}</td>'
        rows_html += f"<tr>{cells}</tr>"

    headers = "".join(f"<th>{c}</th>" for c in df.columns)
    return (
        f'<table class="dataframe" style="width:100%;border-collapse:collapse;">'
        f'<thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>'
    )


def progress_bar(actual: float, target: float, width: str = "100%") -> str:
    """进度条组件"""
    if target <= 0:
        pct = 0
    else:
        pct = min(actual / target * 100, 100)

    if pct >= 95:
        color = MCD_GREEN
    elif pct >= 85:
        color = MCD_GOLD
    else:
        color = MCD_RED

    return (
        f'<div style="width:{width};height:8px;background:#EDEDED;border-radius:4px;overflow:hidden;">'
        f'<div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:4px;transition:width 0.3s;"></div>'
        f'</div>'
    )
