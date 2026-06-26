"""
styles.py - CNN Performance Weekly：CSS 样式
设计系统：暖色纸张风格，统一 token
"""

from config import (
    MCD_RED, MCD_GOLD, MCD_GREEN, MCD_DARK_RED,
    THEME_BG, THEME_PAPER, THEME_INK, THEME_INK2, THEME_LINE, THEME_ROW_ALT,
    THEME_HOVER, THEME_MUTED, THEME_TAG_BG, THEME_TAG_BORDER,
    THEME_SHADOW_1, THEME_SHADOW_2, THEME_RADIUS_S, THEME_RADIUS_M, THEME_RADIUS_L,
)


def get_css() -> str:
    return f"""
<style>
  /* ─── 全局 ─── */
  html {{ scroll-behavior: smooth; }}
  html, body, .stApp {{
    font-family: 'Microsoft YaHei', 'PingFang SC', -apple-system, sans-serif !important;
    background: {THEME_BG};
    color: {THEME_INK};
    font-size: 14px;
    line-height: 1.6;
  }}

  /* ─── 侧边栏 ─── */
  [data-testid="stSidebar"] {{
    background: {THEME_PAPER} !important;
    border-right: 1px solid {THEME_LINE};
    border-top: 3px solid {MCD_GOLD};
  }}
  [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] p {{
    color: {THEME_INK} !important;
    font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif !important;
    font-size: 13px;
  }}
  [data-testid="stSidebar"] .stRadio label,
  [data-testid="stSidebar"] .stSelectbox label,
  [data-testid="stSidebar"] .stTextInput label,
  [data-testid="stSidebar"] .stNumberInput label,
  [data-testid="stSidebar"] .stDateInput label {{
    color: {THEME_INK2} !important;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.02em;
    margin-bottom: 4px;
  }}
  [data-testid="stSidebar"] hr {{
    border-color: {THEME_LINE} !important;
    margin: 16px 0;
  }}
  [data-testid="stSidebar"] .stSelectbox > div > div,
  [data-testid="stSidebar"] .stTextInput > div > div,
  [data-testid="stSidebar"] .stNumberInput > div > div,
  [data-testid="stSidebar"] .stDateInput > div > div,
  [data-testid="stSidebar"] .stFileUploader > div {{
    background: {THEME_PAPER} !important;
    border: 1.5px solid {THEME_TAG_BORDER} !important;
    border-radius: {THEME_RADIUS_S} !important;
    color: {THEME_INK} !important;
  }}
  [data-testid="stSidebar"] .stFileUploader {{
    border: 1.5px solid {THEME_TAG_BORDER} !important;
    border-radius: {THEME_RADIUS_S} !important;
    padding: 8px !important;
  }}

  /* ─── Sidebar multiselect ─── */
  [data-testid="stSidebar"] [data-baseweb="tag"] {{
    background-color: {THEME_HOVER} !important;
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
    border: 1px solid {THEME_TAG_BORDER} !important;
    border-radius: {THEME_RADIUS_S} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="select"]:focus-within {{
    border-color: {MCD_RED} !important;
    box-shadow: 0 0 0 1px {MCD_RED}40 !important;
  }}

  /* ─── Sidebar date input ─── */
  [data-testid="stSidebar"] [data-baseweb="input"] {{
    border: 1px solid {THEME_TAG_BORDER} !important;
    border-radius: {THEME_RADIUS_S} !important;
  }}
  [data-testid="stSidebar"] [data-baseweb="input"]:focus-within {{
    border-color: {MCD_RED} !important;
    box-shadow: 0 0 0 1px {MCD_RED}40 !important;
  }}

  /* ─── Section 标题 ─── */
  .section-header {{
    font-size: 20px;
    font-weight: 800;
    color: {MCD_DARK_RED};
    padding: 24px 0 8px 0;
    border-bottom: 2px solid {MCD_RED};
    margin-bottom: 16px;
    letter-spacing: 0.3px;
  }}
  .section-subheader {{
    font-size: 14px;
    font-weight: 600;
    color: {THEME_INK2};
    margin: 16px 0 8px 0;
    letter-spacing: 0.02em;
  }}

  /* ─── KPI Card ─── */
  .kpi-card {{
    background: {THEME_PAPER};
    border: 1px solid {THEME_LINE};
    border-radius: {THEME_RADIUS_M};
    padding: 16px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    box-shadow: {THEME_SHADOW_1};
    transition: box-shadow .15s;
  }}
  .kpi-card:hover {{
    box-shadow: {THEME_SHADOW_2};
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: {MCD_RED};
  }}
  .kpi-card.green::before {{ background: #5a8a50; }}
  .kpi-card.yellow::before {{ background: {MCD_GOLD}; }}
  .kpi-card.red::before {{ background: {MCD_RED}; }}

  .kpi-label {{
    font-size: 12px;
    font-weight: 600;
    color: {THEME_MUTED};
    margin-bottom: 6px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}
  .kpi-value {{
    font-size: 28px;
    font-weight: 800;
    color: {THEME_INK};
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 4px;
    font-variant-numeric: tabular-nums;
  }}
  .kpi-sub {{
    font-size: 12px;
    color: {THEME_MUTED};
    font-variant-numeric: tabular-nums;
  }}
  .kpi-sub .up {{ color: #5a8a50; }}
  .kpi-sub .down {{ color: {MCD_RED}; }}

  /* ─── 表格 ─── */
  .dataframe {{
    font-size: 13px !important;
    font-variant-numeric: tabular-nums;
  }}
  .dataframe th {{
    font-weight: 700 !important;
    color: #fff !important;
    background: {MCD_DARK_RED} !important;
    font-size: 12px !important;
    padding: 10px 12px !important;
  }}
  .dataframe td {{
    padding: 8px 12px !important;
    border-bottom: 1px solid {THEME_LINE} !important;
  }}
  .dataframe tr:nth-child(even) td {{
    background: {THEME_ROW_ALT} !important;
  }}

  /* ─── 锚点跳转偏移 ─── */
  [id^="sec-"] {{ scroll-margin-top: 115px; }}

  /* ─── 分隔线 ─── */
  .divider {{
    border: none;
    border-top: 1px solid {THEME_LINE};
    margin: 32px 0;
  }}

  /* ─── 顶部栏 ─── */
  .topbar {{
    background: linear-gradient(135deg, #DB0007, {MCD_DARK_RED});
    border-bottom: 3px solid {MCD_GOLD};
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 26px;
    box-shadow: 0 2px 12px rgba(0,0,0,.15);
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    height: 57px;
  }}
  .topbar-left {{ display: flex; align-items: center; gap: 14px; }}
  .topbar-logo-img {{
    height: 40px;
    width: auto;
    filter: brightness(0) invert(1);
  }}
  .topbar-title h1 {{
    font-size: 16px;
    font-weight: 800;
    color: #fff;
    letter-spacing: .3px;
    margin: 0;
  }}
  .topbar-title .sub {{
    font-size: 12px;
    color: rgba(255,255,255,.85);
    margin-top: 2px;
  }}
  .topbar-right {{
    text-align: right;
    color: rgba(255,255,255,.92);
    font-size: 12px;
    line-height: 1.6;
  }}
  .topbar-badge {{
    display: inline-block;
    background: {MCD_GOLD};
    color: #5a1a00;
    font-weight: 800;
    font-size: 12px;
    padding: 2px 12px;
    border-radius: 20px;
    margin-bottom: 3px;
  }}

  /* ─── 导航栏 ─── */
  .nav-bar {{
    position: fixed;
    top: 60px; left: 0; right: 0;
    z-index: 90;
    background: rgba(255,253,248,.96);
    backdrop-filter: blur(6px);
    border-bottom: 1px solid {THEME_LINE};
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 8px 20px;
  }}
  .nav-bar a.nav-link,
  .nav-bar a.nav-link:link,
  .nav-bar a.nav-link:visited,
  .nav-bar a.nav-link:active {{
    font-size: 12px !important;
    font-weight: 700 !important;
    color: {THEME_INK2} !important;
    background: transparent !important;
    padding: 5px 14px !important;
    border-radius: 16px !important;
    text-decoration: none !important;
    border-bottom: none !important;
    transition: background .15s, color .15s;
    white-space: nowrap;
  }}
  .nav-bar a.nav-link:hover {{
    background: {THEME_HOVER} !important;
    color: {MCD_RED} !important;
    text-decoration: none !important;
  }}

  /* ─── 紧凑间距 ─── */
  .block-container {{
    padding-top: 0 !important;
    padding-bottom: 1rem !important;
  }}
  [data-testid="stVerticalBlock"] > div {{ margin-bottom: 0 !important; }}
  [data-testid="stHorizontalBlock"] {{ gap: 0.4rem !important; }}

  /* ─── 隐藏侧边栏折叠按钮 ─── */
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarCollapseButton"] button {{
    display: none !important;
  }}
  [data-testid="stSidebar"] {{
    min-width: 280px !important;
    max-width: 280px !important;
  }}

  /* ─── 调整 Streamlit 默认 header ─── */
  header[data-testid="stHeader"] {{
    background: transparent !important;
    box-shadow: none !important;
  }}
  header[data-testid="stHeader"] button[kind="header"] {{
    display: none !important;
  }}

  /* ─── Plan 卡片删除按钮（小号低调）─── */
  .stButton button {{
    font-size: 12px !important;
    padding: 2px 12px !important;
    min-height: 28px !important;
    border-radius: {THEME_RADIUS_S} !important;
    font-weight: 500 !important;
    transition: all .15s !important;
  }}

  /* ─── 隐藏 Streamlit footer ─── */
  footer {{ visibility: hidden; }}
</style>
"""
