"""
iQuery — FastAPI application entry point (Phase 2+).

Registers all API routers and configures CORS for local development
and production (via FRONTEND_URL env var).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ingest import router as ingest_router
from app.api.chat import router as chat_router
from app.api.admin import router as admin_router
from app.api.feedback import router as feedback_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="iQuery API",
    description=(
        "Internal document-grounded chatbot using RAG. "
        "Upload company documents and ask questions — answers are grounded in your docs."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if settings.frontend_url:
    # Add the deployed frontend URL (e.g. https://iquery-frontend.onrender.com)
    allowed_origins.append(settings.frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(ingest_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(feedback_router)


# ── Health check ─────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"], summary="Health check")
async def health():
    """Returns a 200 OK with basic system info."""
    from app.vectorstore.chroma_store import get_collection_count
    return {
        "status": "ok",
        "service": "iQuery API",
        "version": "2.0.0",
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.embedding_model,
        "total_chunks_indexed": get_collection_count(),
    }


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "iQuery API v2.0 is running. Visit /docs for the interactive API reference."}
