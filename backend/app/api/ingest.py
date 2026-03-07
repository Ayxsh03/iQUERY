"""
Ingest API router — handles document upload, parsing, chunking,
embedding, and storage in a single POST /api/ingest endpoint.
"""

import time
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.ingestion.loader import load_document
from app.ingestion.chunker import chunk_pages
from app.embeddings.embedder import embed_texts
from app.vectorstore.chroma_store import add_chunks, delete_document, list_documents

router = APIRouter(prefix="/api", tags=["Ingestion"])


class IngestResponse(BaseModel):
    filename: str
    pages_parsed: int
    chunks_created: int
    processing_time_s: float
    message: str


class DocumentListResponse(BaseModel):
    documents: List[dict]
    total_documents: int


@router.post("/ingest", response_model=IngestResponse, summary="Upload and index a document")
async def ingest_document(file: UploadFile = File(...)):
    """
    Upload a PDF, DOCX, or TXT file. The system will:
    1. Extract text from the document
    2. Split into overlapping chunks
    3. Generate embeddings for each chunk
    4. Store everything in the vector database

    Supported formats: .pdf, .docx, .txt
    """
    start = time.time()

    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".doc", ".txt"}
    filename = file.filename or "unnamed"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {', '.join(allowed_extensions)}",
        )

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(file_bytes) > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50 MB.")

    try:
        # Step 1: Parse document
        pages = load_document(file_bytes, filename)

        # Step 2: Chunk
        chunks = chunk_pages(pages)
        if not chunks:
            raise HTTPException(status_code=422, detail="No text could be extracted from this document.")

        # Step 3: Embed
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(texts)

        # Step 4: Store (delete old version if re-uploading same file)
        delete_document(filename)
        count = add_chunks(chunks, embeddings)

        elapsed = round(time.time() - start, 3)

        return IngestResponse(
            filename=filename,
            pages_parsed=len(pages),
            chunks_created=count,
            processing_time_s=elapsed,
            message=f"Successfully indexed '{filename}' with {count} chunks.",
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}",
        )


@router.get("/documents", response_model=DocumentListResponse, summary="List indexed documents")
async def get_documents():
    """Return all documents currently indexed in the vector store."""
    docs = list_documents()
    return DocumentListResponse(documents=docs, total_documents=len(docs))


@router.delete("/documents/{filename:path}", summary="Delete an indexed document")
async def remove_document(filename: str):
    """Remove all chunks for a specific document from the vector store."""
    deleted = delete_document(filename)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found.")
    return {"message": f"Deleted {deleted} chunks for '{filename}'."}
