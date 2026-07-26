import os
import chromadb
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

from config import CHROMA_HOST, CHROMA_PORT, CHROMA_COLLECTION

_client = None
_ef = None
_use_http = None


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
        _ef = ONNXMiniLM_L6_V2()
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