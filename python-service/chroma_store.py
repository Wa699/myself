import os
import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION

_client = None
_ef = None
_use_http = None


class SimpleEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """A simple embedding that works without model downloads.
    Uses character n-gram based hashing to produce embeddings.
    This is a FALLBACK until the ONNX model is downloaded."""
    
    def __init__(self, dim: int = 384):
        self._dim = dim
    
    def _hash_embed(self, text: str) -> list[float]:
        """Simple hash-based embedding."""
        import hashlib
        result = [0.0] * self._dim
        for i in range(len(text) - 2):
            trigram = text[i:i+3]
            h = int(hashlib.md5(trigram.encode()).hexdigest(), 16)
            idx = h % self._dim
            result[idx] += 1.0
        # Normalize
        norm = max(sum(v*v for v in result) ** 0.5, 0.001)
        return [v / norm for v in result]
    
    def __call__(self, input):
        texts = [input] if isinstance(input, str) else input
        return [self._hash_embed(t) for t in texts]


def _is_http():
    global _use_http
    if _use_http is None:
        _use_http = bool(CHROMA_HOST)
    return _use_http


def _get_client():
    global _client
    if _client is None:
        host = CHROMA_HOST
        port = int(CHROMA_PORT) if CHROMA_PORT else 8000
        if _is_http():
            _client = chromadb.HttpClient(host=host, port=port)
        else:
            _client = chromadb.PersistentClient(path="./chroma_data")
    return _client


def _get_ef():
    global _ef
    if _ef is None:
        _ef = SimpleEmbeddingFunction()
    return _ef


def get_collection():
    client = _get_client()
    ef = _get_ef()
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        embedding_function=ef,
    )


def clear_and_rebuild(documents: list[dict]) -> int:
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
    if not documents:
        return 0

    collection = get_collection()
    ids = [d["id"] for d in documents]
    texts = [d["text"] for d in documents]
    metadatas = [d["metadata"] for d in documents]

    collection.add(ids=ids, documents=texts, metadatas=metadatas)
    return len(documents)