"""
app.py - CNN Performance Weekly 主入口
"""

import base64
from pathlib import Path

import streamlit as st
from datetime import date, timedelta

from config import MCD_RED, MCD_GOLD, API_PROVIDERS, CHANNELS
from tabs.tab_plan import PLAN_CHANNELS
from data import read_data, filter_week_data
from scoring import compute_scores
from styles import get_css
from tabs.tab_summary import render as render_summary
from tabs.tab_operational import render as render_operational
from tabs.tab_bu import render as render_bu
from tabs.tab_plan import render as render_plan
from export import generate_html
from llm_service import analyze_content, analyze_channel_summary


def render_topbar():
    """渲染顶部栏"""
    logo_path = Path(__file__).parent / "mcdonalds.png"
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()

    st.markdown(f"""
    <div class="topbar">
      <div class="topbar-left">
        <img src="data:image/png;base64,{logo_b64}" class="topbar-logo-img" alt="McDonald's">
        <div class="topbar-title">
          <h1>Performance Review</h1>
          <div class="sub">周度数据复盘看板</div>
        </div>
      </div>
      <div class="topbar-right">
        <span class="topbar-badge">Weekly Report</span><br>
        McDonald's China &middot; IT Operating &middot; Traffic
      </div>
    </div>
    """, unsafe_allow_html=True)


