"""
Vector database wrapper around ChromaDB (embedded — no server process needed).
Stores one collection per course so search/RAG can be scoped to a course.
"""
from functools import lru_cache
from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.services.embeddings import get_embedding_provider


@lru_cache(maxsize=1)
def get_chroma_client():
    return chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIR,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def _collection_name(course_id: int) -> str:
    return f"course_{course_id}_materials"


def get_or_create_collection(course_id: int):
    client = get_chroma_client()
    return client.get_or_create_collection(name=_collection_name(course_id))


def index_chunks(course_id: int, material_id: int, chunk_ids: List[int], chunks: List[str], titles: List[str]):
    """Embed and upsert chunks for a material into the course's vector collection."""
    if not chunks:
        return
    provider = get_embedding_provider()
    vectors = provider.embed(chunks)
    collection = get_or_create_collection(course_id)
    ids = [f"m{material_id}_c{cid}" for cid in chunk_ids]
    metadatas = [{"material_id": material_id, "title": titles[i]} for i in range(len(chunks))]
    collection.upsert(ids=ids, embeddings=vectors, documents=chunks, metadatas=metadatas)


def semantic_search(course_id: int, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Returns top_k most semantically similar chunks with distance-based score."""
    provider = get_embedding_provider()
    query_vec = provider.embed([query])[0]
    collection = get_or_create_collection(course_id)
    count = collection.count()
    if count == 0:
        return []
    results = collection.query(query_embeddings=[query_vec], n_results=min(top_k, count))

    out = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        similarity = max(0.0, 1.0 - dist)  # cosine distance -> similarity approx
        out.append({
            "chunk_text": doc,
            "material_id": meta.get("material_id"),
            "material_title": meta.get("title"),
            "score": round(similarity, 4),
        })
    return out
