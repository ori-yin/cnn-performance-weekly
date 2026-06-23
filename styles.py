"""
styles.py - CNN Performance Weekly：CSS 样式
参考 ITO Traffic Operating Framework 的暖色纸张风格
"""

from config import MCD_RED, MCD_GOLD, MCD_GREEN


def get_css() -> str:
    return f"""
<style>
  /* ─── 全局：暖色纸张底 ─── */
  html, body, .stApp {{
    font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, sans-serif !important;
    background: #f4efe6;
    color: #2b2620;
  }}

  /* ─── 侧边栏 ─── */
  [data-testid="stSidebar"] {{
    background: #fffdf8 !important;
    border-right: 1px solid #e4d9bf;
    border-top: 3px solid {MCD_GOLD};
  }}

  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] p {{
    color: #2b2620 !important;
    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
  }}

  [data-testid="stSidebar"] .stRadio label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label,
  [data-testid="stSidebar"] .stNumberInput label,
  [data-testid="stSidebar"] .stDateInput label {{
    color: #5a5048 !important;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.02em;
    margin-bottom: 4px;
  }}

  [data-testid="stSidebar"] hr {{
    border-color: #e4d9bf !important;
    margin: 16px 0;
  }}

  [data-testid="stSidebar"] .stSelectbox > div > div,
  [data-testid="stSidebar"] .stTextInput > div > div,
  [data-testid="stSidebar"] .stNumberInput > div > div,
  [data-testid="stSidebar"] .stDateInput > div > div,
  [data-testid="stSidebar"] .stFileUploader > div {{
    background: #fffdf8 !important;
    border: 1.5px solid #d4c9af !important;
    border-radius: 6px !important;
    color: #2b2620 !important;
  }}

  [data-testid="stSidebar"] .stFileUploader {{
    border: 1.5px solid #d4c9af !important;
    border-radius: 6px !important;
    padding: 8px !important;
  }}

  /* ─── Sidebar multiselect ─── */
  [data-testid="stSidebar"] [data-baseweb="tag"] {{
    background-color: #fdeef0 !important;
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
    border: 1px solid #d4c9af !important;
    border-radius: 6px !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"]:focus-within {{
    border-color: {MCD_RED} !important;
    box-shadow: 0 0 0 1px {MCD_RED}40 !important;
  }}

  /* ─── Sidebar date input ─── */
  [data-testid="stSidebar"] [data-baseweb="input"] {{
    border: 1px solid #d4c9af !important;
    border-radius: 6px !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="input"]:focus-within {{
    border-color: {MCD_RED} !important;
    box-shadow: 0 0 0 1px {MCD_RED}40 !important;
  }}

  /* ─── Section 标题 ─── */
  .section-header {{
    font-size: 19px;
    font-weight: 800;
    color: #a8001a;
    padding: 20px 0 8px 0;
    border-bottom: 2px solid {MCD_RED};
    margin-bottom: 14px;
    letter-spacing: 0.3px;
  }}

  .section-subheader {{
    font-size: 14px;
    font-weight: 600;
    color: #5a5048;
    margin: 14px 0 8px 0;
    letter-spacing: 0.02em;
  }}

  /* ─── KPI Card：暖色纸张风 ─── */
  .kpi-card {{
    background: #fffdf8;
    border: 1px solid #e4d9bf;
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(120,90,30,.05);
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

  .kpi-card.green::before {{ background: #5a8a50; }}
  .kpi-card.yellow::before {{ background: {MCD_GOLD}; }}
  .kpi-card.red::before {{ background: {MCD_RED}; }}

  .kpi-label {{
    font-size: 11px;
    font-weight: 600;
    color: #5a5048;
    margin-bottom: 6px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}

  .kpi-value {{
    font-size: 26px;
    font-weight: 800;
    color: #2b2620;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
  }}

  .kpi-sub {{
    font-size: 12px;
    color: #5a5048;
    font-variant-numeric: tabular-nums;
  }}

  .kpi-sub .up {{ color: #5a8a50; }}
  .kpi-sub .down {{ color: {MCD_RED}; }}

  /* ─── 表格：深红表头 ─── */
  .dataframe {{
    font-size: 13px !important;
    font-variant-numeric: tabular-nums;
  }}
  .dataframe th {{
    font-weight: 700 !important;
    color: #fff !important;
    background: #a8001a !important;
    font-size: 11.5px !important;
    padding: 9px 11px !important;
  }}
  .dataframe td {{
    padding: 8px 11px !important;
    border-bottom: 1px solid #f0e8d6 !important;
  }}
  .dataframe tr:nth-child(even) td {{
    background: #fcfaf3 !important;
  }}

  /* ─── 分隔线 ─── */
  .divider {{
    border: none;
    border-top: 1px solid #e4d9bf;
    margin: 28px 0;
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
