"""
tab_operational.py - 第二层：Operational 分析
AARR / 常规 × 渠道，堆积柱状图 + 折叠展开
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import MCD_RED, MCD_GOLD, MCD_GREEN, CHANNELS
from components import section_header, kpi_card, kpi_row


def _compute_metrics(df: pd.DataFrame) -> dict:
    """计算一组数据的核心指标"""
    return {
        "触达成功": df["触达成功"].sum(),
        "点击人次": df["点击人次"].sum(),
        "CTR": df["点击人次"].sum() / df["触达成功"].sum() * 100 if df["触达成功"].sum() > 0 else 0,
        "订单GC": df["订单GC"].sum(),
        "GC转化率": df["订单GC"].sum() / df["点击人次"].sum() * 100 if df["点击人次"].sum() > 0 else 0,
        "Plan数": df["Plan ID"].nunique() if "Plan ID" in df.columns else len(df),
        "订单Sales": round(df["订单Sales"].sum(), 2) if "订单Sales" in df.columns else 0,
    }


def _channel_detail_table(df_sub: pd.DataFrame, plan_type_label: str):
    """渲染单个计划类型的渠道明细表"""
    rows = []
    for ch in CHANNELS:
        ch_df = df_sub[df_sub["渠道"] == ch]
        if len(ch_df) == 0:
            continue
        m = _compute_metrics(ch_df)
        rows.append({
            "渠道": ch,
            "触达成功": int(m["触达成功"]),
            "点击人次": int(m["点击人次"]),
            "CTR": m["CTR"],
            "订单GC": int(m["订单GC"]),
            "GC转化率": m["GC转化率"],
            "Plan数": m["Plan数"],
            "订单Sales": m["订单Sales"],
        })

    if not rows:
        st.info(f"没有 {plan_type_label} 的渠道数据")
        return

    TH = "background:#a8001a;color:#fff;padding:9px 11px;font-weight:700;font-size:11.5px;"
    TD = "padding:8px 11px;border-bottom:1px solid #f0e8d6;"
    TD_EVEN = "padding:8px 11px;border-bottom:1px solid #f0e8d6;background:#fcfaf3;"

    rows_html = ""
    for i, r in enumerate(rows):
        td_style = TD_EVEN if i % 2 == 1 else TD
        rows_html += (
            f"<tr>"
            f"<td style='{td_style}'>{r['渠道']}</td>"
            f"<td style='{td_style}text-align:right;'>{r['触达成功']:,}</td>"
            f"<td style='{td_style}text-align:right;'>{r['点击人次']:,}</td>"
            f"<td style='{td_style}text-align:right;'>{r['CTR']:.2f}%</td>"
            f"<td style='{td_style}text-align:right;'>{r['订单GC']:,}</td>"
            f"<td style='{td_style}text-align:right;'>{r['GC转化率']:.1f}%</td>"
            f"<td style='{td_style}text-align:right;'>{r['Plan数']}</td>"
            f"<td style='{td_style}text-align:right;'>{r['订单Sales']:,.2f}</td>"
            f"</tr>"
        )

    st.markdown(
        f'<div style="font-size:13px;font-weight:600;color:#2b2620;margin:12px 0 8px;">{plan_type_label} 分渠道</div>'
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;background:#fffdf8;border-radius:9px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.04);">'
        f'<thead><tr>'
        f'<th style="{TH}text-align:left;">渠道</th>'
        f'<th style="{TH}text-align:right;">触达成功</th>'
        f'<th style="{TH}text-align:right;">点击人次</th>'
        f'<th style="{TH}text-align:right;">CTR</th>'
        f'<th style="{TH}text-align:right;">订单GC</th>'
        f'<th style="{TH}text-align:right;">GC转化率</th>'
        f'<th style="{TH}text-align:right;">Plan数</th>'
        f'<th style="{TH}text-align:right;">订单Sales</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>',
        unsafe_allow_html=True,
    )


def render(df: pd.DataFrame, target: int):
    """渲染 Operational 分析层"""

    st.markdown(section_header("Operational 分析", "AARR / 常规 × 渠道"), unsafe_allow_html=True)

    # 筛选 Operational 数据
    df_op = df[df["计划类型"].notna()].copy()

    if len(df_op) == 0:
        st.info("当前筛选条件下没有 Operational 数据")
        return

    # ─── 汇总 KPI ──────────────────────────────────────
    m_total = _compute_metrics(df_op)
    m_aarr = _compute_metrics(df_op[df_op["计划类型"] == "AARRPlan"])
    m_normal = _compute_metrics(df_op[df_op["计划类型"] == "常规Plan"])

    cards = [
        kpi_card("Operational 总触达", int(m_total["触达成功"])),
        kpi_card("Operational 总点击", int(m_total["点击人次"])),
        kpi_card("AARR 占比", m_aarr["点击人次"] / m_total["点击人次"] * 100 if m_total["点击人次"] > 0 else 0, unit="%"),
        kpi_card("常规 占比", m_normal["点击人次"] / m_total["点击人次"] * 100 if m_total["点击人次"] > 0 else 0, unit="%"),
    ]
    st.markdown(kpi_row(cards), unsafe_allow_html=True)

    # ─── 每日堆积柱状图（AARR + 常规 vs Target）──────────
    st.markdown('<div class="section-subheader">每日 DAU：AARR + 常规 堆积</div>', unsafe_allow_html=True)

    daily_type = df_op.groupby([df_op["发送日期"].dt.date, "计划类型"]).agg(
        DAU=("点击人次", "sum"),
    ).reset_index()
    daily_type.columns = ["日期", "计划类型", "DAU"]

    daily_aarr = daily_type[daily_type["计划类型"] == "AARRPlan"].set_index("日期")["DAU"]
    daily_normal = daily_type[daily_type["计划类型"] == "常规Plan"].set_index("日期")["DAU"]

    # 合并，确保所有日期都有
    all_dates = sorted(daily_type["日期"].unique())
    daily_aarr = daily_aarr.reindex(all_dates, fill_value=0)
    daily_normal = daily_normal.reindex(all_dates, fill_value=0)

    fig = go.Figure()

    # AARR 柱（底部）
    fig.add_trace(go.Bar(
        x=all_dates,
        y=daily_aarr.values,
        name="AARR",
        marker_color=MCD_RED,
        opacity=0.85,
    ))

    # 常规柱（堆叠在上面）
    fig.add_trace(go.Bar(
        x=all_dates,
        y=daily_normal.values,
        name="常规",
        marker_color=MCD_GOLD,
        opacity=0.85,
    ))

    # Target 水平线
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

    fig.update_layout(
        barmode="stack",
        height=320,
        margin=dict(l=40, r=20, t=30, b=40),
        plot_bgcolor="#f4efe6",
        paper_bgcolor="#f4efe6",
        xaxis=dict(title="", gridcolor="#E8E8E8", tickformat="%m/%d\n%a"),
        yaxis=dict(title="DAU（点击人次）", gridcolor="#E8E8E8", tickformat=","),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
        ),
        font=dict(family="'PingFang SC', 'Microsoft YaHei', sans-serif"),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ─── 分渠道明细（折叠）─────────────────────────────
    with st.expander("▼ 分渠道明细", expanded=False):
        df_aarr = df_op[df_op["计划类型"] == "AARRPlan"]
        df_normal = df_op[df_op["计划类型"] == "常规Plan"]

        if len(df_aarr) > 0:
            _channel_detail_table(df_aarr, "AARR")

        if len(df_normal) > 0:
            _channel_detail_table(df_normal, "常规")

    # ─── 分渠道每日趋势（折叠）─────────────────────────
    with st.expander("▼ 分渠道每日趋势", expanded=False):
        daily_ch = df_op.groupby([df_op["发送日期"].dt.date, "渠道"]).agg(
            DAU=("点击人次", "sum"),
        ).reset_index()
        daily_ch.columns = ["日期", "渠道", "DAU"]

        ch_colors = {
            "APP Push": MCD_RED,
            "企微1v1": MCD_GOLD,
            "短信": MCD_GREEN,
            "微信小程序订阅消息": "#5B5BD6",
        }

        fig2 = go.Figure()
        for ch in CHANNELS:
            subset = daily_ch[daily_ch["渠道"] == ch]
            if len(subset) > 0:
                fig2.add_trace(go.Scatter(
                    x=subset["日期"],
                    y=subset["DAU"],
                    mode="lines+markers",
                    name=ch,
                    line=dict(color=ch_colors.get(ch, "#999"), width=2),
                    marker=dict(size=4),
                ))

        if target > 0:
            fig2.add_hline(y=target, line_dash="dash", line_color="#999", line_width=1.5,
                           annotation_text="Target", annotation_position="top right")

        fig2.update_layout(
            height=280,
            margin=dict(l=40, r=20, t=30, b=40),
            plot_bgcolor=MCD_BG,
            paper_bgcolor=MCD_BG,
            xaxis=dict(title="", gridcolor="#E8E8E8", tickformat="%m/%d"),
            yaxis=dict(title="DAU", gridcolor="#E8E8E8", tickformat=","),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
            font=dict(family="'PingFang SC', 'Microsoft YaHei', sans-serif"),
        )
        st.plotly_chart(fig2, use_container_width=True)
