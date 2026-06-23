"""
tab_summary.py - 第一层：Executive Summary
KPI Cards + 每日 DAU 趋势图 + Nudge Type 堆积柱状图
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import MCD_RED, MCD_GOLD, MCD_GREEN
from components import kpi_card, kpi_row, section_header


def render(df: pd.DataFrame, target: int):
    """渲染 Executive Summary 层，返回 (figs, kpis) 供导出用"""

    st.markdown(section_header("Executive Summary", ""), unsafe_allow_html=True)

    # ─── 计算汇总指标 ──────────────────────────────────────
    total_clicks = df["点击人次"].sum()
    total_reach = df["触达成功"].sum()
    total_gc = df["订单GC"].sum()
    total_sales = df["订单Sales"].sum() if "订单Sales" in df.columns else 0

    # 按天聚合
    daily = df.groupby(df["发送日期"].dt.date).agg(
        DAU=("点击人次", "sum"),
        触达=("触达成功", "sum"),
        GC=("订单GC", "sum"),
    ).reset_index()
    daily.columns = ["日期", "DAU", "触达", "GC"]

    days_count = len(daily)

    # 完成天数
    if target > 0:
        completed_days = int((daily["DAU"] >= target).sum())
        completion_str = f"{completed_days}/{days_count}"
        avg_dau = daily["DAU"].mean()
        achievement_rate = avg_dau / target * 100
    else:
        completion_str = "—"
        avg_dau = daily["DAU"].mean()
        achievement_rate = 0

    # ─── KPI Cards（固定 3 列 × 2 行）────────────────────
    status_actual = "green" if achievement_rate >= 95 else ("yellow" if achievement_rate >= 85 else "red") if target > 0 else ""

    row1_cards = [
        kpi_card("DAU Target（日均）", target),
        kpi_card("DAU Actual（日均）", round(avg_dau), status=status_actual),
        kpi_card("达成率", achievement_rate, unit="%" if target > 0 else "", status=status_actual),
    ]

    completion_status = "green" if target > 0 and completed_days >= days_count else ("yellow" if target > 0 and completed_days >= days_count * 0.7 else "red") if target > 0 else ""
    row2_cards = [
        kpi_card("完成天数", completion_str, sub=f"共 {days_count} 天", status=completion_status),
        kpi_card("总触达成功", total_reach),
        kpi_card("总订单Sales", total_sales, unit=""),
    ]

    st.markdown(kpi_row(row1_cards), unsafe_allow_html=True)
    st.markdown(kpi_row(row2_cards), unsafe_allow_html=True)

    # ─── 每日 DAU 趋势图 ──────────────────────────────────
    st.markdown('<div class="section-subheader">每日 DAU 趋势</div>', unsafe_allow_html=True)

    fig = go.Figure()

    # DAU 折线
    fig.add_trace(go.Scatter(
        x=daily["日期"],
        y=daily["DAU"],
        mode="lines+markers",
        name="DAU（点击人次）",
        line=dict(color=MCD_RED, width=2.5),
        marker=dict(size=6, color=MCD_RED),
        fill="tozeroy",
        fillcolor="rgba(218,41,28,0.05)",
    ))

    # Target 水平线（黑色）
    if target > 0:
        fig.add_hline(
            y=target,
            line_dash="dash",
            line_color="#1a1a1a",
            line_width=2,
            annotation_text=f"Target: {target:,.0f}",
            annotation_position="top right",
            annotation_font=dict(size=12, color="#1a1a1a"),
        )

        # 标记未完成的点
        colors = [MCD_GREEN if v >= target else MCD_RED for v in daily["DAU"]]
        fig.add_trace(go.Scatter(
            x=daily["日期"],
            y=daily["DAU"],
            mode="markers",
            name="完成/未完成",
            marker=dict(size=10, color=colors, symbol="circle"),
            showlegend=False,
        ))

    fig.update_layout(
        height=320,
        margin=dict(l=60, r=20, t=30, b=40),
        plot_bgcolor="#f4efe6",
        paper_bgcolor="#f4efe6",
        xaxis=dict(title="", gridcolor="#E8E8E8", tickformat="%m/%d\n%a"),
        yaxis=dict(title="DAU", gridcolor="#E8E8E8", tickformat=","),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        font=dict(family="'PingFang SC', 'Microsoft YaHei', sans-serif"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ─── Nudge Type 每日拆分（堆积柱状图）─────────────────
    st.markdown('<div class="section-subheader">Nudge Type 每日拆分</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:12px;color:#999;margin-bottom:8px;">'
        'On-demand / Responsive 暂无数据，仅展示 Operational</div>',
        unsafe_allow_html=True,
    )

    df_op = df[df["计划类型"].notna()].copy()
    daily_type = df_op.groupby([df_op["发送日期"].dt.date, "计划类型"]).agg(
        DAU=("点击人次", "sum"),
    ).reset_index()
    daily_type.columns = ["日期", "计划类型", "DAU"]

    daily_aarr = daily_type[daily_type["计划类型"] == "AARRPlan"].set_index("日期")["DAU"]
    daily_normal = daily_type[daily_type["计划类型"] == "常规Plan"].set_index("日期")["DAU"]

    all_dates = sorted(daily_type["日期"].unique())
    daily_aarr = daily_aarr.reindex(all_dates, fill_value=0)
    daily_normal = daily_normal.reindex(all_dates, fill_value=0)

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=all_dates,
        y=daily_aarr.values,
        name="AARR",
        marker_color=MCD_RED,
        opacity=0.85,
    ))

    fig2.add_trace(go.Bar(
        x=all_dates,
        y=daily_normal.values,
        name="常规",
        marker_color=MCD_GOLD,
        opacity=0.85,
    ))

    if target > 0:
        fig2.add_hline(
            y=target,
            line_dash="dash",
            line_color="#1a1a1a",
            line_width=2,
            annotation_text=f"Target: {target:,.0f}",
            annotation_position="top right",
            annotation_font=dict(size=12, color="#1a1a1a"),
        )

    fig2.update_layout(
        barmode="stack",
        height=300,
        margin=dict(l=60, r=20, t=30, b=40),
        plot_bgcolor="#f4efe6",
        paper_bgcolor="#f4efe6",
        xaxis=dict(title="", gridcolor="#E8E8E8", tickformat="%m/%d\n%a"),
        yaxis=dict(title="DAU（点击人次）", gridcolor="#E8E8E8", tickformat=","),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        font=dict(family="'PingFang SC', 'Microsoft YaHei', sans-serif"),
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ─── 返回数据供导出（用 JSON 序列化避免 deepcopy 问题）─────
    import json
    fig_json = fig.to_json()
    fig2_json = fig2.to_json()

    kpis = {
        "avg_dau": round(avg_dau),
        "achievement_rate": round(achievement_rate, 1),
        "completion_str": completion_str,
        "days_count": days_count,
        "total_reach": total_reach,
        "total_sales": total_sales,
        "status": status_actual,
    }
    figs = [fig_json, fig2_json]
    return figs, kpis
