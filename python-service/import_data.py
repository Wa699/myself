import json

from chunks import chunk_text
from chroma_store import clear_and_rebuild


def import_resume_data(file_path: str) -> int:
    """读取简历 JSON 文件，按段落分块后写入 Chroma。返回导入的 chunk 数量。"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents: list[dict] = []
    chunk_idx = 0

    basics = data.get("basics", {})
    name = basics.get("name", "未知")

    # 基本信息摘要
    summary = basics.get("summary", "")
    if summary:
        chunks = chunk_text(summary)
        for c in chunks:
            documents.append({
                "id": f"chunk_{chunk_idx}",
                "text": c,
                "metadata": {"category": "basics", "title": f"{name} - 个人简介", "name": name},
            })
            chunk_idx += 1

    # 技能
    skills = data.get("skills", [])
    if skills:
        skills_text = "技能：" + "、".join(skills)
        chunks = chunk_text(skills_text)
        for c in chunks:
            documents.append({
                "id": f"chunk_{chunk_idx}",
                "text": c,
                "metadata": {"category": "skills", "title": f"{name} - 技能", "name": name},
            })
            chunk_idx += 1

    # 项目经历
    projects = data.get("projects", [])
    for proj in projects:
        proj_name = proj.get("name", "")
        proj_desc = proj.get("description", "")
        proj_tech = "、".join(proj.get("tech", []))
        proj_text = f"项目：{proj_name}\n描述：{proj_desc}\n技术栈：{proj_tech}"
        chunks = chunk_text(proj_text)
        for c in chunks:
            documents.append({
                "id": f"chunk_{chunk_idx}",
                "text": c,
                "metadata": {"category": "projects", "title": f"{proj_name}", "name": name},
            })
            chunk_idx += 1

    # 教育经历
    education = data.get("education", [])
    for edu in education:
        school = edu.get("school", "")
        degree = edu.get("degree", "")
        major = edu.get("major", "")
        year = edu.get("year", "")
        edu_text = f"教育：{school} | {degree} | {major} | {year}"
        chunks = chunk_text(edu_text)
        for c in chunks:
            documents.append({
                "id": f"chunk_{chunk_idx}",
                "text": c,
                "metadata": {"category": "education", "title": f"{school} - {degree}", "name": name},
            })
            chunk_idx += 1

    # 荣誉
    honors = data.get("honors", [])
    if honors:
        honors_text = "荣誉：" + "；".join(honors)
        chunks = chunk_text(honors_text)
        for c in chunks:
            documents.append({
                "id": f"chunk_{chunk_idx}",
                "text": c,
                "metadata": {"category": "honors", "title": f"{name} - 荣誉", "name": name},
            })
            chunk_idx += 1

    return clear_and_rebuild(documents)
