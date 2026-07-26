import time

from fastapi import FastAPI, HTTPException

from models import ChatRequest, ChatResponse, Citation, ImportRequest
from search import search_similar, is_sufficient
from llm import generate_answer
from import_data import import_resume_data

app = FastAPI(title="Resume RAG Chatbot", version="1.0.0")

INSUFFICIENT_ANSWER = "根据已有资料，无法确认该信息"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/internal/ai/chat")
def chat(req: ChatRequest) -> ChatResponse:
    """内部接口：接收问题，检索 + LLM 生成回答。"""
    start = time.time()

    try:
        results = search_similar(req.question)
    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        return ChatResponse(
            answer="向量检索服务异常，请稍后重试",
            citations=[],
            evidence_sufficient=False,
            duration_ms=duration_ms,
        )

    if not is_sufficient(results):
        duration_ms = int((time.time() - start) * 1000)
        return ChatResponse(
            answer=INSUFFICIENT_ANSWER,
            citations=[],
            evidence_sufficient=False,
            duration_ms=duration_ms,
        )

    context_chunks = [r["text"] for r in results]
    try:
        answer, llm_duration_ms = generate_answer(req.question, context_chunks)
    except RuntimeError:
        duration_ms = int((time.time() - start) * 1000)
        return ChatResponse(
            answer="AI 模型服务暂时不可用，请稍后重试",
            citations=[],
            evidence_sufficient=False,
            duration_ms=duration_ms,
        )

    citations = []
    for r in results[:3]:
        meta = r["metadata"]
        citations.append(Citation(
            title=meta.get("title", ""),
            category=meta.get("category", ""),
            excerpt=r["text"][:200],
        ))

    total_duration_ms = int((time.time() - start) * 1000)
    return ChatResponse(
        answer=answer,
        citations=citations,
        evidence_sufficient=True,
        duration_ms=total_duration_ms,
    )


@app.post("/internal/ai/import")
def import_data(req: ImportRequest):
    """内部接口：导入简历数据。"""
    try:
        count = import_resume_data(req.file_path)
        return {"status": "ok", "count": count}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"文件不存在: {req.file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
