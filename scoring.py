"""
scoring.py - CNN Performance Weekly：综合评分算法
参考 mcd-content-rank 的评分体系
"""

import numpy as np
import pandas as pd
from config import (
    CTR_THRESHOLDS, GC_THRESHOLDS,
    CTR_UNKNOWN_THRESHOLD, GC_UNKNOWN_THRESHOLD,
    SCORING_EXP, W_REACH, W_CTR, W_GC,
    CONFIDENCE_THRESHOLDS, CONFIDENCE_DEFAULT,
)


def _piecewise_score(value: float, threshold: float, exp: float = SCORING_EXP) -> float:
    """
    分段评分函数：
    - value < threshold: score = 100 × (value / threshold)^exp
    - value >= threshold: score = 100
    """
    if threshold <= 0 or pd.isna(value) or value < 0:
        return 0.0
    if value >= threshold:
        return 100.0
    return 100.0 * (value / threshold) ** exp


def _confidence_penalty(reach: float) -> float:
    """置信度惩罚：触达规模越小，惩罚越重"""
    if pd.isna(reach) or reach <= 0:
        return 0.0
    for threshold, penalty in CONFIDENCE_THRESHOLDS:
        if reach < threshold:
            return penalty
    return CONFIDENCE_DEFAULT


def _reach_score(reach: float, max_reach: float) -> float:
    """触达规模得分：幂次归一化"""
    if pd.isna(reach) or max_reach <= 0:
        return 0.0
    return 100.0 * (reach / max_reach) ** 0.3


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    为每个 Plan 计算综合评分。

    输入 df 需包含：渠道、触达成功、点击人次、订单GC
    输出新增列：CTR得分、GC得分、触达得分、综合评分
    """
    df = df.copy()

    # 最大触达（用于归一化）
    max_reach = df["触达成功"].max() if len(df) > 0 else 1
    if max_reach <= 0:
        max_reach = 1

    def _score_row(row):
        channel = row.get("渠道", "")
        ctr = row.get("CTR", 0)
        gc_rate = row.get("GC转化率", 0)
        reach = row.get("触达成功", 0)

        # 渠道阈值
        ctr_threshold = CTR_THRESHOLDS.get(channel, CTR_UNKNOWN_THRESHOLD)
        gc_threshold = GC_THRESHOLDS.get(channel, GC_UNKNOWN_THRESHOLD)

        # 分项得分
        ctr_score = _piecewise_score(ctr, ctr_threshold)
        gc_score = _piecewise_score(gc_rate, gc_threshold)
        reach_score = _reach_score(reach, max_reach)

        # 加权
        raw_score = (
            W_REACH * reach_score
            + W_CTR * ctr_score
            + W_GC * gc_score
        )

        # 置信度惩罚
        penalty = _confidence_penalty(reach)
        final_score = raw_score * penalty

        return pd.Series({
            "触达得分": round(reach_score, 1),
            "CTR得分": round(ctr_score, 1),
            "GC得分": round(gc_score, 1),
            "综合评分": round(final_score, 1),
        })

    score_cols = df.apply(_score_row, axis=1)
    df = pd.concat([df, score_cols], axis=1)

    return df


def get_status(actual: float, target: float) -> str:
    """
    根据达成率返回状态色。
    - green: 达成 (>= 95%)
    - yellow: 落后 5-15% (85% ~ 95%)
    - red: 落后 15%+ (< 85%)
    """
    if target <= 0 or pd.isna(actual):
        return "gray"
    ratio = actual / target
    if ratio >= 0.95:
        return "green"
    elif ratio >= 0.85:
        return "yellow"
    else:
        return "red"
