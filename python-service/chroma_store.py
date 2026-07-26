import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION

_client: chromadb.PersistentClient | None = None
_ef: embedding_functions.SentenceTransformerEmbeddingFunction | None = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
        )
    return _client


def _get_ef() -> embedding_functions.SentenceTransformerEmbeddingFunction:
    global _ef
    if _ef is None:
        _ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    return _ef


def get_collection() -> chromadb.Collection:
    client = _get_client()
    ef = _get_ef()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=ef,
    )


def clear_and_rebuild(documents: list[dict]) -> int:
    """删除旧集合后全量重建。documents: [{"id": str, "text": str, "metadata": dict}]"""
    client = _get_client()
    ef = _get_ef()

    try:
        client.delete_collection(name=CHROMA_COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=ef,
    )

    if not documents:
        return 0

    ids = [d["id"] for d in documents]
    texts = [d["text"] for d in documents]
    metadatas = [d["metadata"] for d in documents]

    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    return len(documents)


def add_documents(documents: list[dict]) -> int:
    """增量追加文档。"""
    if not documents:
        return 0

    collection = get_collection()
    ids = [d["id"] for d in documents]
    texts = [d["text"] for d in documents]
    metadatas = [d["metadata"] for d in documents]

    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    return len(documents)
