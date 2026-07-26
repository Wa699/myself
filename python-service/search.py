from config import SIMILARITY_THRESHOLD
from chroma_store import get_collection


def search_similar(query: str, n_results: int = 5) -> list[dict]:
    """向量检索，返回 [{"text": str, "metadata": dict, "distance": float}]"""
    collection = get_collection()

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    output: list[dict] = []
    if not results["ids"] or not results["ids"][0]:
        return output

    for i, doc_id in enumerate(results["ids"][0]):
        output.append({
            "text": results["documents"][0][i] if results["documents"] else "",
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else 0.0,
        })

    return output


def is_sufficient(results: list[dict]) -> bool:
    """判断检索结果是否足够：至少有一条记录的相似度高于阈值。"""
    if not results:
        return False
    return results[0]["distance"] < (1.0 - SIMILARITY_THRESHOLD)
