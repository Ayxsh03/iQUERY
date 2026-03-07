"""
Embedding module — wraps SentenceTransformers to produce dense vector
embeddings for text chunks.

The model is loaded once at startup (lazy singleton) to avoid repeated
expensive loads on every request.
"""

from typing import List
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    """Load and cache the SentenceTransformer model (singleton)."""
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of text strings and return a list of float vectors.

    Args:
        texts: List of strings to embed.

    Returns:
        List of embedding vectors (one per input string).
    """
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """
    Embed a single query string.

    Args:
        query: The user query.

    Returns:
        A single embedding vector.
    """
    model = _get_model()
    embedding = model.encode([query], normalize_embeddings=True)
    return embedding[0].tolist()
