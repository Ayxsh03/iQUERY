"""
Chat API router — the RAG query endpoint.

Flow for each request:
    1. Receive user query
    2. Retrieve top-k relevant chunks from the vector store
    3. Call LLM with context + query
    4. Return answer + source citations
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.retrieval.retriever import retrieve
from app.generation.llm import generate_answer
from app.vectorstore.chroma_store import get_collection_count

router = APIRouter(prefix="/api", tags=["Chat"])


# ── Request / Response schemas ────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000, description="User's question")
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="Override result count")
    source_filter: Optional[str] = Field(default=None, description="Restrict to a specific document")


class SourceReference(BaseModel):
    source: str
    page: int
    excerpt: str      # first 200 chars of the chunk
    relevance: float  # 1 - distance (higher = more relevant)


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceReference]
    chunks_retrieved: int
    latency_s: float


# ── Endpoint ──────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse, summary="Ask a question about your documents")
async def chat(request: ChatRequest):
    """
    Submit a natural-language question and get an answer grounded in
    the indexed company documents.

    Returns the answer along with source citations (document name, page,
    and a short excerpt from the relevant chunk).
    """
    # Guard: nothing indexed yet
    if get_collection_count() == 0:
        raise HTTPException(
            status_code=400,
            detail="No documents have been indexed yet. Please upload documents via POST /api/ingest first.",
        )

    try:
        # Step 1: Retrieve relevant chunks
        chunks = retrieve(
            query=request.query,
            top_k=request.top_k,
            source_filter=request.source_filter,
        )

        if not chunks:
            return ChatResponse(
                query=request.query,
                answer="I couldn't find any relevant information in the uploaded documents for your question.",
                sources=[],
                chunks_retrieved=0,
                latency_s=0.0,
            )

        # Step 2: Generate answer
        answer, latency = generate_answer(query=request.query, chunks=chunks)

        # Step 3: Build source references (deduplicated by source+page)
        seen = set()
        sources = []
        for chunk in chunks:
            key = (chunk["source"], chunk["page"])
            if key not in seen:
                seen.add(key)
                sources.append(SourceReference(
                    source=chunk["source"],
                    page=chunk["page"],
                    excerpt=chunk["text"][:200].strip() + ("…" if len(chunk["text"]) > 200 else ""),
                    relevance=round(1 - chunk["distance"], 4),
                ))

        return ChatResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            chunks_retrieved=len(chunks),
            latency_s=latency,
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}",
        )
