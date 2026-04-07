"""
Admin API router — document management, query logs, and feedback viewer.

Endpoints:
    GET  /api/admin/documents       List all documents with metadata
    DELETE /api/admin/documents/{filename}  Delete a document
    POST /api/admin/reindex/{filename}  Re-index (requires re-upload)
    GET  /api/admin/logs            Get recent query logs
    GET  /api/admin/feedback        Get all feedback records
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.db.database import get_db
from app.vectorstore.chroma_store import delete_document, list_documents

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ── Response schemas ───────────────────────────────────────────────────

class DocumentMeta(BaseModel):
    id: Optional[int] = None
    filename: str
    upload_ts: Optional[str] = None
    chunk_count: int
    status: str = "indexed"


class DocumentsResponse(BaseModel):
    documents: List[DocumentMeta]
    total: int


class QueryLogEntry(BaseModel):
    id: int
    query: str
    answer_preview: Optional[str]
    chunks_retrieved: int
    latency_s: float
    ts: str


class LogsResponse(BaseModel):
    logs: List[QueryLogEntry]
    total: int


class FeedbackEntry(BaseModel):
    id: int
    query: str
    answer: Optional[str]
    rating: int
    comment: Optional[str]
    ts: str


class FeedbackResponse(BaseModel):
    feedback: List[FeedbackEntry]
    total: int


# ── Endpoints ─────────────────────────────────────────────────────────


@router.get("/documents", response_model=DocumentsResponse, summary="List all indexed documents")
async def admin_list_documents():
    """
    Returns all documents with rich metadata (upload time, chunk count, status).
    Merges ChromaDB chunk counts with SQLite document records.
    """
    # Get chunk counts from ChromaDB (source of truth for indexed state)
    chroma_docs = {d["source"]: d["chunk_count"] for d in list_documents()}

    # Get metadata from SQLite
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, filename, upload_ts, chunk_count, status FROM documents ORDER BY upload_ts DESC"
        ).fetchall()

    docs = []
    seen_filenames = set()

    for row in rows:
        fname = row["filename"]
        seen_filenames.add(fname)
        # Use ChromaDB's chunk count as the live count; fall back to SQLite stored
        live_chunks = chroma_docs.get(fname, row["chunk_count"])
        status = "indexed" if fname in chroma_docs else "deleted"
        docs.append(DocumentMeta(
            id=row["id"],
            filename=fname,
            upload_ts=row["upload_ts"],
            chunk_count=live_chunks,
            status=status,
        ))

    # Include any ChromaDB docs that weren't logged to SQLite (e.g., old uploads)
    for fname, chunk_count in chroma_docs.items():
        if fname not in seen_filenames:
            docs.append(DocumentMeta(
                filename=fname,
                chunk_count=chunk_count,
                status="indexed",
            ))

    return DocumentsResponse(documents=docs, total=len(docs))


@router.delete("/documents/{filename:path}", summary="Delete a document from the index")
async def admin_delete_document(filename: str):
    """Remove a document from ChromaDB and mark it deleted in SQLite."""
    deleted_chunks = delete_document(filename)

    with get_db() as conn:
        conn.execute(
            "UPDATE documents SET status = 'deleted' WHERE filename = ?",
            (filename,),
        )

    if deleted_chunks == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Document '{filename}' not found in the index.",
        )

    return {
        "message": f"Deleted '{filename}' ({deleted_chunks} chunks removed).",
        "filename": filename,
        "chunks_removed": deleted_chunks,
    }


@router.post("/reindex/{filename:path}", summary="Re-index a document (re-upload required)")
async def admin_reindex_document(filename: str):
    """
    Currently, re-indexing requires the user to re-upload the file.
    This endpoint returns a clear instruction message.
    The file bytes are not stored server-side to keep storage minimal.
    """
    return {
        "message": (
            f"To re-index '{filename}', please delete it and re-upload it via "
            "the Admin panel's upload section. Document bytes are not persisted "
            "server-side to keep the deployment storage-efficient."
        ),
        "action_required": "re-upload",
        "filename": filename,
    }


@router.get("/logs", response_model=LogsResponse, summary="Get recent query logs")
async def admin_get_logs(
    limit: int = Query(default=50, ge=1, le=500, description="Max number of logs to return"),
    offset: int = Query(default=0, ge=0),
):
    """Return the most recent query logs, newest first."""
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM query_logs").fetchone()[0]
        rows = conn.execute(
            "SELECT id, query, answer_preview, chunks_retrieved, latency_s, ts "
            "FROM query_logs ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()

    logs = [
        QueryLogEntry(
            id=row["id"],
            query=row["query"],
            answer_preview=row["answer_preview"],
            chunks_retrieved=row["chunks_retrieved"],
            latency_s=row["latency_s"],
            ts=row["ts"],
        )
        for row in rows
    ]

    return LogsResponse(logs=logs, total=total)


@router.get("/feedback", response_model=FeedbackResponse, summary="Get all feedback entries")
async def admin_get_feedback(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Return user feedback records, newest first."""
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
        rows = conn.execute(
            "SELECT id, query, answer, rating, comment, ts "
            "FROM feedback ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()

    entries = [
        FeedbackEntry(
            id=row["id"],
            query=row["query"],
            answer=row["answer"],
            rating=row["rating"],
            comment=row["comment"],
            ts=row["ts"],
        )
        for row in rows
    ]

    return FeedbackResponse(feedback=entries, total=total)
