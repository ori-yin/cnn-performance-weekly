"""
app.py - CNN Performance Weekly 主入口
"""

import streamlit as st
from datetime import date, timedelta
import urllib.parse

from config import MCD_RED, MCD_GOLD
from data import read_data, filter_week_data
from styles import get_css
from tabs.tab_summary import render as render_summary
from tabs.tab_operational import render as render_operational
from tabs.tab_bu import render as render_bu
from tabs.tab_plan import render as render_plan


def render_topbar(today_str: str):
    """渲染顶部栏"""
    st.markdown(f"""
    <div class="topbar">
      <div class="topbar-left">
        <div class="topbar-logo">M</div>
        <div class="topbar-title">
          <h1>Performance Review</h1>
          <div class="sub">周度数据复盘看板</div>
        </div>
      </div>
      <div class="topbar-right">
        <span class="topbar-badge">Weekly Report</span><br>
        {today_str} &nbsp; McDonald's China &middot; IT Operating &middot; Traffic
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_nav(active_tab: str):
    """渲染导航栏（用 st.radio 实现真实切换）"""
    tabs = {
        "summary": "Executive Summary",
        "operational": "Operational Analysis",
        "bu": "BU Analysis",
        "plan": "Plan Analysis",
    }
    # 用 radio 实现，但用 CSS 隐藏原生样式，用自定义 HTML 模拟按钮
    cols = st.columns(len(tabs))
    selected = active_tab
    for i, (key, label) in enumerate(tabs.items()):
        with cols[i]:
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if key == active_tab else "secondary",
            ):
                selected = key
    return selected


def main():
    st.set_page_config(
        page_title="Performance Review",
        page_icon="favicon.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 隐藏 Streamlit 默认 header（brand mark + hamburger）
    st.markdown(get_css(), unsafe_allow_html=True)

    # ─── 顶部栏 ─────────────────────────────────────────
    today_str = date.today().strftime("%Y-%m-%d")
    render_topbar(today_str)

    # ─── 导航栏 ─────────────────────────────────────────
    # 用 query params 或 session state 追踪当前 tab
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "summary"

    # 检查 URL query params
    query_params = st.query_params
    if "tab" in query_params:
        tab_val = query_params["tab"]
        if tab_val in ["summary", "operational", "bu", "plan"]:
            st.session_state.active_tab = tab_val

    active_tab = render_nav(st.session_state.active_tab)
    if active_tab != st.session_state.active_tab:
        st.session_state.active_tab = active_tab
        st.query_params["tab"] = active_tab
        st.rerun()

    # ─── 侧边栏 ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 数据设置")
        uploaded = st.file_uploader(
            "上传 Excel / CSV",
            type=["xlsx", "xls", "csv"],
            help="拖入 CNN 周报数据文件",
        )

        st.markdown("---")
        target_dau = st.number_input(
            "Target DAU（日均）",
            min_value=0,
            value=1000,
            step=100,
            help="本周每日目标触达人次",
        )

        # ── 日期范围 ──
        st.markdown("---")
        st.markdown("##### 日期范围")
        today = date.today()
        default_start = today - timedelta(days=today.weekday() + 7)  # 上周一
        default_end = default_start + timedelta(days=6)               # 上周日
        start_date = st.date_input("开始日期", value=default_start)
        end_date = st.date_input("结束日期", value=default_end)

        # ── 维度筛选 ──
        st.markdown("---")
        st.markdown("##### 维度筛选")

    # ─── 数据读取 ─────────────────────────────────────────
    if uploaded is not None:
        raw_df = read_data(uploaded)
    else:
        st.info("请在左侧上传 Excel 或 CSV 数据文件")
        return

    if raw_df is None or raw_df.empty:
        st.error("数据文件读取失败或为空")
        return

    # 日期筛选
    df = filter_week_data(raw_df, start_date, end_date)
    if df.empty:
        st.warning(f"所选日期范围 [{start_date} ~ {end_date}] 内无数据")
        return

    # Sidebar 维度筛选（需数据加载后才有选项）
    with st.sidebar:
        channels = sorted(df["渠道"].dropna().unique().tolist()) if "渠道" in df.columns else []
        plan_types = sorted(df["计划类型"].dropna().unique().tolist()) if "计划类型" in df.columns else []
        bus = sorted(df["预算owner"].dropna().unique().tolist()) if "预算owner" in df.columns else []

        selected_channels = st.multiselect("渠道", channels, default=channels)
        selected_plan_types = st.multiselect("计划类型", plan_types, default=plan_types)
        selected_bus = st.multiselect("预算 Owner (BU)", bus, default=bus)

    # 应用筛选
    if selected_channels:
        df = df[df["渠道"].isin(selected_channels)]
    if selected_plan_types:
        df = df[df["计划类型"].isin(selected_plan_types)]
    if selected_bus:
        df = df[df["预算owner"].isin(selected_bus)]

    if df.empty:
        st.warning("筛选后无数据，请调整筛选条件")
        return

    # ─── 主体内容 ─────────────────────────────────────────
    tab = st.session_state.active_tab

    if tab == "summary":
        render_summary(df, target_dau)
    elif tab == "operational":
        render_operational(df, target_dau)
    elif tab == "bu":
        render_bu(df, target_dau)
    elif tab == "plan":
        render_plan(df)


if __name__ == "__main__":
    main()
