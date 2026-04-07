# iQuery — API Reference

The FastAPI backend exposes the following endpoints. 
All endpoints are prefixed with `/api`.
For interactive testing, run the backend and visit `http://localhost:8000/docs`.

### System
- `GET /api/health`
  - **Returns**: Server status, version, configured LLM, and total chunk count.

### Ingestion (RAG Pipeline)
- `POST /api/ingest`
  - **Body**: `multipart/form-data` with a `file` field (.pdf, .docx, .txt).
  - **Action**: Extracts text, chunks it, generates embeddings, stores in ChromaDB, and logs metadata to SQLite.
  - **Returns**: Filename, chunk count, and processing time.

### Chat (RAG Pipeline)
- `POST /api/chat`
  - **Body**: `{"query": "your question", "top_k": 5}`
  - **Action**: Retrieves top-K chunks, generates grounded answer, logs query analytics to SQLite.
  - **Returns**: The text answer, list of source references (document name, page, excerpt), and latency.

### Admin Tools
- `GET /api/admin/documents`
  - **Returns**: Array of indexed documents merged from SQLite metadata and ChromaDB state.
- `DELETE /api/admin/documents/{filename}`
  - **Action**: Purges the document chunks from ChromaDB and marks it deleted in SQLite.
- `POST /api/admin/reindex/{filename}`
  - **Action**: Returns instructions to re-upload (to preserve ephemeral storage, original file bytes aren't kept globally).
- `GET /api/admin/logs`
  - **Returns**: Most recent chat queries, answers, latency stats, and chunk retrieval counts.
- `GET /api/admin/feedback`
  - **Returns**: All user-submitted feedback (1-5 stars) and comments.

### Feedback
- `POST /api/feedback`
  - **Body**: `{"query": "the question", "answer": "the answer", "rating": 5, "comment": "optional"}`
  - **Action**: Saves the feedback to the SQLite database.
