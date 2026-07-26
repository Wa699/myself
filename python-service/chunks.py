def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """将文本按段落拆分后再按目标大小合并/切割，保证每个 chunk 不超出 chunk_size。"""
    if not text or not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if not current:
            current = para
        elif len(current) + len(para) + 1 <= chunk_size:
            current += "\n" + para
        else:
            chunks.append(current)
            if len(current) > overlap:
                current = current[-overlap:] + "\n" + para
            else:
                current = para

    if current:
        chunks.append(current)

    result: list[str] = []
    for c in chunks:
        if len(c) <= chunk_size:
            result.append(c)
        else:
            start = 0
            while start < len(c):
                end = min(start + chunk_size, len(c))
                result.append(c[start:end].strip())
                start += chunk_size - overlap

    return [r for r in result if r]
