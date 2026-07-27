import time
import json
import requests

from config import (
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    PRIMARY_API_KEY,
    FALLBACK_API_KEY,
    PRIMARY_BASE_URL,
    FALLBACK_BASE_URL,
)

SYSTEM_PROMPT = (
    "你是一个个人简历问答助手。请依据下面提供的候选人资料回答问题。"
    "规则："
    "1. 优先呈现资料中已有的相关信息，即使不够完整也要先说出已知部分；"
    "2. 如果资料有相关内容但缺少细节，先总结已知信息，再说明「资料中未详细展开」；"
    "3. 只有在该话题完全不存在于资料中时，才说「根据已有资料，无法确认该信息」；"
    "4. 绝对不要编造或猜测不存在的信息。请用中文回答，简洁专业。"
)

FREE_CHAT_SYSTEM_PROMPT = (
    "你是一个友好的个人简历问答助手。你可以自然地回应日常对话（如问候、感谢等）。"
    "当用户提出简历相关问题时：先呈现资料中已有的信息，再说明局限；"
    "只有话题完全不在资料中时才说「无法确认」。"
    "绝对不要编造或猜测候选人的信息。请用中文回答，简洁友好。"
)


def _build_user_prompt(question: str, context_chunks: list[str]) -> str:
    chunks_text = "\n\n---\n\n".join(context_chunks)
    return f"候选人资料：\n{chunks_text}\n\n问题：{question}"


def _call_model(
    model: str,
    api_key: str,
    base_url: str,
    messages: list[dict],
    temperature: float = 0.3,
    timeout: int = 30,
) -> str:
    """通用模型调用，失败抛异常。"""
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def _try_model(
    model: str,
    api_key: str,
    base_url: str,
    question: str,
    context_chunks: list[str],
) -> str:
    """用指定模型生成 RAG 回答（带简历上下文）。"""
    user_prompt = _build_user_prompt(question, context_chunks)
    return _call_model(
        model, api_key, base_url,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )


def _try_primary_fallback(messages_fn) -> tuple[str, int]:
    """主模型优先，失败则降级到备用模型，均失败抛出 RuntimeError。
    messages_fn 是一个接受 (model, api_key, base_url) 并返回 answer 字符串的回调。
    """
    start = time.time()

    if PRIMARY_API_KEY:
        try:
            answer = messages_fn(PRIMARY_MODEL, PRIMARY_API_KEY, PRIMARY_BASE_URL)
            duration_ms = int((time.time() - start) * 1000)
            return answer, duration_ms
        except Exception:
            pass

    if FALLBACK_API_KEY:
        try:
            answer = messages_fn(FALLBACK_MODEL, FALLBACK_API_KEY, FALLBACK_BASE_URL)
            duration_ms = int((time.time() - start) * 1000)
            return answer, duration_ms
        except Exception:
            pass

    raise RuntimeError("所有模型均不可用")


def generate_answer(question: str, context_chunks: list[str]) -> tuple[str, int]:
    """返回 (answer, duration_ms)。RAG 模式：带简历上下文回答。"""
    def _call(model, api_key, base_url):
        return _try_model(model, api_key, base_url, question, context_chunks)

    return _try_primary_fallback(_call)


def generate_free_chat(question: str) -> tuple[str, int]:
    """返回 (answer, duration_ms)。自由对话模式：无简历上下文，模型自行判断是寒暄还是无法回答。"""
    def _call(model, api_key, base_url):
        return _call_model(
            model, api_key, base_url,
            messages=[
                {"role": "system", "content": FREE_CHAT_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.7,
        )

    return _try_primary_fallback(_call)


def generate_questions(context_text: str) -> list[str]:
    """根据简历文本动态生成 5-6 个面试问题。每次调用都是新鲜的。"""
    prompt = f"""基于以下候选人简历内容，生成 5 个面试官可能会问的问题。每个问题一行，不要编号，直接写问题。

简历内容：
{context_text[:3000]}

要求：
- 只提简历中有足够信息可以回答的问题，不要提简历中只有一句话带过的话题
- 问题覆盖技能、项目、教育、经验等不同方面
- 用中文，简洁自然"""

    def _call(model, api_key, base_url):
        return _call_model(
            model, api_key, base_url,
            messages=[
                {"role": "system", "content": "你是一个面试问题生成器。只输出问题，每行一个，不要编号，不要额外解释。只提简历中有详细信息的问题，简历中一笔带过的内容不要提问。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )

    try:
        answer, _ = _try_primary_fallback(_call)
        questions = [q.strip() for q in answer.strip().split("\n") if q.strip()]
        return questions[:6] if questions else _fallback_questions_from_text(context_text)
    except RuntimeError:
        return _fallback_questions_from_text(context_text)


def _fallback_questions_from_text(text: str) -> list[str]:
    """LLM 不可用时从文本关键词提取简单问题。"""
    qs = []
    if "项目" in text:
        qs.append("请介绍一下你做过的项目？")
    if "技能" in text or "技术" in text:
        qs.append("你掌握哪些核心技术？")
    if "教育" in text or "大学" in text:
        qs.append("请介绍一下你的教育背景？")
    if "实习" in text or "工作" in text:
        qs.append("请介绍一下你的工作/实习经历？")
    if not qs:
        qs = ["请简单介绍一下你自己？"]
    return qs


# ========== 流式输出 ==========

def _call_model_stream(model: str, api_key: str, base_url: str,
                       messages: list[dict], temperature: float = 0.3):
    """流式调用 LLM，逐 token yield。"""
    resp = requests.post(
        f"{base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        },
        timeout=60,
        stream=True,
    )
    resp.raise_for_status()
    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        data_str = line[6:]
        if data_str.strip() == "[DONE]":
            break
        try:
            chunk = json.loads(data_str)
            delta = chunk["choices"][0].get("delta", {})
            content = delta.get("content", "")
            if content:
                yield content
        except (json.JSONDecodeError, KeyError, IndexError):
            continue


def generate_answer_stream(question: str, context_chunks: list[str]):
    """流式 RAG 回答。主模型优先，失败降级。"""
    user_prompt = _build_user_prompt(question, context_chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # 尝试主模型
    if PRIMARY_API_KEY:
        try:
            yield from _call_model_stream(PRIMARY_MODEL, PRIMARY_API_KEY, PRIMARY_BASE_URL, messages)
            return
        except Exception:
            pass

    # 降级备用模型
    if FALLBACK_API_KEY:
        try:
            yield from _call_model_stream(FALLBACK_MODEL, FALLBACK_API_KEY, FALLBACK_BASE_URL, messages)
            return
        except Exception:
            pass

    raise RuntimeError("所有模型均不可用")


def generate_free_chat_stream(question: str):
    """流式自由对话。"""
    messages = [
        {"role": "system", "content": FREE_CHAT_SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    if PRIMARY_API_KEY:
        try:
            yield from _call_model_stream(PRIMARY_MODEL, PRIMARY_API_KEY, PRIMARY_BASE_URL, messages, temperature=0.7)
            return
        except Exception:
            pass

    if FALLBACK_API_KEY:
        try:
            yield from _call_model_stream(FALLBACK_MODEL, FALLBACK_API_KEY, FALLBACK_BASE_URL, messages, temperature=0.7)
            return
        except Exception:
            pass

    raise RuntimeError("所有模型均不可用")