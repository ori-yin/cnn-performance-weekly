"""
tab_plan.py - 第四层：Plan 分析
每个渠道 Top 3 + Bottom 3，综合评分，含文案标题和正文
"""

import json
import re
import streamlit as st
import pandas as pd
from config import MCD_RED, MCD_GOLD, MCD_GREEN, CHANNELS
from components import section_header

# Plan分析渠道列表（排除短信，领导要求保留备用）
PLAN_CHANNELS = [ch for ch in CHANNELS if ch != "短信"]


def _parse_message_content(raw):
    """
    解析消息内容 JSON，提取标题和正文。
    参考 mcd-content-rank 的 data_cleaning.py。
    """
    if pd.isna(raw) or not isinstance(raw, str):
        return "", ""

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return "", ""

    title = data.get("title", "")
    text = data.get("text", "")

    # 从 forms 中提取
    if not title and "forms" in data:
        for item in data["forms"]:
            if item.get("code") == "thing1" and item.get("value"):
                title = item["value"]
                break
    if not text and "forms" in data:
        for item in data["forms"]:
            code = item.get("code", "")
            if code in ["thing5", "short_thing5"] and item.get("value"):
                text = item["value"]
                break

    # 兜底
    if not title and text:
        first_part = re.split(r'[。！？\n]', str(text).strip())[0].strip()
        title = first_part if first_part else str(text)[:20]

    title = str(title).strip().replace('\r\n', '').replace('\n', '')
    text = str(text).strip().replace('\r\n', '').replace('\n', '')

    return title, text


def _plan_card_html(row: pd.Series, rank: int, is_good: bool, ai_result: dict = None) -> str:
    """生成单个 Plan 卡片的 HTML，可选 AI 解读"""
    medal_map = {1: "🥇", 2: "🥈", 3: "🥉"}
    medal = medal_map.get(rank, f'<span style="color:#999;font-size:11px;">{rank}.</span>')

    score = row.get("综合评分", 0)
    score_color = MCD_GREEN if score >= 75 else (MCD_GOLD if score >= 60 else MCD_RED)

    plan_name = str(row.get("Plan名称", "—"))
    if len(plan_name) > 50:
        plan_name = plan_name[:50] + "..."

    plan_id = str(row.get("Plan ID", ""))
    bu = str(row.get("预算owner", "—"))
    send_date = str(row.get("发送日期", ""))
    if send_date and len(send_date) > 10:
        send_date = send_date[:10]

    msg_title = str(row.get("消息标题", "")).strip()
    msg_text = str(row.get("消息内容", "")).strip()

    # 文案区域（无边框，直接展示）
    msg_html = ""
    if msg_title:
        msg_html += f'<div style="font-weight:600;color:#2b2620;font-size:12px;margin-top:6px;">{msg_title}</div>'
    if msg_text:
        display_text = msg_text[:100] + "..." if len(msg_text) > 100 else msg_text
        msg_html += f'<div style="color:#888;font-size:12px;line-height:1.5;margin-top:2px;">{display_text}</div>'

    # 数据豆腐块（药丸样式，参考 mcd-content-rank）
    metrics = [
        ("触达", f'{int(row.get("触达成功", 0)):,}'),
        ("点击", f'{int(row.get("点击人次", 0)):,}'),
        ("CTR", f'{row.get("CTR", 0):.2f}%'),
        ("GC", f'{int(row.get("订单GC", 0)):,}'),
        ("GC率", f'{row.get("GC转化率", 0):.1f}%'),
        ("Sales", f'{row.get("订单Sales", 0):,.2f}'),
    ]
    metrics_html = ""
    for label, val in metrics:
        metrics_html += (
            f'<span style="background:#F8F7F5;padding:3px 10px;border-radius:6px;font-size:12px;color:#888;font-weight:500;">'
            f'{label} {val}</span>'
        )

    return (
        f'<div style="background:#fff;border:1px solid #e4d9bf;border-radius:10px;padding:14px 16px;margin-bottom:10px;">'
        f'<div style="display:flex;align-items:center;gap:6px;font-size:12px;margin-bottom:6px;">'
        f'<span>{medal}</span>'
        f'<span style="color:#5a5048;">{plan_id}</span>'
        f'<span style="color:#ccc;">·</span>'
        f'<span style="color:#5a5048;">{bu}</span>'
        f'<span style="color:#ccc;">·</span>'
        f'<span style="color:#999;">{send_date}</span>'
        f'<span style="margin-left:auto;font-size:16px;font-weight:800;color:{score_color};">{score:.0f}</span>'
        f'</div>'
        f'<div style="font-size:13px;font-weight:700;color:#2b2620;margin-bottom:4px;">{plan_name}</div>'
        f'{msg_html}'
        f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">'
        f'{metrics_html}'
        f'</div>'
        f'{_ai_inline_html(ai_result)}'
        f'</div>'
    )


