import json
import requests

from config import PRIMARY_API_KEY, PRIMARY_BASE_URL, PRIMARY_MODEL


def parse_pdf(file_path: str) -> str:
    """从 PDF 提取纯文本。"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except ImportError:
        raise ImportError("请安装 pypdf: pip install pypdf")


def parse_docx(file_path: str) -> str:
    """从 Word 文档提取纯文本。"""
    try:
        from docx import Document
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        raise ImportError("请安装 python-docx: pip install python-docx")


def extract_text(file_path: str) -> str:
    """根据文件后缀自动选择解析器，返回纯文本。"""
    lower = file_path.lower()
    if lower.endswith(".pdf"):
        return parse_pdf(file_path)
    elif lower.endswith(".docx"):
        return parse_docx(file_path)
    elif lower.endswith(".txt") or lower.endswith(".md"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"不支持的文件格式: {file_path}，请使用 .pdf / .docx / .txt")


def text_to_resume_json(raw_text: str, file_path: str = "resume") -> dict:
    """用 LLM 把简历原文转换成结构化 JSON。"""
    if not PRIMARY_API_KEY:
        return _fallback_parse(raw_text)

    prompt = f"""你是一个简历解析器。请从以下简历原文中提取信息，输出严格的 JSON 格式，不要包含任何其他内容。

要求：
- basics: name（姓名）、title（职位）、summary（一句话简介）
- skills: 技能列表（数组）
- projects: 项目列表，每项含 name、description、tech（技术栈数组）
- education: 教育经历列表，每项含 school、degree、major、year
- honors: 荣誉列表（数组）
- 缺失的字段用空字符串或空数组

简历原文：
{raw_text}

输出 JSON："""

    try:
        resp = requests.post(
            f"{PRIMARY_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {PRIMARY_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": PRIMARY_MODEL,
                "messages": [
                    {"role": "system", "content": "你是一个简历解析器。只输出 JSON，不要任何其他内容，不要 markdown 代码块标记。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
            },
            timeout=60,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        # 去掉可能的 markdown 代码块标记
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1]
            if text.endswith("```"):
                text = text[:-3]
        return json.loads(text.strip())
    except Exception:
        return _fallback_parse(raw_text)


def _fallback_parse(raw_text: str) -> dict:
    """LLM 不可用时的简单兜底。"""
    lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    name = lines[0] if lines else "未知"
    return {
        "basics": {"name": name, "title": "", "summary": raw_text[:200]},
        "skills": [],
        "projects": [],
        "education": [],
        "honors": [],
    }


def import_resume_file(file_path: str) -> int:
    """一站式：解析 PDF/Word → 转 JSON → 导入 Chroma。"""
    from import_data import import_resume_data
    import tempfile, os

    raw_text = extract_text(file_path)
    resume_data = text_to_resume_json(raw_text, file_path)

    # 写入临时 JSON 文件，交给 import_resume_data
    tmp_path = os.path.join(tempfile.gettempdir(), "_resume_parsed.json")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(resume_data, f, ensure_ascii=False, indent=2)

    return import_resume_data(tmp_path)