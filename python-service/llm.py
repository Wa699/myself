import time
from openai import OpenAI

from config import (
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    PRIMARY_API_KEY,
    FALLBACK_API_KEY,
    PRIMARY_BASE_URL,
    FALLBACK_BASE_URL,
)

SYSTEM_PROMPT = (
    "你是一个个人简历问答助手。你只能依据下面提供的候选人资料回答问题。"
    "如果资料中没有相关信息，你必须明确说\"根据已有资料，无法确认该信息\"，"
    "绝对不要编造或猜测。请用中文回答，简洁专业。"
)


def _build_user_prompt(question: str, context_chunks: list[str]) -> str:
    chunks_text = "\n\n---\n\n".join(context_chunks)
    return f"候选人资料：\n{chunks_text}\n\n问题：{question}"


def _try_model(
    model: str,
    api_key: str,
    base_url: str,
    question: str,
    context_chunks: list[str],
) -> str:
    """尝试用指定模型生成回答，失败抛异常。"""
    client = OpenAI(api_key=api_key, base_url=base_url)
    user_prompt = _build_user_prompt(question, context_chunks)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        timeout=30.0,
    )

    return response.choices[0].message.content or ""


def generate_answer(question: str, context_chunks: list[str]) -> tuple[str, int]:
    """返回 (answer, duration_ms)。主模型优先，失败则降级，均失败抛出 RuntimeError。"""
    start = time.time()

    if PRIMARY_API_KEY:
        try:
            answer = _try_model(
                PRIMARY_MODEL, PRIMARY_API_KEY, PRIMARY_BASE_URL,
                question, context_chunks,
            )
            duration_ms = int((time.time() - start) * 1000)
            return answer, duration_ms
        except Exception:
            pass

    if FALLBACK_API_KEY:
        try:
            answer = _try_model(
                FALLBACK_MODEL, FALLBACK_API_KEY, FALLBACK_BASE_URL,
                question, context_chunks,
            )
            duration_ms = int((time.time() - start) * 1000)
            return answer, duration_ms
        except Exception:
            pass

    raise RuntimeError("所有模型均不可用")
