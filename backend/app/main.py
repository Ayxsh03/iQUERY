"""
iQuery — FastAPI application entry point (Phase 2+).

Registers all API routers and configures CORS for local development
and production (via FRONTEND_URL env var).
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

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


# ── CORS Logging Middleware ───────────────────────────────────────────
class CORSLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        if origin:
            print(f"[CORS] Request from origin: {origin}, Method: {request.method}, Path: {request.url.path}")
        response = await call_next(request)
        return response

app.add_middleware(CORSLoggingMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add FRONTEND_URL if set
if settings.frontend_url:
    clean_url = settings.frontend_url.rstrip("/")
    if clean_url not in allowed_origins:
        allowed_origins.append(clean_url)
    # Also add www variant if not present
    if clean_url.startswith("https://") and "www." not in clean_url:
        www_variant = clean_url.replace("https://", "https://www.")
        if www_variant not in allowed_origins:
            allowed_origins.append(www_variant)

# Common Render domain patterns
render_origins = [
    "https://iqueryweb.onrender.com",
    "https://iquery-frontend.onrender.com",
    "https://iquery.onrender.com",
    "https://iquery-api.onrender.com",  # Allow API to call itself if needed
]
for origin in render_origins:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

# Log CORS configuration on startup
print(f"[CORS] Allowed origins: {allowed_origins}")
print(f"[CORS] Regex pattern: https://.*\\.onrender\\.com")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(ingest_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(feedback_router)


# ── Startup Event ─────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Preload models and initialize services on startup."""
    print("[STARTUP] Initializing iQuery API...")
    
    # Preload embedding model to avoid first-request delay
    try:
        from app.embeddings.embedder import _get_model
        print("[STARTUP] Loading embedding model...")
        _get_model()
        print("[STARTUP] Embedding model loaded successfully")
    except Exception as e:
        print(f"[STARTUP] Warning: Could not preload embedding model: {e}")
    
    print(f"[STARTUP] API ready on port {settings.app_port}")


# ── Health check ─────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"], summary="Health check")
async def health():
    """Returns a 200 OK with basic system info."""
    try:
        from app.vectorstore.chroma_store import get_collection_count
        chunk_count = get_collection_count()
    except Exception as e:
        print(f"[HEALTH] ChromaDB not ready: {e}")
        chunk_count = 0
    
    return {
        "status": "ok",
        "service": "iQuery API",
        "version": "2.0.0",
        "llm_provider": settings.llm_provider,
        "embedding_model": settings.embedding_model,
        "total_chunks_indexed": chunk_count,
    }


@app.get("/api/ready", tags=["System"], summary="Readiness probe")
async def ready():
    """Lightweight readiness check for load balancers."""
    return {"status": "ready"}


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "iQuery API v2.0 is running. Visit /docs for the interactive API reference."}


@app.options("/{path:path}", include_in_schema=False)
async def options_handler(path: str):
    """Handle CORS preflight requests for all paths."""
    from fastapi.responses import Response
    return Response(status_code=200)


@app.get("/api/debug/cors", tags=["Debug"], include_in_schema=False)
async def debug_cors():
    """Return current CORS configuration for debugging."""
    return {
        "allowed_origins": allowed_origins,
        "frontend_url_setting": settings.frontend_url,
        "cors_regex": "https://.*\\.onrender\\.com",
    }
