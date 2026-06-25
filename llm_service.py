"""
llm_service.py - CNN Performance Weekly：LLM 内容分析服务
参考 mcd-content-rank 项目实现
"""

import json
import re
import openai
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
- 客观审视这条内容是否还有优化提升的空间，不作为必须输出项
- 如果有，则输出这条内容还可以在哪些方面改进？比如CTR点击高但转化低，是不是需要优化落地页体验等
- 基于各项数据结果以及具体的内容文案本身做分析"""


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