def update_topbar_badge(text: str):
    """用 JS 更新顶部栏 badge 文字"""
    import streamlit.components.v1 as components
    components.html(f"""
    <script>
    (function() {{
      var badge = parent.document.querySelector('.topbar-badge');
      if (badge) badge.textContent = '{text}';
    }})();
    </script>
    """, height=0)


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
    import streamlit.components.v1 as components  # noqa: E402 — Streamlit lazy init
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

    # ─── 顶部栏 + 导航栏 ──────────────────────────────────
    render_topbar()
    render_nav()
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

    # 更新顶部栏 badge 显示所选日期范围
    update_topbar_badge(f"{start_date} ~ {end_date}")

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

    # ─── 侧边栏：AI 配置（折叠）─────────────────────────────
    with st.sidebar:
        st.markdown("---")
        with st.expander("AI 解读配置", expanded=False):
            ai_provider = st.selectbox("AI 服务商", options=list(API_PROVIDERS.keys()), index=0)
            ai_models = API_PROVIDERS[ai_provider]["models"]
            ai_model = st.selectbox("模型", options=ai_models, index=0)
            ai_api_key = st.text_input(
                "API Key",
                value=API_PROVIDERS[ai_provider].get("api_key", ""),
                type="password",
            )

        if st.button("✨ AI 分析", use_container_width=True):
            # 按渠道×维度分批，每个渠道3个维度×4条
            df_ai = df.copy()
            if "消息内容" in df_ai.columns:
                from tabs.tab_plan import _parse_message_content
                parsed = df_ai["消息内容"].apply(_parse_message_content)
                df_ai["消息标题"] = parsed.apply(lambda x: x[0])
                df_ai["消息内容_parsed"] = parsed.apply(lambda x: x[1])

            ai_results = st.session_state.get("ai_results", {})
            channel_summary = st.session_state.get("channel_summary", {})
            ch_count = 0

            # 3个排序维度
            DIMS = [
                ("score", "综合评分"),
                ("ctr", "CTR"),
                ("sales", "订单Sales"),
            ]

            for ch in PLAN_CHANNELS:
                ch_df = df_ai[df_ai["渠道"] == ch]
                if len(ch_df) < 2:
                    continue
                agg = {
                    "Plan名称": "first",
                    "触达成功": "sum",
                    "点击人次": "sum",
                    "订单GC": "sum",
                    "综合评分": "mean",
                    "CTR": "mean",
                    "GC转化率": "mean",
                    "消息标题": "first",
                }
                if "消息内容_parsed" in ch_df.columns:
                    agg["消息内容_parsed"] = "first"
                elif "消息内容" in ch_df.columns:
                    agg["消息内容"] = "first"
                if "订单Sales" in ch_df.columns:
                    agg["订单Sales"] = "sum"

                plan_agg = ch_df.groupby("Plan ID").agg(agg).reset_index()
                plan_agg = plan_agg[plan_agg["触达成功"] > 0]
                if len(plan_agg) < 2:
                    continue

                # 过滤掉被删除的Plan
                deleted = st.session_state.get("deleted_plans", set())
                plan_agg = plan_agg[~plan_agg["Plan ID"].isin(deleted)]

                # 渠道总结：取综合评分TOP4
                summary_top = plan_agg.sort_values("综合评分", ascending=False).head(4)
                summary_items = []
                for _, row in summary_top.iterrows():
                    msg_col = "消息内容_parsed" if "消息内容_parsed" in row.index else "消息内容"
                    content = str(row.get(msg_col, "")).strip() if msg_col in row.index else ""
                    summary_items.append({
                        "标题": str(row.get("消息标题", "")),
                        "内容": content[:200],
                        "触达成功": int(row["触达成功"]),
                        "CTR": float(row["CTR"]),
                        "订单GC": int(row["订单GC"]),
                        "订单Sales": float(row.get("订单Sales", 0)),
                        "综合评分": float(row["综合评分"]),
                    })

                with st.spinner(f"AI 正在生成 {ch} 渠道总结..."):
                    ch_summary = analyze_channel_summary(ai_api_key, ai_provider, ai_model, ch, summary_items)
                channel_summary[ch] = ch_summary

                for dim_id, sort_col in DIMS:
                    if sort_col in plan_agg.columns:
                        dim_top = plan_agg.sort_values(sort_col, ascending=False).head(4)
                    else:
                        dim_top = plan_agg.sort_values("综合评分", ascending=False).head(4)

                    items = []
                    keys = []
                    for rank, (_, row) in enumerate(dim_top.iterrows(), 1):
                        msg_col = "消息内容_parsed" if "消息内容_parsed" in row.index else "消息内容"
                        content = str(row.get(msg_col, "")).strip() if msg_col in row.index else ""
                        items.append({
                            "标题": str(row.get("消息标题", "")),
                            "内容": content[:200],
                            "渠道": ch,
                            "触达成功": int(row["触达成功"]),
                            "点击人次": int(row["点击人次"]),
                            "CTR": float(row["CTR"]),
                            "订单GC": int(row["订单GC"]),
                            "订单GC转化率": float(row["GC转化率"]),
                            "综合评分": float(row["综合评分"]),
                            "排名": rank,
                        })
                        keys.append(f"{row['Plan ID']}_{ch}_{dim_id}")

                    with st.spinner(f"AI 正在分析 {ch} - {dim_id}（{len(items)} 条）..."):
                        results = analyze_content(ai_api_key, ai_provider, ai_model, items)
                    ai_results.update(dict(zip(keys, results)))
                    ch_count += 1

            if ch_count > 0:
                st.session_state["ai_results"] = ai_results
                st.session_state["channel_summary"] = channel_summary
                st.rerun()
            else:
                st.warning("没有可分析的 Plan 数据")

    # ─── 主体内容（单页滚动，4个 section）─────────────────────
    st.markdown('<div id="sec-summary"></div>', unsafe_allow_html=True)
    summary_figs, summary_kpis = render_summary(df, target_dau)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div id="sec-operational"></div>', unsafe_allow_html=True)
    op_figs, op_kpis, op_detail_html = render_operational(df, target_dau)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div id="sec-bu"></div>', unsafe_allow_html=True)
    bu_figs, bu_table_html = render_bu(df)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div id="sec-plan"></div>', unsafe_allow_html=True)
    ai_results = st.session_state.get("ai_results", {})
    channel_summary = st.session_state.get("channel_summary", {})
    plan_html = render_plan(df, ai_results=ai_results, channel_summary=channel_summary)

    # ─── 导出 HTML 按钮 ──────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("##### 导出分享")

        figs = {
            "summary": summary_figs,
            "operational": op_figs,
            "bu": bu_figs,
        }
        kpis = {
            "summary": summary_kpis,
            "operational": op_kpis,
        }
        tables = {
            "operational": op_detail_html,
            "bu": bu_table_html,
            "plan": plan_html,
        }

        html_content = generate_html(df, target_dau, figs, tables, kpis, period_str=f"{start_date} ~ {end_date}", channel_summary=channel_summary)
        today_str = date.today().strftime("%Y%m%d")
        st.download_button(
            label="下载 HTML 看板",
            data=html_content,
            file_name=f"performance_review_{today_str}.html",
            mime="text/html",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
