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

  /* ─── 顶部栏（Topbar）────────────────────────────────────────── */
  .topbar {{
    background: linear-gradient(135deg, #DB0007, #a8001a);
    border-bottom: 3px solid #FFBC0D;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 26px;
    box-shadow: 0 2px 14px rgba(0,0,0,.18);
    position: sticky;
    top: 0;
    z-index: 100;
    margin: -1.5rem -1rem 0 -1rem;
  }}
  .topbar-left {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .topbar-logo {{
    font-size: 34px;
    font-weight: 900;
    color: #FFBC0D;
    font-style: italic;
    letter-spacing: -3px;
    line-height: 1;
    text-shadow: 1px 2px 4px rgba(0,0,0,.3);
  }}
  .topbar-title h1 {{
    font-size: 17px;
    font-weight: 800;
    color: #fff;
    letter-spacing: .3px;
    margin: 0;
  }}
  .topbar-title .sub {{
    font-size: 11px;
    color: rgba(255,255,255,.85);
    margin-top: 1px;
  }}
  .topbar-right {{
    text-align: right;
    color: rgba(255,255,255,.92);
    font-size: 10.5px;
    line-height: 1.6;
  }}
  .topbar-badge {{
    display: inline-block;
    background: #FFBC0D;
    color: #5a1a00;
    font-weight: 800;
    font-size: 10.5px;
    padding: 2px 11px;
    border-radius: 20px;
    margin-bottom: 3px;
  }}

  /* ─── 导航栏（锚点链接，参考 ITO）────────────────────────────── */
  .nav-bar {{
    position: sticky;
    top: 57px;
    z-index: 90;
    background: rgba(255,253,248,.96);
    backdrop-filter: blur(6px);
    border-bottom: 1px solid #e4d9bf;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 8px 20px;
    margin: 0 -1rem 1rem -1rem;
  }}
  .nav-bar a.nav-link,
  .nav-bar a.nav-link:link,
  .nav-bar a.nav-link:visited,
  .nav-bar a.nav-link:active {{
    font-size: 11.5px !important;
    font-weight: 700 !important;
    color: #5a5048 !important;
    background: transparent !important;
    padding: 4px 11px !important;
    border-radius: 16px !important;
    text-decoration: none !important;
    border-bottom: none !important;
    transition: .15s;
    white-space: nowrap;
  }}
  .nav-bar a.nav-link:hover {{
    background: #fde9ea !important;
    color: #DA291C !important;
    text-decoration: none !important;
  }}

  /* ─── 紧凑间距 ─── */
  .block-container {{
    padding-top: 0 !important;
    padding-bottom: 1rem !important;
  }}
  [data-testid="stVerticalBlock"] > div {{
    margin-bottom: 0 !important;
  }}
  [data-testid="stHorizontalBlock"] {{
    gap: 0.4rem !important;
  }}

  /* ─── 确保 sticky 定位生效 ─── */
  .stApp {{
    overflow: visible !important;
  }}
  [data-testid="stAppViewContainer"] {{
    overflow: visible !important;
  }}

  /* ─── 调整 Streamlit 默认 header（保留侧边栏切换按钮）─── */
  header[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
  }}
  header[data-testid="stHeader"] button[kind="header"] {{
    color: #2b2620 !important;
  }}

  /* ─── 隐藏 Streamlit footer ─── */
  footer {{ visibility: hidden; }}
</style>
"""
