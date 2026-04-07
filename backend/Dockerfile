# ─── Build stage ────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for chromadb / sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─── Runtime stage ──────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Crucial for 512MB free tier: limit PyTorch/OpenBLAS threads so memory doesn't spike
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV VECLIB_MAXIMUM_THREADS=1
ENV NUMEXPR_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ ./app/
COPY scripts/ ./scripts/ 2>/dev/null || true

# Create data directories (ChromaDB + SQLite will use these)
RUN mkdir -p /app/chroma_db /app/data

# Pre-download the embedding model to avoid runtime download delay
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Expose API port
EXPOSE 8000

# Health check - increased start-period to 120s for model loading
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD python -c "import urllib.request, os; port = os.environ.get('PORT', '8000'); urllib.request.urlopen(f'http://localhost:{port}/api/health')"

# Use shell form to allow environment variable expansion for PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
