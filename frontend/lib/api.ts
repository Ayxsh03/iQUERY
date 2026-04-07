/**
 * iQuery API client
 * Centralizes all fetch calls to the backend so components don't
 * contain raw URLs or error-handling boilerplate.
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export type Source = {
  source: string;
  page: number;
  excerpt: string;
  relevance: number;
};

export type ChatResponse = {
  query: string;
  answer: string;
  sources: Source[];
  chunks_retrieved: number;
  latency_s: number;
};

export type DocumentMeta = {
  id?: number;
  filename: string;
  upload_ts?: string;
  chunk_count: number;
  status: string;
};

export type QueryLogEntry = {
  id: number;
  query: string;
  answer_preview: string | null;
  chunks_retrieved: number;
  latency_s: number;
  ts: string;
};

export type FeedbackEntry = {
  id: number;
  query: string;
  answer: string | null;
  rating: number;
  comment: string | null;
  ts: string;
};

export type IngestResponse = {
  filename: string;
  pages_parsed: number;
  chunks_created: number;
  processing_time_s: number;
  message: string;
};

export type HealthResponse = {
  status: string;
  service: string;
  version: string;
  llm_provider: string;
  embedding_model: string;
  total_chunks_indexed: number;
};

// ── Helper ────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? `Request failed: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ── API Methods ───────────────────────────────────────────────────────

export const api = {
  health(): Promise<HealthResponse> {
    return apiFetch('/api/health');
  },

  chat(query: string, topK?: number): Promise<ChatResponse> {
    return apiFetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK }),
    });
  },

  ingest(file: File): Promise<IngestResponse> {
    const form = new FormData();
    form.append('file', file);
    return apiFetch('/api/ingest', { method: 'POST', body: form });
  },

  listDocuments(): Promise<{ documents: DocumentMeta[]; total: number }> {
    return apiFetch('/api/admin/documents');
  },

  deleteDocument(filename: string): Promise<{ message: string; chunks_removed: number }> {
    return apiFetch(`/api/admin/documents/${encodeURIComponent(filename)}`, {
      method: 'DELETE',
    });
  },

  reindex(filename: string): Promise<{ message: string }> {
    return apiFetch(`/api/admin/reindex/${encodeURIComponent(filename)}`, {
      method: 'POST',
    });
  },

  getLogs(limit = 50): Promise<{ logs: QueryLogEntry[]; total: number }> {
    return apiFetch(`/api/admin/logs?limit=${limit}`);
  },

  getFeedback(limit = 50): Promise<{ feedback: FeedbackEntry[]; total: number }> {
    return apiFetch(`/api/admin/feedback?limit=${limit}`);
  },

  submitFeedback(payload: {
    query: string;
    answer: string;
    rating: number;
    comment?: string;
  }): Promise<{ id: number; message: string }> {
    return apiFetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },
};
