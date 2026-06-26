"""
tab_bu.py - 第三层：BU 分析
按预算 owner 聚合，不拆 AARR/常规
"""

import streamlit as st
import pandas as pd
from config import MCD_DARK_RED, THEME_INK, THEME_INK2, THEME_MUTED, THEME_PAPER, THEME_LINE, THEME_ROW_ALT, THEME_RADIUS_M
from components import section_header


def _compute_bu_metrics(df: pd.DataFrame) -> dict:
    """计算 BU 的核心指标"""
    return {
        "Plan数": df["Plan ID"].nunique() if "Plan ID" in df.columns else len(df),
        "触达成功": int(df["触达成功"].sum()),
        "点击人次": int(df["点击人次"].sum()),
        "CTR": df["点击人次"].sum() / df["触达成功"].sum() * 100 if df["触达成功"].sum() > 0 else 0,
        "订单GC": int(df["订单GC"].sum()),
        "GC转化率": df["订单GC"].sum() / df["点击人次"].sum() * 100 if df["点击人次"].sum() > 0 else 0,
        "订单Sales": round(df["订单Sales"].sum(), 2) if "订单Sales" in df.columns else 0,
    }


def render(df: pd.DataFrame):
    """渲染 BU 分析层"""

    st.markdown(section_header("BU 分析", ""), unsafe_allow_html=True)

    # 按 BU 聚合
    bu_groups = df.groupby("预算owner")
    bu_rows = []

    for bu, bu_df in bu_groups:
        if pd.isna(bu) or bu == "[NULL]" or bu == "":
            continue
        m = _compute_bu_metrics(bu_df)
        bu_rows.append({"BU": bu, **m})

    if not bu_rows:
        st.info("当前筛选条件下没有 BU 数据")
        return

    bu_df = pd.DataFrame(bu_rows)
    bu_df = bu_df.sort_values("点击人次", ascending=False).reset_index(drop=True)
    days_count = df["发送日期"].dt.date.nunique()

    # ─── BU 综合评分 ────────────────────────────────────────
    # 触达归一化（幂律压缩）
    reach_max = bu_df["触达成功"].max()
    if reach_max > 0:
        bu_df["触达_norm"] = (bu_df["触达成功"] / reach_max) ** 0.3 * 100
    else:
        bu_df["触达_norm"] = 0

    # CTR 归一化（Q3 阈值）
    ctr_q3 = bu_df["CTR"].quantile(0.75)
    if ctr_q3 > 0:
        bu_df["CTR_norm"] = bu_df["CTR"].apply(lambda x: 100 if x >= ctr_q3 else 100 * (x / ctr_q3) ** 1.5)
    else:
        bu_df["CTR_norm"] = 50

    # GC转化率 归一化（Q3 阈值）
    gc_q3 = bu_df["GC转化率"].quantile(0.75)
    if gc_q3 > 0:
        bu_df["GC_norm"] = bu_df["GC转化率"].apply(lambda x: 100 if x >= gc_q3 else 100 * (x / gc_q3) ** 1.5)
    else:
        bu_df["GC_norm"] = 50

    # 置信度惩罚
    def _penalty(reach):
        if reach < 100: return 0.1
        if reach < 500: return 0.3
        if reach < 1000: return 0.5
        if reach < 5000: return 0.8
        return 1.0

    bu_df["惩罚"] = bu_df["触达成功"].apply(_penalty)
    bu_df["评分"] = (bu_df["CTR_norm"] * 0.50 + bu_df["触达_norm"] * 0.25 + bu_df["GC_norm"] * 0.25) * bu_df["惩罚"]
    bu_df["评分"] = bu_df["评分"].round(1)

    # ─── BU 排行榜（4 个榜单横排）──────────────────────────
    st.markdown('<div class="section-subheader">BU 排行榜</div>', unsafe_allow_html=True)

    def _fmt_val(val, unit=""):
        if unit == "%":
            return f"{val:.2f}%"
        if val >= 1_000_000:
            return f"{val/1_000_000:.1f}M"
        if val >= 1_000:
            return f"{val/1_000:.1f}K"
        return f"{val:,.0f}"

    def _rank_html(title, sorted_df, metric_col, unit=""):
        medal_bg = ["#FFF8E1", "#F5F5F5", "#FBE9E7"]
        medal_icon = ["🥇", "🥈", "🥉"]
        rows = ""
        for i, (_, row) in enumerate(sorted_df.head(5).iterrows()):
            bg = medal_bg[i] if i < 3 else "#fff"
            icon = medal_icon[i] if i < 3 else f'<span style="color:{THEME_MUTED};font-size:11px;">{i+1}.</span>'
            val = _fmt_val(row[metric_col], unit)
            rows += (
                f'<div style="display:flex;align-items:center;gap:8px;padding:6px 10px;background:{bg};border-radius:6px;margin-bottom:3px;">'
                f'<span style="width:22px;text-align:center;flex-shrink:0;">{icon}</span>'
                f'<span style="flex:1;font-size:12px;font-weight:600;color:{THEME_INK};overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{row["BU"]}</span>'
                f'<span style="font-size:12px;color:{THEME_INK2};font-variant-numeric:tabular-nums;flex-shrink:0;">{val}</span>'
                f'</div>'
            )
        return (
            f'<div style="background:{THEME_PAPER};border:1px solid {THEME_LINE};border-radius:{THEME_RADIUS_M};padding:12px;">'
            f'<div style="font-size:13px;font-weight:700;color:{MCD_DARK_RED};margin-bottom:8px;">{title}</div>'
            f'{rows}</div>'
        )

    rank_plan = bu_df.sort_values("Plan数", ascending=False)
    rank_reach = bu_df.sort_values("触达成功", ascending=False)
    rank_ctr = bu_df[bu_df["触达成功"] >= 10000].sort_values("CTR", ascending=False)
    rank_sales = bu_df.sort_values("订单Sales", ascending=False)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_rank_html("Plan数 TOP5", rank_plan, "Plan数"), unsafe_allow_html=True)
    with c2:
        st.markdown(_rank_html("触达成功 TOP5", rank_reach, "触达成功"), unsafe_allow_html=True)
    with c3:
        st.markdown(_rank_html("CTR TOP5", rank_ctr, "CTR", unit="%"), unsafe_allow_html=True)
    with c4:
        st.markdown(_rank_html("Sales TOP5", rank_sales, "订单Sales"), unsafe_allow_html=True)

    # 排行榜 HTML（供导出）
    bu_rank_html = (
        '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">'
        + _rank_html("Plan数 TOP5", rank_plan, "Plan数")
        + _rank_html("触达成功 TOP5", rank_reach, "触达成功")
        + _rank_html("CTR TOP5", rank_ctr, "CTR", unit="%")
        + _rank_html("Sales TOP5", rank_sales, "订单Sales")
        + '</div>'
    )

    # ─── BU 总览表（构建一次，显示+导出共用）─────────────────
    st.markdown('<div class="section-subheader">BU 总览</div>', unsafe_allow_html=True)

    TH = f"background:{MCD_DARK_RED};color:#fff;padding:10px 12px;font-weight:700;font-size:12px;"
    TD = f"padding:8px 12px;border-bottom:1px solid {THEME_LINE};"
    TD_EVEN = f"padding:8px 12px;border-bottom:1px solid {THEME_LINE};background:{THEME_ROW_ALT};"

    rows_html = ""
    for i, (_, row) in enumerate(bu_df.iterrows()):
        td_style = TD_EVEN if i % 2 == 1 else TD
        d = days_count if days_count > 0 else 1
        rows_html += (
            f"<tr>"
            f"<td style='{td_style}font-weight:600;'>{row['BU']}</td>"
            f"<td style='{td_style}text-align:right;'>{row['Plan数']}</td>"
            f"<td style='{td_style}text-align:right;'>{int(row['触达成功'] / d):,}</td>"
            f"<td style='{td_style}text-align:right;'>{int(row['点击人次'] / d):,}</td>"
            f"<td style='{td_style}text-align:right;'>{row['CTR']:.2f}%</td>"
            f"<td style='{td_style}text-align:right;'>{int(row['订单GC'] / d):,}</td>"
            f"<td style='{td_style}text-align:right;'>{row['GC转化率']:.1f}%</td>"
            f"<td style='{td_style}text-align:right;'>{row['订单Sales'] / d:,.2f}</td>"
            f"<td style='{td_style}text-align:right;'>{row['评分']:.1f}</td>"
            f"</tr>"
        )

    bu_table_html = (
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;background:{THEME_PAPER};border-radius:9px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.04);">'
        f'<thead><tr>'
        f'<th style="{TH}text-align:left;">BU</th>'
        f'<th style="{TH}text-align:right;">Plan数</th>'
        f'<th style="{TH}text-align:right;">触达成功（日均）</th>'
        f'<th style="{TH}text-align:right;">点击人次（日均）</th>'
        f'<th style="{TH}text-align:right;">CTR</th>'
        f'<th style="{TH}text-align:right;">订单GC（日均）</th>'
        f'<th style="{TH}text-align:right;">GC转化率</th>'
        f'<th style="{TH}text-align:right;">订单Sales（日均）</th>'
        f'<th style="{TH}text-align:right;">评分</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>'
    )
    st.markdown(bu_table_html, unsafe_allow_html=True)

    return [], bu_rank_html + bu_table_html
