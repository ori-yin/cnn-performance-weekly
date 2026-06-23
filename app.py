"""
app.py - CNN Performance Weekly：Streamlit 主入口
"""

import sys
import os
import streamlit as st
import pandas as pd

# 确保项目根目录在 path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import MCD_RED, MCD_GOLD, CHANNELS
from data import read_data, filter_week_data
from scoring import compute_scores
from styles import get_css

# ─── 页面配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="CNN Performance Weekly",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 注入全局 CSS
st.markdown(get_css(), unsafe_allow_html=True)


# ─── 侧边栏 ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="font-size:20px;font-weight:800;color:{MCD_RED};margin-bottom:4px;">CNN Performance Weekly</div>'
        f'<div style="font-size:12px;color:#999;margin-bottom:20px;">周度数据复盘看板</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 文件上传
    uploaded_file = st.file_uploader(
        "上传数据文件",
        type=["csv", "xlsx"],
        help="支持 CSV / XLSX 格式",
    )

    # Target 输入
    target_dau = st.number_input(
        "DAU Target（日均）",
        min_value=0,
        value=0,
        step=1000,
        help="输入日均 DAU 目标值（点击人次）",
    )

    st.markdown("---")

    # 筛选器（数据加载后显示）
    filter_channel = None
    filter_plan_type = None
    filter_owner = None
    filter_date_range = None

    if uploaded_file is not None:
        st.markdown(
            '<div style="font-size:13px;font-weight:700;color:#1a1a1a;margin-bottom:12px;'
            'padding-bottom:6px;border-bottom:2px solid #DA291C;">筛选条件</div>',
            unsafe_allow_html=True,
        )

        # 读取数据（缓存）
        @st.cache_data
        def load_data(file_bytes, file_name):
            """缓存数据读取"""
            import io
            fake_file = io.BytesIO(file_bytes)
            fake_file.name = file_name
            return read_data(fake_file)

        try:
            df_all = load_data(uploaded_file.getvalue(), uploaded_file.name)

            # 日期筛选
            valid_dates = df_all["发送日期"].dropna()
            if len(valid_dates) > 0:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()

                st.markdown(
                    '<div style="font-size:11px;font-weight:600;color:#888;'
                    'margin-bottom:4px;letter-spacing:0.05em;">日期范围</div>',
                    unsafe_allow_html=True,
                )

                col1, col2 = st.columns(2)
                with col1:
                    date_start = st.date_input("开始", value=min_date, min_value=min_date, max_value=max_date)
                with col2:
                    date_end = st.date_input("结束", value=max_date, min_value=min_date, max_value=max_date)

                filter_date_range = (pd.Timestamp(date_start), pd.Timestamp(date_end))

            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

            # 渠道筛选
            available_channels = sorted(df_all["渠道"].dropna().unique().tolist())
            filter_channel = st.multiselect(
                "渠道",
                options=available_channels,
                default=available_channels,
            )

            # 计划类型筛选
            available_types = sorted(df_all["计划类型"].dropna().unique().tolist())
            filter_plan_type = st.multiselect(
                "计划类型",
                options=available_types,
                default=available_types,
            )

            # BU 筛选
            available_owners = sorted(df_all["预算owner"].dropna().unique().tolist())
            filter_owner = st.multiselect(
                "BU（预算owner）",
                options=available_owners,
                default=available_owners,
            )

        except Exception as e:
            st.error(f"数据读取失败: {e}")
            df_all = None
    else:
        df_all = None


# ─── 主区域 ──────────────────────────────────────────────
if df_all is None:
    # 未上传文件时的引导页
    st.markdown(
        f"""
        <div style="text-align:center;padding:120px 40px;">
            <div style="font-size:48px;margin-bottom:16px;">📊</div>
            <div style="font-size:24px;font-weight:700;color:#1a1a1a;margin-bottom:8px;">
                CNN Performance Weekly
            </div>
            <div style="font-size:14px;color:#999;">
                请在左侧上传数据文件（CSV / XLSX），并输入 DAU Target
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ─── 应用筛选 ──────────────────────────────────────────────
df = df_all.copy()
if filter_date_range:
    df = df[(df["发送日期"] >= filter_date_range[0]) & (df["发送日期"] <= filter_date_range[1])]
if filter_channel:
    df = df[df["渠道"].isin(filter_channel)]
if filter_plan_type:
    df = df[df["计划类型"].isin(filter_plan_type)]
if filter_owner:
    df = df[df["预算owner"].isin(filter_owner)]

# ─── 计算综合评分 ──────────────────────────────────────
df = compute_scores(df)

# ─── 页面标题 ──────────────────────────────────────────────
st.markdown(
    f'<div style="font-size:28px;font-weight:800;color:#1a1a1a;margin-bottom:4px;">'
    f'CNN Performance Weekly</div>'
    f'<div style="font-size:13px;color:#999;margin-bottom:24px;">'
    f'周度数据复盘 · 聚焦 Operational</div>',
    unsafe_allow_html=True,
)

# ─── 加载 Tab 模块 ──────────────────────────────────────
from tabs.tab_summary import render as render_summary
from tabs.tab_operational import render as render_operational
from tabs.tab_bu import render as render_bu
from tabs.tab_plan import render as render_plan

# ─── 渲染各层 ──────────────────────────────────────────────
render_summary(df, target_dau)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

render_operational(df, target_dau)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

render_bu(df)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

render_plan(df)
