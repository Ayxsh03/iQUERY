<div align="center">

# 🔍 iQuery

### Internal Document-Grounded Chatbot using RAG

*Ask questions. Get answers. Grounded strictly in your company's own documents.*

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org)
[![ChromaDB](https://img.shields.io/badge/Vector_Store-ChromaDB-orange)](https://www.trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🧠 What is iQuery?

**iQuery** is an open-source, internal knowledge chatbot built for startups and SMEs. It uses **Retrieval-Augmented Generation (RAG)** to answer employee questions strictly from company documents — HR policies, IT guides, onboarding handbooks, technical manuals — without hallucinating.

**Phase 1 & 2 Complete.** This final version includes a beautiful Next.js frontend, an admin analytics panel, source citations, user feedback loops, and full Docker deployment support.

---

## ✨ Features

- 💬 **Grounded Chat**: Answers are generated *strictly* using the context from uploaded documents.
- 📄 **Source Citations**: Every answer includes expandable cards showing exact document names, page numbers, and text excerpts.
- 📂 **Multi-Format Ingestion**: Drag-and-drop upload for PDF, DOCX, and TXT files.
- 📊 **Admin Dashboard**: Manage indexed documents, view query logs, and monitor system latency.
- ⭐ **Feedback Loop**: Users can rate answers (1-5 stars) to help evaluate RAG quality over time.
- 🐳 **Docker-Ready**: Simple deployment via `docker-compose.yml`.

---

## ⚡ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend** | Next.js 14, Tailwind CSS | Dark-themed, responsive React UI |
| **Backend** | FastAPI | High-performance async Python API |
| **Vector DB** | ChromaDB | Local vector store for document embeddings |
| **Metadata DB** | SQLite | Tracks document status, query logs, and feedback |
| **Embeddings** | SentenceTransformers | `all-MiniLM-L6-v2` runs locally and free |
| **LLM** | Groq API / Ollama | Configurable AI generator (defaults to free Groq `llama3-8b`) |
| **Parsing** | PyPDF2, python-docx | Text extraction pipelines |

---

## 🏗 Architecture

iQuery uses a clear separation of concerns. The Next.js frontend communicates purely with the FastAPI backend. The backend manages the RAG pipeline: file parsing → chunking → embedding → ChromaDB storage → retrieval → LLM generation.

For a detailed view, see [docs/architecture.md](docs/architecture.md).

---

## 🛠 Local Setup

### Prerequisites
- Docker & Docker Compose (Recommended)
- OR Python 3.11+ and Node.js 20+
- A free [Groq API key](https://console.groq.com)

### Quick Start (Docker)

1. **Clone the repo**
   ```bash
   git clone https://github.com/Ayxsh03/iQUERY.git
   cd iQUERY
   ```

2. **Configure Environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env to add your GROQ_API_KEY
   ```

3. **Start everything**
   ```bash
   docker compose up --build
   ```

4. **Visit the app**
   - Frontend web app: `http://localhost:3000`
   - Interactive Backend API docs: `http://localhost:8000/docs`

---

## 🚀 Deployment (Render Free Tier)

For full step-by-step instructions on deploying the split frontend and backend containers to the web for free, read the [Render Deployment Guide](docs/deployment.md).

> **Note on Free Hosting**: Render's free tier uses ephemeral storage. This means uploaded documents in ChromaDB and SQLite will reset when the instance sleeps. For university viva/demo purposes, simply upload fresh documents at the beginning of the presentation.

---

## 📖 Detailed Guides

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment.md)

---

## 🎓 Final Project Demo Script

1. **Start fresh**: Open the frontend `http://localhost:3000`. Show the welcome screen.
2. **Setup**: Go to the **Admin** panel (gear icon).
3. **Upload**: Drag and drop a sample PDF (e.g., an IT policy document). Watch the upload progress and see it appear in the Documents list.
4. **Query**: Return to the **Chat** screen. Ask a specific question covered by the uploaded PDF.
5. **Citations**: Expand the source cards attached to the bot's response to prove the answer was grounded.
6. **Feedback**: Click the star rating under the answer to show the feedback loop.
7. **Analytics**: Go back to the **Admin** panel. Open the **Query Logs** tab to show latency and chunk stats. Open the **Feedback** tab to show the captured rating.

---

## 📄 License
MIT — see [LICENSE](LICENSE)

