"""
llm_service.py - CNN Performance Weekly：LLM 内容分析服务
参考 mcd-content-rank 项目实现
"""

import json
import re
import openai
from config import API_PROVIDERS


ANALYSIS_DIMENSIONS = """请从以下4个维度逐条分析：

1. 核心亮点/问题
- 这条文案表现好（或不好）的主要原因是什么？
- 是文案吸引力、人群匹配度、利益点强度，还是数据承接能力？

2. 可借鉴点（表现好时）
- 标题是否直接表达利益点？
- 是否有场景感（早餐、午餐、下午茶、晚餐、周末、会员日）？
- 是否有紧迫感（今日限定、最后一天、限时、即将结束）？
- 人群匹配是否精准（内容—人群—场景一致）？

3. 改进方向（表现差时）
- 最值得尝试的一个改动方向是什么？
- 是标题吸引力不足、利益点不清晰、人群不匹配，还是落地页承接差？

4. 可复用/可优化
- 如果表现好，哪个点值得借鉴复用？
- 如果表现差，最值得尝试的一个改动方向是什么？"""


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

每条内容请输出以下4个字段（每个字段50字左右）：
- "core_issue": 核心亮点/问题（表现好/不好的主要原因）
- "highlight": 可借鉴点（表现好时值得借鉴的点）
- "weakness": 改进方向（表现差时最值得尝试的改动）
- "action": 可复用/可优化（具体行动建议）

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
        default = {"core_issue": "—", "highlight": "—", "weakness": "—", "action": "—"}
        results = (results + [default] * len(items))[:len(items)]
        for r in results:
            for k, v in default.items():
                r.setdefault(k, v)
        return results
    except json.JSONDecodeError as e:
        return [{"error": f"JSON解析失败: {str(e)[:50]}"}] * len(items)
    except Exception as e:
        return [{"error": f"API调用失败: {str(e)[:80]}"}] * len(items)
