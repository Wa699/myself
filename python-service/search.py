"""Simple keyword-based search - works without any model downloads."""
from chroma_store import get_collection


def search_similar(query: str, n_results: int = 5) -> list[dict]:
    """Keyword-based search: fetch all documents and rank by keyword overlap."""
    try:
        collection = get_collection()
        all_docs = collection.get()
    except Exception:
        return []

    if not all_docs["ids"]:
        return []

    query_terms = set(query.lower())
    scored = []

    for i, doc_id in enumerate(all_docs["ids"]):
        text = all_docs["documents"][i] if all_docs["documents"] else ""
        meta = all_docs["metadatas"][i] if all_docs["metadatas"] else {}

        # Score = percentage of query chars found in document
        hits = sum(1 for c in query if c in text)
        score = hits / max(len(query), 1)

        # Bonus for exact substring match
        if query.lower() in text.lower():
            score += 0.3

        scored.append({
            "text": text,
            "metadata": meta,
            "distance": 1.0 - score,  # Lower = better
            "score": score,
        })

    scored.sort(key=lambda x: x["distance"])
    return scored[:n_results]


def is_sufficient(results: list[dict]) -> bool:
    """Check if the best result has a reasonable score."""
    if not results:
        return False
    # score > 0.1 means there's at least some keyword overlap
    return results[0].get("score", 0) > 0.1