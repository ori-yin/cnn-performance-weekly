"""
app.py - CNN Performance Weekly 主入口
"""

import streamlit as st
from datetime import date, timedelta

from config import MCD_RED, MCD_GOLD
from data import read_data, filter_week_data
from scoring import compute_scores
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
        <img src="mcdonalds.png" class="topbar-logo-img" alt="McDonald's">
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


def render_nav():
    """渲染导航栏（锚点跳转，单页滚动）"""
    st.markdown("""
    <div class="nav-bar">
      <a class="nav-link" href="#sec-summary">Executive Summary</a>
      <a class="nav-link" href="#sec-operational">Operational Analysis</a>
      <a class="nav-link" href="#sec-bu">BU Analysis</a>
      <a class="nav-link" href="#sec-plan">Plan Analysis</a>
    </div>
    """, unsafe_allow_html=True)


def render_fixed_header_js():
    """用 JS 把 topbar 和 nav 移到 body 层级，实现真正固定"""
    import streamlit.components.v1 as components
    components.html("""
    <script>
    (function() {
      function setupFixedHeader() {
        var topbar = parent.document.querySelector('.topbar');
        var navBar = parent.document.querySelector('.nav-bar');
        if (!topbar || !navBar) return;
        if (topbar.dataset.fixed) return;

        topbar.dataset.fixed = '1';
        parent.document.body.insertBefore(topbar, parent.document.body.firstChild);
        parent.document.body.insertBefore(navBar, topbar.nextSibling);

        var main = parent.document.querySelector('[data-testid="stAppViewContent"]');
        if (main) main.style.paddingTop = '100px';

        // 侧边栏固定宽度 280px
        topbar.style.left = '280px';
        navBar.style.left = '280px';
      }

      setupFixedHeader();
      setTimeout(setupFixedHeader, 500);
      setTimeout(setupFixedHeader, 1000);
    })();
    </script>
    """, height=0)


def main():
    st.set_page_config(
        page_title="Performance Review",
        page_icon="favicon.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(get_css(), unsafe_allow_html=True)

    # ─── 顶部栏 ─────────────────────────────────────────
    today_str = date.today().strftime("%Y-%m-%d")
    render_topbar(today_str)

    # ─── 导航栏 ─────────────────────────────────────────
    render_nav()

    # ─── 固定 header JS ──────────────────────────────────
    render_fixed_header_js()

    # ─── 侧边栏：文件上传 ────────────────────────────────
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
            value=50000,
            step=1000,
            help="本周每日目标触达人次",
        )

    # ─── 数据读取 ─────────────────────────────────────────
    if uploaded is not None:
        raw_df = read_data(uploaded)
    else:
        st.info("请在左侧上传 Excel 或 CSV 数据文件")
        return

    if raw_df is None or raw_df.empty:
        st.error("数据文件读取失败或为空")
        return

    # ─── 侧边栏：日期范围（根据数据自动限定）─────────────────
    data_min = raw_df["发送日期"].min().date()
    data_max = raw_df["发送日期"].max().date()

    # 默认上一个自然周（周一~周日）
    today = date.today()
    days_since_monday = today.weekday()
    default_end = today - timedelta(days=days_since_monday + 1)  # 上周日
    default_start = default_end - timedelta(days=6)               # 上周一
    # 确保不超出数据范围
    default_start = max(default_start, data_min)
    default_end = min(default_end, data_max)

    with st.sidebar:
        st.markdown("---")
        st.markdown("##### 日期范围")
        start_date = st.date_input("开始日期", value=default_start, min_value=data_min, max_value=data_max)
        end_date = st.date_input("结束日期", value=default_end, min_value=data_min, max_value=data_max)

    df = filter_week_data(raw_df, start_date, end_date)
    if df.empty:
        st.warning(f"所选日期范围 [{start_date} ~ {end_date}] 内无数据")
        return

    # 计算综合评分
    df = compute_scores(df)

    # ─── 维度筛选（需数据加载后才有选项）─────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("##### 维度筛选")

        channels = sorted(df["渠道"].dropna().unique().tolist()) if "渠道" in df.columns else []
        plan_types = sorted(df["计划类型"].dropna().unique().tolist()) if "计划类型" in df.columns else []
        bus = sorted(df["预算owner"].dropna().unique().tolist()) if "预算owner" in df.columns else []

        selected_channels = st.multiselect("渠道", channels, default=channels)
        selected_plan_types = st.multiselect("计划类型", plan_types, default=plan_types)
        selected_bus = st.multiselect("预算 Owner (BU)", bus, default=bus)

    if selected_channels:
        df = df[df["渠道"].isin(selected_channels)]
    if selected_plan_types:
        df = df[df["计划类型"].isin(selected_plan_types)]
    if selected_bus:
        df = df[df["预算owner"].isin(selected_bus)]

    if df.empty:
        st.warning("筛选后无数据，请调整筛选条件")
        return

    # ─── 主体内容（单页滚动，4个 section）─────────────────────
    st.markdown('<div id="sec-summary"></div>', unsafe_allow_html=True)
    render_summary(df, target_dau)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div id="sec-operational"></div>', unsafe_allow_html=True)
    render_operational(df, target_dau)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div id="sec-bu"></div>', unsafe_allow_html=True)
    render_bu(df)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div id="sec-plan"></div>', unsafe_allow_html=True)
    render_plan(df)


if __name__ == "__main__":
    main()