def _ai_inline_html(ai_result: dict = None) -> str:
    """生成卡片内 AI 解读折叠区域 HTML"""
    if not ai_result:
        return ""
    if "error" in ai_result:
        return (
            f'<details style="margin-top:8px;">'
            f'<summary style="font-size:12px;font-weight:600;color:#c00;cursor:pointer;">⚠ AI 解读失败</summary>'
            f'<div style="background:#F8F7F5;border-radius:6px;padding:10px 12px;margin-top:4px;">'
            f'<div style="font-size:12px;color:#c00;">{ai_result["error"]}</div>'
            f'</div></details>'
        )
    return (
        f'<details style="margin-top:8px;">'
        f'<summary style="font-size:12px;font-weight:600;color:#a8001a;cursor:pointer;">✨ AI 解读</summary>'
        f'<div style="background:#F8F7F5;border-radius:6px;padding:10px 12px;margin-top:4px;">'
        f'<div style="font-size:12px;color:#5a5048;line-height:1.7;">'
        f'核心亮点/问题：{ai_result.get("core_issue", "—")}<br>'
        f'可借鉴点：{ai_result.get("highlight", "—")}<br>'
        f'改进方向：{ai_result.get("weakness", "—")}<br>'
        f'可复用/可优化：{ai_result.get("action", "—")}'
        f'</div></div></details>'
    )


def _aggregate_plans(ch_df: pd.DataFrame) -> pd.DataFrame:
    """按 Plan 聚合单个渠道的数据"""
    agg_dict = {
        "Plan名称": "first",
        "预算owner": "first",
        "发送日期": "first",
        "触达成功": "sum",
        "点击人次": "sum",
        "订单GC": "sum",
        "综合评分": "mean",
        "CTR": "mean",
        "GC转化率": "mean",
        "消息标题": "first",
        "消息内容": "first",
    }
    if "订单Sales" in ch_df.columns:
        agg_dict["订单Sales"] = "sum"
    plan_agg = ch_df.groupby("Plan ID").agg(agg_dict).reset_index()
    plan_agg = plan_agg[plan_agg["触达成功"] > 0]
    return plan_agg


def _render_plan_cards(top_n: pd.DataFrame, ch: str, ai_results: dict = None):
    """Streamlit 渲染 TOP4 卡片（两列）"""
    col_l, col_r = st.columns(2)
    rows_list = list(top_n.iterrows())
    with col_l:
        for i, (_, row) in enumerate(rows_list[:2], 1):
            ai_key = f"{row['Plan ID']}_{ch}"
            ai = ai_results.get(ai_key) if ai_results else None
            st.markdown(_plan_card_html(row, i, is_good=True, ai_result=ai), unsafe_allow_html=True)
    with col_r:
        for i, (_, row) in enumerate(rows_list[2:4], 3):
            ai_key = f"{row['Plan ID']}_{ch}"
            ai = ai_results.get(ai_key) if ai_results else None
            st.markdown(_plan_card_html(row, i, is_good=True, ai_result=ai), unsafe_allow_html=True)


def _export_plan_cards(top_n: pd.DataFrame, ch: str, ai_results: dict = None) -> str:
    """导出 HTML：TOP4 卡片（两列）"""
    rows_list = list(top_n.iterrows())
    html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">'
    html += '<div>'
    for i, (_, row) in enumerate(rows_list[:2], 1):
        ai_key = f"{row['Plan ID']}_{ch}"
        ai = ai_results.get(ai_key) if ai_results else None
        html += _plan_card_html(row, i, is_good=True, ai_result=ai)
    html += '</div><div>'
    for i, (_, row) in enumerate(rows_list[2:4], 3):
        ai_key = f"{row['Plan ID']}_{ch}"
        ai = ai_results.get(ai_key) if ai_results else None
        html += _plan_card_html(row, i, is_good=True, ai_result=ai)
    html += '</div></div>'
    return html


