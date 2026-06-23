"""
tab_bu.py - 第三层：BU 分析
按预算 owner 聚合，不拆 AARR/常规
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import MCD_RED, MCD_GOLD, MCD_GREEN, MCD_BG
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

    st.markdown(section_header("BU 分析", "按预算 owner 聚合"), unsafe_allow_html=True)

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

    # ─── BU 总览表 ──────────────────────────────────────
    st.markdown('<div class="section-subheader">BU 总览</div>', unsafe_allow_html=True)

    rows_html = ""
    for _, row in bu_df.iterrows():
        rows_html += (
            f"<tr style='border-bottom:1px solid #F0F0F0;'>"
            f"<td style='padding:8px;font-weight:600;'>{row['BU']}</td>"
            f"<td style='text-align:right;padding:8px;'>{row['Plan数']}</td>"
            f"<td style='text-align:right;padding:8px;'>{row['触达成功']:,}</td>"
            f"<td style='text-align:right;padding:8px;'>{row['点击人次']:,}</td>"
            f"<td style='text-align:right;padding:8px;'>{row['CTR']:.2f}%</td>"
            f"<td style='text-align:right;padding:8px;'>{row['订单GC']:,}</td>"
            f"<td style='text-align:right;padding:8px;'>{row['GC转化率']:.1f}%</td>"
            f"<td style='text-align:right;padding:8px;'>{row['订单Sales']:,.2f}</td>"
            f"</tr>"
        )

    st.markdown(
        f'<table style="width:100%;border-collapse:collapse;font-size:13px;">'
        f'<thead><tr style="border-bottom:2px solid #E8E8E8;">'
        f'<th style="text-align:left;padding:8px;color:#666;font-size:11px;">BU</th>'
        f'<th style="text-align:right;padding:8px;color:#666;font-size:11px;">Plan数</th>'
        f'<th style="text-align:right;padding:8px;color:#666;font-size:11px;">触达成功</th>'
        f'<th style="text-align:right;padding:8px;color:#666;font-size:11px;">点击人次</th>'
        f'<th style="text-align:right;padding:8px;color:#666;font-size:11px;">CTR</th>'
        f'<th style="text-align:right;padding:8px;color:#666;font-size:11px;">订单GC</th>'
        f'<th style="text-align:right;padding:8px;color:#666;font-size:11px;">GC转化率</th>'
        f'<th style="text-align:right;padding:8px;color:#666;font-size:11px;">订单Sales</th>'
        f'</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>',
        unsafe_allow_html=True,
    )

    # ─── BU 贡献柱状图（可切换触达/点击）─────────────────
    st.markdown('<div class="section-subheader">BU 贡献</div>', unsafe_allow_html=True)

    chart_metric = st.radio(
        "指标",
        options=["触达成功", "点击人次"],
        horizontal=True,
        label_visibility="collapsed",
        key="bu_chart_metric",
    )

    top_n = bu_df.head(15)
    bar_color = MCD_RED if chart_metric == "触达成功" else MCD_GOLD

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=top_n["BU"],
        y=top_n[chart_metric],
        marker_color=bar_color,
        name=chart_metric,
        text=top_n[chart_metric].apply(lambda x: f"{x:,}"),
        textposition="outside",
        textfont=dict(size=10),
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=40, r=20, t=30, b=60),
        plot_bgcolor=MCD_BG,
        paper_bgcolor=MCD_BG,
        xaxis=dict(title="", gridcolor="#E8E8E8", tickangle=-30),
        yaxis=dict(title=chart_metric, gridcolor="#E8E8E8", tickformat=","),
        showlegend=False,
        font=dict(family="'PingFang SC', 'Microsoft YaHei', sans-serif"),
    )

    st.plotly_chart(fig, use_container_width=True)
