<div align="center">

# 🔍 iQuery

### Internal Document-Grounded Chatbot using RAG

*Ask questions. Get answers. Grounded in your company's own documents.*

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/Vector_Store-ChromaDB-orange)](https://www.trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🧠 What is iQuery?

**iQuery** is an open-source, internal knowledge chatbot built for startups and SMEs. It uses **Retrieval-Augmented Generation (RAG)** to answer employee questions strictly from company documents — HR policies, IT guides, onboarding handbooks, technical manuals — without hallucinating.

**No paid APIs required.** Everything runs locally or on a free tier.

---

## 🏗 Architecture Overview

```
User Query
    │
    ▼
[ FastAPI Backend ]
    │
    ├──► Embedder (SentenceTransformers)
    │         │
    │         ▼
    │    ChromaDB (vector search)
    │         │
    │         ▼
    └──► Retrieved Chunks ──► LLM (Groq / Ollama)
                                    │
                                    ▼
                            Answer + Source Citations
```

---

## ⚡ Tech Stack

| Component | Technology |
|---|---|
| Backend Framework | FastAPI |
| Embeddings | SentenceTransformers (`all-MiniLM-L6-v2`) |
| Vector Store | ChromaDB (persistent, local) |
| LLM (primary) | Groq API — `llama3-8b-8192` (free tier) |
| LLM (fallback) | Ollama — `mistral` (fully local) |
| Document Parsing | PyPDF2, python-docx |
| Text Chunking | LangChain RecursiveCharacterTextSplitter |

---

## 🚀 Phase 1 — What's Working

- [x] Upload PDF, DOCX, and TXT documents via API
- [x] Automatic text extraction and chunking
- [x] Dense embeddings stored in ChromaDB
- [x] Cosine-similarity retrieval
- [x] Grounded answer generation (Groq / Ollama)
- [x] Source citations with page numbers
- [x] CLI smoke test script

---

## 📁 Project Structure

```
iQUERY/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── config.py             # Settings (env vars)
│   │   ├── ingestion/            # Document loading + chunking
│   │   ├── embeddings/           # SentenceTransformers wrapper
│   │   ├── vectorstore/          # ChromaDB CRUD
│   │   ├── retrieval/            # Query → top-k chunks
│   │   ├── generation/           # LLM prompt + response
│   │   └── api/                  # FastAPI routers
│   ├── data/sample_docs/         # Sample documents for testing
│   ├── scripts/test_query.py     # CLI smoke test
│   ├── requirements.txt
│   └── .env.example
└── README.md
```

---

## 🛠 Local Setup

### Prerequisites
- Python 3.10+
- A free [Groq API key](https://console.groq.com) (takes 30 seconds to get)

### 1. Clone the repository
```bash
git clone https://github.com/Ayxsh03/iQUERY.git
cd iQUERY
```

### 2. Set up Python environment
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 4. Start the server
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`

---

## 📖 API Usage

### Interactive docs
Visit `http://localhost:8000/docs` for the full Swagger UI.

### Ingest a document
```bash
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@/path/to/your/document.pdf"
```

**Response:**
```json
{
  "filename": "company_policy.pdf",
  "pages_parsed": 12,
  "chunks_created": 47,
  "processing_time_s": 2.3,
  "message": "Successfully indexed 'company_policy.pdf' with 47 chunks."
}
```

### Ask a question
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the annual leave policy?"}'
```

**Response:**
```json
{
  "query": "What is the annual leave policy?",
  "answer": "Full-time employees are entitled to 20 days of annual paid leave per year...",
  "sources": [
    {
      "source": "company_policy.pdf",
      "page": 3,
      "excerpt": "All full-time employees are entitled to 20 days of annual paid leave...",
      "relevance": 0.92
    }
  ],
  "chunks_retrieved": 5,
  "latency_s": 1.2
}
```

### Run the CLI smoke test
```bash
# With the server running:
python scripts/test_query.py
```

---

## 🔧 Configuration

All settings are controlled via `.env`:

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `groq` | `groq` or `ollama` |
| `GROQ_API_KEY` | — | Your Groq API key |
| `GROQ_MODEL` | `llama3-8b-8192` | Model name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformers model |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Chunks retrieved per query |

---

## 🗺 Roadmap

- **Phase 1 ✅** — RAG Backend (this phase)
- **Phase 2 🔜** — Web Chat UI (Next.js) with source citations
- **Phase 3 🔜** — Admin Panel, feedback collection, evaluation, deployment

---

## 📄 License

MIT — see [LICENSE](LICENSE)
