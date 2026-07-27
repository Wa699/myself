from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class Citation(BaseModel):
    title: str
    category: str
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    evidence_sufficient: bool
    duration_ms: int


class ImportRequest(BaseModel):
    file_path: str  # 支持 .json / .pdf / .docx / .txt / .md
