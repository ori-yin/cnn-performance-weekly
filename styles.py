"""
styles.py - CNN Performance Weekly：CSS 样式
沿用 mcd-content-rank / mcd-reach-trend 的视觉语言
"""

from config import MCD_RED, MCD_GOLD, MCD_GREEN, MCD_BG, MCD_CARD_BG, MCD_BORDER


def get_css() -> str:
    return f"""
<style>
  /* ─── 顶部 header 只隐藏装饰元素，保留 sidebar toggle ─── */
  /* 注：不隐藏 header，避免误伤 sidebar 展开按钮 */

  /* ─── 全局字体 ─── */
  html, body, .stApp {{
    font-family: 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', sans-serif !important;
    background: {MCD_BG};
    color: #1a1a1a;
  }}

  /* ─── 侧边栏 ─── */
  [data-testid="stSidebar"] {{
    background: #FFFFFF !important;
    border-right: 1px solid #E8E8E8;
    border-top: 3px solid {MCD_GOLD};
  }}

  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] p {{
    color: #1a1a1a !important;
    font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
  }}

  [data-testid="stSidebar"] .stRadio label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label,
  [data-testid="stSidebar"] .stNumberInput label,
  [data-testid="stSidebar"] .stDateInput label {{
    color: #666 !important;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.02em;
    margin-bottom: 4px;
  }}

  [data-testid="stSidebar"] hr {{
    border-color: #EFEFEF !important;
    margin: 16px 0;
  }}

  [data-testid="stSidebar"] .stSelectbox > div > div,
  [data-testid="stSidebar"] .stTextInput > div > div,
  [data-testid="stSidebar"] .stNumberInput > div > div,
  [data-testid="stSidebar"] .stDateInput > div > div {{
    background: #FFFFFF !important;
    border: 1px solid #E0E0E0 !important;
    border-radius: 6px !important;
    color: #1a1a1a !important;
  }}

  /* ─── Sidebar multiselect 样式 ─── */
  [data-testid="stSidebar"] [data-baseweb="tag"] {{
    background-color: #FFF0EE !important;
    border: 1px solid {MCD_RED}40 !important;
    border-radius: 4px !important;
    color: {MCD_RED} !important;
    font-size: 12px !important;
    font-weight: 500 !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="tag"] span {{
    color: {MCD_RED} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"] {{
    border: 1px solid #E0E0E0 !important;
    border-radius: 6px !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"]:focus-within {{
    border-color: {MCD_RED} !important;
    box-shadow: 0 0 0 1px {MCD_RED}40 !important;
  }}

  /* ─── Sidebar date input 样式 ─── */
  [data-testid="stSidebar"] [data-baseweb="input"] {{
    border: 1px solid #E0E0E0 !important;
    border-radius: 6px !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="input"]:focus-within {{
    border-color: {MCD_RED} !important;
    box-shadow: 0 0 0 1px {MCD_RED}40 !important;
  }}

  /* ─── Section 标题 ─── */
  .section-header {{
    font-size: 20px;
    font-weight: 700;
    color: #1a1a1a;
    padding: 24px 0 8px 0;
    border-bottom: 2px solid {MCD_RED};
    margin-bottom: 16px;
    letter-spacing: -0.01em;
  }}

  .section-subheader {{
    font-size: 14px;
    font-weight: 600;
    color: #666;
    margin: 16px 0 8px 0;
    letter-spacing: 0.02em;
  }}

  /* ─── KPI Card ─── */
  .kpi-card {{
    background: {MCD_CARD_BG};
    border: 1px solid {MCD_BORDER};
    border-radius: 12px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }}

  .kpi-card::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    background: {MCD_RED};
  }}

  .kpi-card.green::before {{ background: {MCD_GREEN}; }}
  .kpi-card.yellow::before {{ background: {MCD_GOLD}; }}
  .kpi-card.red::before {{ background: {MCD_RED}; }}

  .kpi-label {{
    font-size: 11px;
    font-weight: 600;
    color: #999;
    margin-bottom: 6px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}

  .kpi-value {{
    font-size: 28px;
    font-weight: 800;
    color: #1a1a1a;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
  }}

  .kpi-sub {{
    font-size: 12px;
    color: #666;
    font-variant-numeric: tabular-nums;
  }}

  .kpi-sub .up {{ color: {MCD_GREEN}; }}
  .kpi-sub .down {{ color: {MCD_RED}; }}

  /* ─── 状态色块 ─── */
  .status-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 4px;
  }}
  .status-dot.green {{ background: {MCD_GREEN}; }}
  .status-dot.yellow {{ background: {MCD_GOLD}; }}
  .status-dot.red {{ background: {MCD_RED}; }}

  /* ─── 表格优化 ─── */
  .dataframe {{
    font-size: 13px !important;
    font-variant-numeric: tabular-nums;
  }}
  .dataframe th {{
    font-weight: 600 !important;
    color: #666 !important;
    font-size: 11px !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}
  .dataframe td {{
    padding: 6px 8px !important;
  }}

  /* ─── 分隔线 ─── */
  .divider {{
    border: none;
    border-top: 1px solid #E8E8E8;
    margin: 32px 0;
  }}

  /* ─── 紧凑间距 ─── */
  .block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
  }}
  [data-testid="stVerticalBlock"] > div {{
    margin-bottom: 0 !important;
  }}
  [data-testid="stHorizontalBlock"] {{
    gap: 0.4rem !important;
  }}

  /* ─── 隐藏 Streamlit footer ─── */
  footer {{ visibility: hidden; }}
</style>
"""
