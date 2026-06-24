"""
llm_service.py - CNN Performance Weekly：LLM 内容分析服务
参考 mcd-content-rank 项目实现
"""

import json
import re
import openai
from config import API_PROVIDERS


ANALYSIS_DIMENSIONS = """请从以下4个维度逐条分析：

1. 文案好在哪里
- 标题是否直接表达利益点？
- 是否有明确行动引导？
- 是否有场景感（早餐、午餐、下午茶、晚餐、周末、会员日）？
- 是否有紧迫感（今日限定、最后一天、限时、即将结束）？
- 是否减少理解成本，用户一眼知道有什么好处？

2. 人群匹配好在哪里
- 内容是否匹配该人群的历史偏好？
- 是否匹配用户生命周期阶段（新客、活跃、沉默、咖啡偏好、甜品偏好）？
- 是否避免了泛人群的低相关性？
- 是否属于"内容—人群—场景"一致？

3. 利益点好在哪里
- 利益点是否强？是价格利益、会员权益、新品尝鲜、限时提醒、抽奖机制、套餐组合，还是情绪价值？
- 利益点是否足够具体？
- 是否比普通活动表达更有吸引力？

4. 数据表现说明了什么
- 如果 CTR 高：说明内容点击吸引力强，重点看标题、利益点、场景表达。
- 如果 GC 转化率高：说明点击后的承接和购买意愿强，重点看落地页、商品、券、套餐是否匹配。
- 如果触达高且 CTR 不低：说明内容有放大价值。
- 如果触达低但评分高：需要提醒样本量可能不足，建议小范围复测或扩大触达验证。"""


def build_analysis_prompt(items: list) -> str:
    """构建批量分析 prompt"""
    lines = []
    for i, item in enumerate(items, 1):
        lines.append(
            f"【{i}】标题：{item['标题']}"
            f"｜正文：{item['内容']}"
            f"｜渠道：{item['渠道']}"
            f"｜触达：{item['触达成功']}"
            f"｜点击：{item['点击人次']}"
            f"｜CTR：{item['CTR']:.2f}%"
            f"｜GC：{item['订单GC']}"
            f"｜GC转化率：{item['订单GC转化率']:.2f}%"
            f"｜综合评分：{item['综合评分']:.2f}"
            f"｜排名：第{item['排名']}名"
        )

    return f"""你是麦当劳中国内容营销分析专家。请对以下 Plan 内容逐条分析。

{ANALYSIS_DIMENSIONS}

每条内容请输出以下4个字段（每个字段70字左右）：
- "rank_factor": 核心归因（为什么排名靠前/靠后）
- "highlight": 亮点
- "weakness": 短板
- "suggestion": 改进建议

严格输出 JSON 数组，不要输出其他任何文字、不要用markdown代码块。共{len(items)}条：
{chr(10).join(lines)}"""


def call_llm(api_key: str, provider: str, model: str, prompt: str) -> list:
    """调用 LLM API 并返回解析后的结果"""
    provider_config = API_PROVIDERS.get(provider)
    if not provider_config:
        return []

    base_url = provider_config["base_url"]
    client = openai.OpenAI(api_key=api_key, base_url=base_url) if base_url else openai.OpenAI(api_key=api_key)

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
    )
    raw = resp.choices[0].message.content.strip()
    # 清理 markdown 代码块
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    # 清理多余逗号（trailing comma）
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    # 尝试提取 JSON 数组
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        raw = match.group(0)
    # 清理字符串内的非法换行符（JSON 不允许裸换行）
    raw = re.sub(r'(?<!\\)\n', ' ', raw)
    # 修复未转义的引号（简单场景：值里的双引号）
    # 先尝试直接解析
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 如果失败，逐行尝试修复
        lines = raw.split('\n')
        cleaned = ' '.join(line.strip() for line in lines)
        return json.loads(cleaned)


def analyze_content(api_key: str, provider: str, model: str, items: list) -> list:
    """批量分析内容，返回结构化结果列表"""
    if not api_key:
        return [{"error": "请先填写 API Key"}] * len(items)

    prompt = build_analysis_prompt(items)

    try:
        results = call_llm(api_key, provider, model, prompt)
        if not isinstance(results, list):
            results = [results]
        # 补齐或截断
        default = {"rank_factor": "—", "highlight": "—", "weakness": "—", "suggestion": "—"}
        results = (results + [default] * len(items))[:len(items)]
        for r in results:
            for k, v in default.items():
                r.setdefault(k, v)
        return results
    except json.JSONDecodeError as e:
        return [{"error": f"JSON解析失败: {str(e)[:50]}"}] * len(items)
    except Exception as e:
        return [{"error": f"API调用失败: {str(e)[:80]}"}] * len(items)
