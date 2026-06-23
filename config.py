"""
config.py - CNN Performance Weekly：全局配置与常量
"""

# ─── 品牌色（暖色纸质主题）──────────────────────────────────────
MCD_RED = "#DA291C"
MCD_DARK_RED = "#a8001a"  # 深红表头
MCD_GOLD = "#FFC72C"
MCD_GREEN = "#00A04A"
MCD_YELLOW = "#FF9500"

# 暖色纸质主题（参考 ITO Traffic Operating Framework）
THEME_BG = "#f4efe6"        # 页面背景
THEME_PAPER = "#fffdf8"     # 卡片/表格背景
THEME_INK = "#2b2620"       # 主文字
THEME_INK2 = "#5a5048"      # 副文字
THEME_LINE = "#e4d9bf"      # 边框线
THEME_ROW_ALT = "#fcfaf3"   # 交替行背景

# 兼容旧名
MCD_BG = THEME_BG
MCD_CARD_BG = THEME_PAPER
MCD_TEXT = THEME_INK
MCD_TEXT_SUB = THEME_INK2
MCD_TEXT_MUTED = "#999999"
MCD_BORDER = THEME_LINE

# ─── 状态阈值 ──────────────────────────────────────────────────
# 绿 = 达成 / 黄 = 落后 5-15% / 红 = 落后 15%+
STATUS_GREEN = "green"
STATUS_YELLOW = "yellow"
STATUS_RED = "red"

# ─── 列名映射（Fuzzy match）──────────────────────────────────────
# key = 标准字段名, value = 可能出现的列名关键词列表
COLUMN_MAPPING = {
    "发送日期": ["发送日期", "日期", "date", "send_date", "send"],
    "计划类型": ["计划类型", "plan_type", "nudge", "类型"],
    "渠道": ["渠道", "channel"],
    "Plan ID": ["Plan ID", "plan_id", "planid"],
    "Plan名称": ["Plan名称", "plan_name", "planname", "名称"],
    "预算owner": ["预算owner", "owner", "BU", "bu", "预算"],
    "是否用券": ["是否用券", "coupon", "用券"],
    "预计触达": ["预计触达", "expected_reach", "expected", "预计"],
    "触达成功": ["触达成功", "reach", "触达"],
    "点击人次": ["点击人次", "clicks", "点击"],
    "点击后下单人次": ["点击后下单人次", "orders", "下单人次"],
    "订单GC": ["订单GC", "GC", "gc"],
    "订单Sales": ["订单Sales", "Sales", "sales", "订单sales"],
    "消息标题": ["消息标题", "title", "标题"],
    "消息内容": ["消息内容", "content", "内容", "text"],
}

# ─── 数值列 ──────────────────────────────────────────────────
NUMERIC_COLS = [
    "预计触达", "触达成功", "点击人次", "点击后下单人次", "订单GC", "订单Sales"
]

# ─── 评分权重（综合评分体系）────────────────────────────────────
W_REACH = 0.30    # 触达规模
W_CTR = 0.40      # CTR
W_GC = 0.30       # GC 转化率

# ─── CTR/GC 渠道 Q3 阈值（来自历史数据统计）────────────────────
CTR_THRESHOLDS = {
    "APP Push": 0.24,
    "企微1v1": 1.62,
    "微信小程序订阅消息": 4.01,
    "短信": 0.46,
}
GC_THRESHOLDS = {
    "APP Push": 69.5,
    "企微1v1": 18.5,
    "微信小程序订阅消息": 41.0,
    "短信": 26.7,
}
CTR_UNKNOWN_THRESHOLD = 2.85
GC_UNKNOWN_THRESHOLD = 34.8

# ─── 评分幂次 ──────────────────────────────────────────────
SCORING_EXP = 1.5

# ─── 置信度惩罚（触达规模）────────────────────────────────────
CONFIDENCE_THRESHOLDS = [
    (100, 0.1),
    (500, 0.3),
    (1000, 0.5),
    (5000, 0.8),
]
CONFIDENCE_DEFAULT = 1.0

# ─── 渠道列表 ──────────────────────────────────────────────
CHANNELS = ["APP Push", "企微1v1", "短信", "微信小程序订阅消息"]

# ─── 编码尝试顺序 ──────────────────────────────────────────────
ENCODINGS = ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin1"]
