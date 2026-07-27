import time
import hashlib
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from models import ChatRequest, ChatResponse, Citation, ImportRequest
from search import search_similar, is_sufficient
from llm import generate_answer, generate_free_chat, generate_questions
from llm import generate_answer_stream, generate_free_chat_stream
from import_data import import_resume_data
from parse_resume import import_resume_file
from chroma_store import get_collection

app = FastAPI(title="简历问答", version="1.0.0")

INSUFFICIENT_ANSWER = "根据已有资料，无法确认该信息"

# 示例问题缓存：避免每次页面加载都调 LLM
_questions_cache: dict = {"questions": [], "context_hash": "", "generated_at": 0}
_CACHE_TTL_SECONDS = 300  # 5 分钟


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
        # 检索不充分时，让 LLM 自行判断：寒暄则自然回复，简历问题则如实说无法确认
        try:
            answer, llm_duration_ms = generate_free_chat(req.question)
            duration_ms = int((time.time() - start) * 1000)
            return ChatResponse(
                answer=answer,
                citations=[],
                evidence_sufficient=False,
                duration_ms=duration_ms,
            )
        except RuntimeError:
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
    """内部接口：导入简历数据。支持 JSON / PDF / DOCX / TXT / MD。
    - JSON: 直接导入，需符合结构化格式
    - PDF/DOCX/TXT/MD: 自动解析提取文本 → LLM 结构化 → 导入"""
    # 清空示例问题缓存，下次请求会重新生成
    _questions_cache["context_hash"] = ""

    file_path = req.file_path

    # 根据后缀选择导入方式
    if file_path.lower().endswith(".json"):
        try:
            count = import_resume_data(file_path)
            return {"status": "ok", "count": count}
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # PDF / DOCX / TXT / MD → 解析 → 导入
        try:
            count = import_resume_file(file_path)
            return {"status": "ok", "count": count}
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ImportError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/profile")
def get_profile():
    """前端用：从 Chroma 简历数据动态重构候选人简介。
    不依赖缓存，始终反映当前导入的简历。"""
    try:
        collection = get_collection()
        all_docs = collection.get()
    except Exception:
        raise HTTPException(status_code=404, detail="尚未导入简历数据")

    if not all_docs["ids"]:
        raise HTTPException(status_code=404, detail="尚未导入简历数据")

    name = "未知"
    title = ""
    summary = ""
    skills: list[str] = []

    for i, doc_id in enumerate(all_docs["ids"]):
        meta = all_docs["metadatas"][i] if all_docs["metadatas"] else {}
        text = all_docs["documents"][i] if all_docs["documents"] else ""
        category = meta.get("category", "")

        if meta.get("name") and name == "未知":
            name = meta["name"]

        if category == "basics":
            title = meta.get("detail", "")
            if not summary:
                summary = text

        if category == "skills":
            # "技能：Java、JVM、Spring Boot" → parse
            raw = text.replace("技能：", "").replace("技能:", "")
            skills = [s.strip() for s in raw.split("、") if s.strip()]

    return {
        "name": name,
        "title": title,
        "summary": summary,
        "skills": skills,
    }


@app.get("/api/sample-questions")
def get_sample_questions():
    """前端用：LLM 根据简历动态生成问题。带 5 分钟缓存，避免重复调用 LLM。
    导入新简历后缓存自动失效。"""
    global _questions_cache

    try:
        collection = get_collection()
        all_docs = collection.get()
    except Exception:
        raise HTTPException(status_code=404, detail="尚未导入简历数据")

    if not all_docs["ids"]:
        raise HTTPException(status_code=404, detail="尚未导入简历数据")

    # 计算当前简历内容的哈希，判断是否需要重新生成
    context = "\n\n".join(all_docs["documents"])
    context_hash = hashlib.md5(context.encode()).hexdigest()

    now = time.time()
    cache_valid = (
        _questions_cache["context_hash"] == context_hash
        and _questions_cache["questions"]
        and (now - _questions_cache["generated_at"]) < _CACHE_TTL_SECONDS
    )

    if cache_valid:
        return {"questions": _questions_cache["questions"], "cached": True}

    # 缓存过期或简历已变更 → LLM 重新生成
    questions = generate_questions(context)
    _questions_cache = {
        "questions": questions,
        "context_hash": context_hash,
        "generated_at": now,
    }

    return {"questions": questions, "cached": False}


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """流式聊天接口：SSE 逐 token 推送，体验类似 ChatGPT。"""

    async def event_stream():
        start = time.time()
        results = []
        evidence = False
        citations: list[dict] = []

        try:
            results = search_similar(req.question)
        except Exception:
            yield f"data: {json.dumps({'error': '向量检索服务异常，请稍后重试'})}\n\n"
            return

        if not is_sufficient(results):
            # 自由对话流式
            try:
                for token in generate_free_chat_stream(req.question):
                    yield f"data: {json.dumps({'token': token})}\n\n"
                evidence = False
            except RuntimeError:
                yield f"data: {json.dumps({'token': INSUFFICIENT_ANSWER})}\n\n"
                evidence = False
        else:
            # RAG 流式
            context_chunks = [r["text"] for r in results]
            try:
                for token in generate_answer_stream(req.question, context_chunks):
                    yield f"data: {json.dumps({'token': token})}\n\n"
                evidence = True
            except RuntimeError:
                yield f"data: {json.dumps({'token': 'AI 模型服务暂时不可用，请稍后重试'})}\n\n"
                evidence = False

        # 构建 citations
        for r in results[:3]:
            meta = r["metadata"]
            citations.append({
                "title": meta.get("title", ""),
                "category": meta.get("category", ""),
                "excerpt": r["text"][:200],
            })

        duration_ms = int((time.time() - start) * 1000)
        done_msg = json.dumps({
            "done": True,
            "citations": citations,
            "evidence_sufficient": evidence,
            "duration_ms": duration_ms,
        })
        yield f"data: {done_msg}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
