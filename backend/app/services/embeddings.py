"""
Embedding provider abstraction (Module: Semantic Search).
Supports either a local, free sentence-transformers model (default, fully
offline after first download) or OpenAI's embedding API.
"""
from functools import lru_cache
from typing import List

from app.config import settings


class EmbeddingProvider:
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = model_name

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(model=self.model_name, input=texts)
        return [d.embedding for d in resp.data]


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbeddingProvider(settings.OPENAI_EMBEDDING_MODEL)
    return LocalEmbeddingProvider(settings.LOCAL_EMBEDDING_MODEL)
