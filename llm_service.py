"""
llm_service.py - CNN Performance Weekly：LLM 内容分析服务
参考 mcd-content-rank 项目实现
"""

import json
import re
import openai
import dirtyjson
from config import API_PROVIDERS


ANALYSIS_DIMENSIONS = """请从以下3个维度逐条分析：

1. 核心亮点：
- 这条文案表现好的主要原因是什么？
- 是文案吸引力、人群匹配度、利益点强度，还是后续的落地页转化能力（落地页转化能力需要同步考虑GC、Sales，要注意那些CTR点击高但转化低的内容）？

2. 可借鉴点
- 标题是否直接表达利益点？
- 是否有场景感（早餐、午餐、下午茶、晚餐、周末、会员日）？
- 是否有紧迫感（今日限定、最后一天、限时、即将结束）？
- 人群匹配是否精准（内容—人群—场景一致）？
- 以及是否可以沉淀出可复用的模板供后续投放

3. 可优化（不作为必须输出项）
- 这不是"找茬"环节，有优化点就输出，没有就留空，不要硬说
- 如果文案本身已经很好（CTR高、转化好、标题利益点明确），就输出空字符串，不要为了输出而输出
- 只有在数据和文案都指向明确问题时才输出（如CTR高但转化低、标题模糊、利益点不清晰等）
- 基于各项数据结果以及具体的内容文案本身做分析

补充说明：
- 如果看到同一天有两条相同文案，可能是针对不同人群的投放（如新客vs沉默用户），并非重复投放，请注意区分"""


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

每条内容请输出以下字段（每个字段30字左右）：
- "highlight": 核心亮点（表现好的主要原因）
- "reference": 可借鉴点（值得借鉴复用的点，或可沉淀的模板）
- "optimize": 可优化（可选，如有优化空间则输出，无则输出空字符串）

严格输出 JSON 数组，不要输出其他任何文字、不要用markdown代码块。共{len(items)}条：
{chr(10).join(lines)}"""


def _extract_json_robust(raw: str) -> list:
    """
    稳健的 JSON 提取：先尝试标准解析，失败后用正则逐条提取
    """
    # 清理 markdown 代码块
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    # 尝试提取 JSON 数组
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        raw = match.group(0)

    # 方案1：dirtyjson 解析
    try:
        result = dirtyjson.loads(raw)
        if isinstance(result, list):
            return result
    except Exception:
        pass

    # 方案2：标准 json 解析
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
    except Exception:
        pass

    # 方案3：正则逐条提取 {"key": "value", ...}
    items = re.findall(r'\{[^{}]*\}', raw)
    results = []
    for item_str in items:
        item = {}
        # 提取每个 key-value 对
        pairs = re.findall(r'"(\w+)"\s*:\s*"((?:[^"\\]|\\.)*)"', item_str)
        for key, value in pairs:
            item[key] = value
        # 也尝试提取空字符串的情况
        pairs_empty = re.findall(r'"(\w+)"\s*:\s*""', item_str)
        for key in pairs_empty:
            if key not in item:
                item[key] = ""
        if item:
            results.append(item)
    if results:
        return results

    # 方案4：终极兜底 - 返回空列表
    return []


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
    return _extract_json_robust(raw)


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
        default = {"highlight": "—", "reference": "—", "optimize": ""}
        results = (results + [default] * len(items))[:len(items)]
        for r in results:
            for k, v in default.items():
                r.setdefault(k, v)
        return results
    except json.JSONDecodeError as e:
        return [{"error": f"JSON解析失败: {str(e)[:50]}"}] * len(items)
    except Exception as e:
        return [{"error": f"API调用失败: {str(e)[:80]}"}] * len(items)
