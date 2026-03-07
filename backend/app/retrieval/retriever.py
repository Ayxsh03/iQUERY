"""
Retriever — orchestrates query embedding → vector search → ranked results.

This is the core of the RAG pipeline's retrieval step. It combines the
embedder and vector store into a single clean interface.
"""

from typing import List, Dict, Any, Optional

from app.embeddings.embedder import embed_query
from app.vectorstore.chroma_store import query_chunks
from app.config import get_settings


def retrieve(
    query: str,
    top_k: Optional[int] = None,
    source_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant document chunks for a query.

    Pipeline:
        1. Embed the user query using SentenceTransformers
        2. Search ChromaDB by cosine similarity
        3. Return ranked chunks with metadata

    Args:
        query:         The user's question string.
        top_k:         Override number of results (defaults to settings).
        source_filter: Optional filename to restrict search to one doc.

    Returns:
        List of chunk dicts: {text, source, page, chunk_index, distance}
    """
    settings = get_settings()
    k = top_k or settings.top_k_results

    query_vector = embed_query(query)
    chunks = query_chunks(query_vector, top_k=k, source_filter=source_filter)

    # Filter out very distant results (poor matches) — distance > 0.9 on cosine
    relevant = [c for c in chunks if c["distance"] <= 0.9]

    return relevant or chunks  # fallback to all if everything is distant
