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

# 设计系统 tokens
THEME_HOVER = "#fde9ea"     # hover 态背景
THEME_MUTED = "#8a7e72"     # 弱化文字（比 INK2 更淡）
THEME_TAG_BG = "#F8F7F5"    # 药丸/标签背景
THEME_TAG_BORDER = "#e8e0d4" # 标签边框
THEME_SHADOW_1 = "0 1px 3px rgba(120,90,30,.06)"   # 卡片
THEME_SHADOW_2 = "0 2px 8px rgba(120,90,30,.10)"   # 悬浮/弹出
THEME_RADIUS_S = "6px"      # 小圆角（标签、按钮）
THEME_RADIUS_M = "10px"     # 中圆角（卡片）
THEME_RADIUS_L = "14px"     # 大圆角（容器）


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

# ─── API 配置（LLM 分析）──────────────────────────────────────
API_PROVIDERS = {
    "火山方舟": {
        "base_url": "https://ark.cn-beijing.volces.com/api/coding/v3",
        "models": ["minimax-m3"],
        "api_key": "k-897605b4-831b-494a-9e2e-d477d6b17158-fb2d1",
    },
    "百度千帆": {
        "base_url": "https://qianfan.baidubce.com/v2/coding",
        "models": ["qianfan-code-latest"],
        "api_key": "ce-v3/ALTAKSP-QmNPHghHzqzyoxZMVnzVo/c6b429d64ddc09c0c24d2c61a79ab30d1f1f5a55",
    },
    "麦当劳AI网关": {
        "base_url": "https://ai-gateway-test.mcdchina.net/v1",
        "models": ["gemini-3-flash-preview", "gemini-3-pro-image-preview", "deepseek-v3", "claude-sonnet-4.6", "claude-haiku-4.5"],
        "api_key": "",
    },
    "SiliconFlow": {
        "base_url": "https://api.siliconflow.cn/v1",
        "models": ["deepseek-ai/DeepSeek-V3-0324", "Qwen/Qwen2.5-72B-Instruct"],
        "api_key": "",
    },
    "OpenAI": {
        "base_url": None,
        "models": ["gpt-4o-mini", "gpt-4o"],
        "api_key": "",
    },
}
