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


def _render_plan_card(row: pd.Series, rank: int, is_good: bool):
    """渲染单个 Plan 卡片，文案直接显示"""
    border_color = MCD_GREEN if is_good else MCD_RED
    tag = "Top" if is_good else "Bottom"
    tag_color = MCD_GREEN if is_good else MCD_RED

    score = row.get("综合评分", 0)
    score_color = MCD_GREEN if score >= 75 else (MCD_GOLD if score >= 60 else MCD_RED)

    plan_name = str(row.get("Plan名称", "—"))
    if len(plan_name) > 50:
        plan_name = plan_name[:50] + "..."

    msg_title = str(row.get("消息标题", "")).strip()
    msg_text = str(row.get("消息内容", "")).strip()

    # 文案区域
    msg_html = ""
    if msg_title or msg_text:
        msg_html = (
            f'<div style="margin-top:8px;padding:8px 10px;background:#FAFAFA;border-radius:6px;'
            f'border-left:2px solid #E0E0E0;font-size:12px;line-height:1.5;">'
        )
        if msg_title:
            msg_html += f'<div style="font-weight:600;color:#1a1a1a;margin-bottom:2px;">{msg_title}</div>'
        if msg_text:
            display_text = msg_text[:100] + "..." if len(msg_text) > 100 else msg_text
            msg_html += f'<div style="color:#666;">{display_text}</div>'
        msg_html += '</div>'

    st.markdown(
        f'<div style="background:#fff;border:1px solid #E8E8E8;border-left:3px solid {border_color};'
        f'border-radius:8px;padding:12px 16px;margin-bottom:8px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<div>'
        f'<span style="font-size:11px;font-weight:600;color:{tag_color};">{tag} {rank}</span>'
        f'<span style="font-size:11px;color:#999;margin-left:8px;">{row.get("Plan ID", "")}</span>'
        f'</div>'
        f'<div style="font-size:18px;font-weight:800;color:{score_color};">{score:.0f}</div>'
        f'</div>'
        f'<div style="font-size:13px;font-weight:600;margin:6px 0 2px;">{plan_name}</div>'
        f'<div style="font-size:12px;color:#666;">'
        f'BU: {row.get("预算owner", "—")} · '
        f'触达 {int(row.get("触达成功", 0)):,} · '
        f'点击 {int(row.get("点击人次", 0)):,} · '
        f'CTR {row.get("CTR", 0):.2f}% · '
        f'GC率 {row.get("GC转化率", 0):.1f}% · '
        f'Sales {row.get("订单Sales", 0):,.2f}'
        f'</div>'
        f'{msg_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _generate_plan_card_html(row: pd.Series, rank: int, is_good: bool) -> str:
    """生成单个 Plan 卡片的 HTML（供导出用）"""
    border_color = MCD_GREEN if is_good else MCD_RED
    tag = "Top" if is_good else "Bottom"
    tag_color = MCD_GREEN if is_good else MCD_RED

    score = row.get("综合评分", 0)
    score_color = MCD_GREEN if score >= 75 else (MCD_GOLD if score >= 60 else MCD_RED)

    plan_name = str(row.get("Plan名称", "—"))
    if len(plan_name) > 50:
        plan_name = plan_name[:50] + "..."

    msg_title = str(row.get("消息标题", "")).strip()
    msg_text = str(row.get("消息内容", "")).strip()

    msg_html = ""
    if msg_title or msg_text:
        msg_html = (
            f'<div style="margin-top:8px;padding:8px 10px;background:#FAFAFA;border-radius:6px;'
            f'border-left:2px solid #E0E0E0;font-size:12px;line-height:1.5;">'
        )
        if msg_title:
            msg_html += f'<div style="font-weight:600;color:#1a1a1a;margin-bottom:2px;">{msg_title}</div>'
        if msg_text:
            display_text = msg_text[:100] + "..." if len(msg_text) > 100 else msg_text
            msg_html += f'<div style="color:#666;">{display_text}</div>'
        msg_html += '</div>'

    return (
        f'<div style="background:#fff;border:1px solid #E8E8E8;border-left:3px solid {border_color};'
        f'border-radius:8px;padding:12px 16px;margin-bottom:8px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<div>'
        f'<span style="font-size:11px;font-weight:600;color:{tag_color};">{tag} {rank}</span>'
        f'<span style="font-size:11px;color:#999;margin-left:8px;">{row.get("Plan ID", "")}</span>'
        f'</div>'
        f'<div style="font-size:18px;font-weight:800;color:{score_color};">{score:.0f}</div>'
        f'</div>'
        f'<div style="font-size:13px;font-weight:600;margin:6px 0 2px;">{plan_name}</div>'
        f'<div style="font-size:12px;color:#666;">'
        f'BU: {row.get("预算owner", "—")} · '
        f'触达 {int(row.get("触达成功", 0)):,} · '
        f'点击 {int(row.get("点击人次", 0)):,} · '
        f'CTR {row.get("CTR", 0):.2f}% · '
        f'GC率 {row.get("GC转化率", 0):.1f}% · '
        f'Sales {row.get("订单Sales", 0):,.2f}'
        f'</div>'
        f'{msg_html}'
        f'</div>'
    )


def render(df: pd.DataFrame):
    """渲染 Plan 分析层"""

    st.markdown(section_header("Plan 分析", ""), unsafe_allow_html=True)

    if "综合评分" not in df.columns:
        st.warning("数据中缺少综合评分，请检查评分算法")
        return

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

    has_data = False

    for ch in CHANNELS:
        ch_df = df[df["渠道"] == ch].copy()
        if len(ch_df) < 2:
            continue

        has_data = True

        # 按 Plan 聚合
        agg_dict = {
            "Plan名称": "first",
            "预算owner": "first",
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

        if len(plan_agg) < 2:
            continue

        plan_agg = plan_agg.sort_values("综合评分", ascending=False).reset_index(drop=True)

        top3 = plan_agg.head(3)
        bottom3 = plan_agg.tail(3).iloc[::-1]

        st.markdown(f'<div class="section-subheader">{ch}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f'<div style="font-size:13px;font-weight:600;color:{MCD_GREEN};margin-bottom:8px;">Top 3 Good Case</div>',
                unsafe_allow_html=True,
            )
            for i, (_, row) in enumerate(top3.iterrows(), 1):
                _render_plan_card(row, i, is_good=True)

        with col2:
            st.markdown(
                f'<div style="font-size:13px;font-weight:600;color:{MCD_RED};margin-bottom:8px;">Bottom 3 Bad Case</div>',
                unsafe_allow_html=True,
            )
            for i, (_, row) in enumerate(bottom3.iterrows(), 1):
                _render_plan_card(row, i, is_good=False)

    if not has_data:
        st.info("当前筛选条件下没有足够的 Plan 数据进行分析")

    # ─── 生成 Plan HTML 供导出 ──────────────────────────────
    plan_html = ""
    for ch in CHANNELS:
        ch_df = df[df["渠道"] == ch].copy()
        if len(ch_df) < 2:
            continue

        agg_dict = {
            "Plan名称": "first",
            "预算owner": "first",
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

        if len(plan_agg) < 2:
            continue

        plan_agg = plan_agg.sort_values("综合评分", ascending=False).reset_index(drop=True)
        top3 = plan_agg.head(3)
        bottom3 = plan_agg.tail(3).iloc[::-1]

        plan_html += f'<div class="section-subheader">{ch}</div>'
        plan_html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">'

        # Top 3
        plan_html += '<div>'
        plan_html += f'<div style="font-size:13px;font-weight:600;color:{MCD_GREEN};margin-bottom:8px;">Top 3 Good Case</div>'
        for i, (_, row) in enumerate(top3.iterrows(), 1):
            plan_html += _generate_plan_card_html(row, i, is_good=True)
        plan_html += '</div>'

        # Bottom 3
        plan_html += '<div>'
        plan_html += f'<div style="font-size:13px;font-weight:600;color:{MCD_RED};margin-bottom:8px;">Bottom 3 Bad Case</div>'
        for i, (_, row) in enumerate(bottom3.iterrows(), 1):
            plan_html += _generate_plan_card_html(row, i, is_good=False)
        plan_html += '</div>'

        plan_html += '</div>'

    return plan_html