def _export_channel_tabs(ch: str, plan_agg: pd.DataFrame, ai_results: dict = None) -> str:
    """导出 HTML：单个渠道的 3 个维度 tab 切换"""
    prefix = ch.replace(" ", "-").replace("/", "-")
    dims = [
        ("score", "综合评分", "综合评分"),
        ("ctr", "CTR", "CTR"),
        ("sales", "Sales", "订单Sales"),
    ]
    tabs_html = ""
    panels_html = ""
    for idx, (dim_id, label, sort_col) in enumerate(dims):
        checked = "checked" if idx == 0 else ""
        tabs_html += (
            f'<input type="radio" name="dim-{prefix}" id="dim-{prefix}-{dim_id}" {checked} class="plan-dim-input">'
            f'<label for="dim-{prefix}-{dim_id}" class="plan-tab-label">{label}</label>'
        )
        if sort_col in plan_agg.columns:
            sorted_df = plan_agg.sort_values(sort_col, ascending=False).head(4).reset_index(drop=True)
        else:
            sorted_df = plan_agg.sort_values("综合评分", ascending=False).head(4).reset_index(drop=True)
        panels_html += f'<div class="plan-dim-panel">{_export_plan_cards(sorted_df, ch, ai_results)}</div>'
    return f'<div class="plan-dim-tabs">{tabs_html}{panels_html}</div>'


def render(df: pd.DataFrame, ai_results: dict = None):
    """渲染 Plan 分析层，返回 plan_html 供导出用"""

    st.markdown(section_header("Plan 分析", ""), unsafe_allow_html=True)

    if "综合评分" not in df.columns:
        st.warning("数据中缺少综合评分，请检查评分算法")
        return ""

    # 预处理：解析消息内容 JSON → 标题 + 正文
    if "消息内容" in df.columns:
        df = df.copy()
        parsed = df["消息内容"].apply(_parse_message_content)
        df["消息标题"] = parsed.apply(lambda x: x[0])
        df["消息内容"] = parsed.apply(lambda x: x[1])
    elif "消息标题" not in df.columns:
        df = df.copy()
        df["消息标题"] = ""
        df["消息内容"] = ""

    # 检测可用渠道（至少 2 条 Plan）
    available_channels = []
    for ch in PLAN_CHANNELS:
        ch_df = df[df["渠道"] == ch]
        if len(ch_df) >= 2:
            plan_agg = _aggregate_plans(ch_df)
            if len(plan_agg) >= 2:
                available_channels.append(ch)

    if not available_channels:
        st.info("当前筛选条件下没有足够的 Plan 数据进行分析")
        return ""

    # ─── 渠道 + 维度选择器（左右横排）─────────────────────
    col_ch, col_dim = st.columns(2)
    with col_ch:
        selected_ch = st.radio("渠道", options=available_channels, index=0, horizontal=True, key="plan_ch")
    with col_dim:
        sort_dim = st.radio("排序", options=["综合评分", "CTR", "Sales"], index=0, horizontal=True, key="plan_dim")

    # 按选中维度排序
    ch_df = df[df["渠道"] == selected_ch].copy()
    plan_agg = _aggregate_plans(ch_df)

    if sort_dim == "综合评分":
        plan_agg = plan_agg.sort_values("综合评分", ascending=False)
    elif sort_dim == "CTR":
        plan_agg = plan_agg.sort_values("CTR", ascending=False)
    elif sort_dim == "Sales":
        if "订单Sales" in plan_agg.columns:
            plan_agg = plan_agg.sort_values("订单Sales", ascending=False)
        else:
            plan_agg = plan_agg.sort_values("综合评分", ascending=False)

    top4 = plan_agg.head(4).reset_index(drop=True)

    # ─── Streamlit 显示 ──────────────────────────────────
    _render_plan_cards(top4, selected_ch, ai_results)

    # ─── 导出 HTML（渠道 tab + 维度 tab，扁平结构）──────────
    plan_html = ""
    ch_tabs = ""
    ch_panels = ""
    for idx, ch in enumerate(available_channels):
        ch_df_exp = df[df["渠道"] == ch].copy()
        plan_agg_exp = _aggregate_plans(ch_df_exp)
        checked = "checked" if idx == 0 else ""
        ch_tabs += (
            f'<input type="radio" name="plan-ch" id="plan-ch-{idx}" {checked} class="plan-ch-input">'
            f'<label for="plan-ch-{idx}" class="plan-tab-label">{ch}</label>'
        )
        ch_panels += f'<div class="plan-ch-panel">{_export_channel_tabs(ch, plan_agg_exp, ai_results)}</div>'
    plan_html += f'<div class="plan-ch-tabs">{ch_tabs}{ch_panels}</div>'

    return plan_html
