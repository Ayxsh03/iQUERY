"""
ChromaDB vector store wrapper.

Handles:
- Initialising a persistent ChromaDB client + collection
- Adding chunks (with embeddings and metadata)
- Querying by embedding vector
- Deleting all chunks for a given source document
- Listing all unique source documents
"""

import uuid
from typing import List, Dict, Any, Optional
from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings


@lru_cache(maxsize=1)
def _get_client() -> chromadb.PersistentClient:
    settings = get_settings()
    return chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


@lru_cache(maxsize=1)
def _get_collection():
    settings = get_settings()
    client = _get_client()
    return client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> int:
    """
    Add a list of chunks and their embeddings to ChromaDB.

    Args:
        chunks:     List of chunk dicts from chunker.py
        embeddings: Corresponding embedding vectors

    Returns:
        Number of chunks added.
    """
    collection = _get_collection()

    ids = [str(uuid.uuid4()) for _ in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "page": c["page"],
            "chunk_index": c["chunk_index"],
        }
        for c in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    return len(chunks)


def query_chunks(
    query_embedding: List[float],
    top_k: int = 5,
    source_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve the top-k most similar chunks for a query embedding.

    Args:
        query_embedding: The embedded user query vector.
        top_k:           Number of results to return.
        source_filter:   Optional — restrict results to a specific source file.

    Returns:
        List of result dicts with 'text', 'source', 'page', 'distance'.
    """
    collection = _get_collection()
    where = {"source": source_filter} if source_filter else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count() or 1),
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", 0),
            "chunk_index": meta.get("chunk_index", 0),
            "distance": round(dist, 4),
        })

    return output


def delete_document(source_filename: str) -> int:
    """
    Remove all chunks belonging to a specific source document.

    Returns:
        Number of chunks deleted.
    """
    collection = _get_collection()
    results = collection.get(where={"source": source_filename})
    ids_to_delete = results.get("ids", [])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)

    return len(ids_to_delete)


def list_documents() -> List[Dict[str, Any]]:
    """
    Return a list of unique documents in the store with chunk counts.
    """
    collection = _get_collection()
    all_items = collection.get(include=["metadatas"])
    metadatas = all_items.get("metadatas", [])

    doc_map: Dict[str, int] = {}
    for meta in metadatas:
        src = meta.get("source", "unknown")
        doc_map[src] = doc_map.get(src, 0) + 1

    return [{"source": src, "chunk_count": count} for src, count in doc_map.items()]


def get_collection_count() -> int:
    """Return total number of chunks stored."""
    return _get_collection().count()
