'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { api, DocumentMeta, QueryLogEntry, FeedbackEntry } from '@/lib/api';
import Link from 'next/link';
import {
  Upload, Trash2, RefreshCw, FileText, MessageSquare,
  Star, ArrowLeft, CheckCircle, AlertCircle, X, Clock,
  Zap, BarChart2, ChevronDown, ChevronUp,
} from 'lucide-react';

// ── Toast system ───────────────────────────────────────────────────────

type Toast = { id: string; message: string; type: 'success' | 'error' | 'info' };

function ToastContainer({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: string) => void }) {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map(t => (
        <div key={t.id}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl border text-sm animate-slide-up
            ${t.type === 'success' ? 'bg-emerald-900/90 border-emerald-700 text-emerald-200' :
              t.type === 'error'   ? 'bg-red-900/90 border-red-700 text-red-200' :
                                    'bg-blue-900/90 border-blue-700 text-blue-200'}`}>
          {t.type === 'success' ? <CheckCircle size={15} /> :
           t.type === 'error'   ? <AlertCircle size={15} /> :
                                  <Clock size={15} />}
          <span>{t.message}</span>
          <button onClick={() => onDismiss(t.id)} className="ml-2 opacity-60 hover:opacity-100">
            <X size={13} />
          </button>
        </div>
      ))}
    </div>
  );
}

// ── Drag & Drop Upload ─────────────────────────────────────────────────

function UploadZone({ onSuccess }: { onSuccess: () => void }) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState('');
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    const allowed = ['.pdf', '.docx', '.doc', '.txt'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowed.includes(ext)) {
      setError(`File type "${ext}" not supported. Use: ${allowed.join(', ')}`);
      return;
    }

    setError('');
    setUploading(true);
    setProgress(`Uploading ${file.name}…`);
    try {
      const res = await api.ingest(file);
      setProgress(`✓ Indexed "${res.filename}" — ${res.chunks_created} chunks in ${res.processing_time_s}s`);
      onSuccess();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setProgress('');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={e => { e.preventDefault(); setDragging(false); handleFiles(e.dataTransfer.files); }}
      onClick={() => !uploading && inputRef.current?.click()}
      className={`relative rounded-xl border-2 border-dashed p-8 text-center cursor-pointer
                  transition-all duration-200 ${dragging
                    ? 'border-[var(--brand)] bg-[var(--brand-glow)]'
                    : 'border-[var(--border)] hover:border-[var(--border-light)] hover:bg-[var(--bg-tertiary)]'
                  } ${uploading ? 'pointer-events-none opacity-80' : ''}`}
    >
      <input ref={inputRef} type="file" accept=".pdf,.docx,.doc,.txt"
             className="hidden" onChange={e => handleFiles(e.target.files)} />
      <Upload size={28} className={`mx-auto mb-3 ${dragging ? 'text-[var(--brand)]' : 'text-[var(--text-muted)]'}`} />
      <p className="text-sm font-medium text-[var(--text-primary)]">
        {uploading ? 'Processing…' : 'Drop a file or click to browse'}
      </p>
      <p className="text-xs text-[var(--text-muted)] mt-1">PDF, DOCX, DOC, TXT · Max 50 MB</p>
      {progress && (
        <p className="mt-3 text-xs text-[var(--success)] font-medium animate-fade-in">{progress}</p>
      )}
      {error && (
        <p className="mt-3 text-xs text-red-400 animate-fade-in">{error}</p>
      )}
      {uploading && (
        <div className="mt-4 h-1 bg-[var(--bg-tertiary)] rounded-full overflow-hidden">
          <div className="h-full bg-[var(--brand)] rounded-full animate-pulse" style={{ width: '60%' }} />
        </div>
      )}
    </div>
  );
}

// ── Documents Tab ──────────────────────────────────────────────────────

function DocumentsTab({ toast }: { toast: (msg: string, type?: Toast['type']) => void }) {
  const [docs, setDocs] = useState<DocumentMeta[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.listDocuments();
      setDocs(res.documents);
    } catch (e: unknown) {
      toast(e instanceof Error ? e.message : 'Failed to load documents', 'error');
    } finally { setLoading(false); }
  }, [toast]);

  useEffect(() => { refresh(); }, [refresh]);

  const handleDelete = async (filename: string) => {
    if (!confirm(`Delete "${filename}" from the index?`)) return;
    try {
      const res = await api.deleteDocument(filename);
      toast(res.message, 'success');
      refresh();
    } catch (e: unknown) { toast(e instanceof Error ? e.message : 'Delete failed', 'error'); }
  };

  const handleReindex = async (filename: string) => {
    try {
      const res = await api.reindex(filename);
      toast(res.message, 'info');
    } catch (e: unknown) { toast(e instanceof Error ? e.message : 'Reindex failed', 'error'); }
  };

  return (
    <div className="space-y-6">
      <UploadZone onSuccess={() => { toast('Document indexed successfully!', 'success'); refresh(); }} />

      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
          <FileText size={15} className="text-[var(--brand)]" />
          Indexed Documents
          {!loading && <span className="badge badge-blue">{docs.length}</span>}
        </h2>
        <button onClick={refresh} className="btn-ghost text-xs py-1.5 px-3">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {loading ? (
        <div className="space-y-2">
          {[1,2,3].map(i => (
            <div key={i} className="h-14 rounded-lg bg-[var(--bg-card)] border border-[var(--border)] animate-pulse" />
          ))}
        </div>
      ) : docs.length === 0 ? (
        <div className="card text-center py-12 text-[var(--text-muted)]">
          <FileText size={32} className="mx-auto mb-3 opacity-30" />
          <p className="text-sm">No documents indexed yet.</p>
          <p className="text-xs mt-1">Upload a PDF, DOCX, or TXT file above.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {docs.map((doc, i) => (
            <div key={i} className="card flex items-center gap-4 hover:border-[var(--border-light)] transition-all">
              <FileText size={18} className="text-[var(--brand)] shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-[var(--text-primary)] truncate">{doc.filename}</p>
                <p className="text-xs text-[var(--text-muted)]">
                  {doc.chunk_count} chunks
                  {doc.upload_ts && ` · ${new Date(doc.upload_ts).toLocaleDateString()}`}
                </p>
              </div>
              <span className={`badge shrink-0 ${doc.status === 'indexed' ? 'badge-green' : 'badge-red'}`}>
                {doc.status}
              </span>
              <div className="flex items-center gap-1.5 shrink-0">
                <button onClick={() => handleReindex(doc.filename)} className="btn-ghost text-xs py-1 px-2.5" title="Re-index info">
                  <RefreshCw size={12} />
                </button>
                <button onClick={() => handleDelete(doc.filename)} className="btn-danger" title="Delete">
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Logs Tab ───────────────────────────────────────────────────────────

function LogsTab({ toast }: { toast: (msg: string, type?: Toast['type']) => void }) {
  const [logs, setLogs] = useState<QueryLogEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<number | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getLogs(50);
      setLogs(res.logs);
      setTotal(res.total);
    } catch (e: unknown) { toast(e instanceof Error ? e.message : 'Failed to load logs', 'error'); }
    finally { setLoading(false); }
  }, [toast]);

  useEffect(() => { refresh(); }, [refresh]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
          <MessageSquare size={15} className="text-[var(--brand)]" />
          Query Logs
          {!loading && <span className="badge badge-blue">{total} total</span>}
        </h2>
        <button onClick={refresh} className="btn-ghost text-xs py-1.5 px-3">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {loading ? (
        <div className="space-y-2">
          {[1,2,3,4].map(i => <div key={i} className="h-16 rounded-lg bg-[var(--bg-card)] border border-[var(--border)] animate-pulse" />)}
        </div>
      ) : logs.length === 0 ? (
        <div className="card text-center py-12 text-[var(--text-muted)]">
          <MessageSquare size={32} className="mx-auto mb-3 opacity-30" />
          <p className="text-sm">No queries logged yet.</p>
          <p className="text-xs mt-1">Logs appear after the first chat query.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {logs.map((log) => (
            <div key={log.id} className="card hover:border-[var(--border-light)] transition-all cursor-pointer"
              onClick={() => setExpanded(expanded === log.id ? null : log.id)}>
              <div className="flex items-start gap-3">
                <MessageSquare size={14} className="text-[var(--brand)] shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-[var(--text-primary)] truncate">{log.query}</p>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-[var(--text-muted)] flex items-center gap-1">
                      <Clock size={10} /> {new Date(log.ts).toLocaleString()}
                    </span>
                    <span className="text-xs text-[var(--text-muted)] flex items-center gap-1">
                      <Zap size={10} /> {log.latency_s.toFixed(2)}s
                    </span>
                    <span className="text-xs text-[var(--text-muted)]">
                      {log.chunks_retrieved} chunks
                    </span>
                  </div>
                </div>
                {expanded === log.id ? <ChevronUp size={14} className="text-[var(--text-muted)] shrink-0" /> :
                                       <ChevronDown size={14} className="text-[var(--text-muted)] shrink-0" />}
              </div>
              {expanded === log.id && log.answer_preview && (
                <div className="mt-3 pt-3 border-t border-[var(--border)] animate-fade-in">
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed italic">
                    "{log.answer_preview}{log.answer_preview.length >= 300 ? '…' : ''}"
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Feedback Tab ───────────────────────────────────────────────────────

function FeedbackTab({ toast }: { toast: (msg: string, type?: Toast['type']) => void }) {
  const [feedback, setFeedback] = useState<FeedbackEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.getFeedback(50);
      setFeedback(res.feedback);
      setTotal(res.total);
    } catch (e: unknown) { toast(e instanceof Error ? e.message : 'Failed to load feedback', 'error'); }
    finally { setLoading(false); }
  }, [toast]);

  useEffect(() => { refresh(); }, [refresh]);

  const avg = feedback.length > 0
    ? (feedback.reduce((s, f) => s + f.rating, 0) / feedback.length).toFixed(1)
    : null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
          <Star size={15} className="text-[var(--brand)]" />
          Feedback
          {!loading && <span className="badge badge-blue">{total} responses</span>}
          {avg && <span className="badge badge-yellow">{avg} avg ★</span>}
        </h2>
        <button onClick={refresh} className="btn-ghost text-xs py-1.5 px-3">
          <RefreshCw size={13} className={loading ? 'animate-spin' : ''} /> Refresh
        </button>
      </div>

      {!loading && feedback.length > 0 && (
        <div className="grid grid-cols-3 gap-3">
          {[5,4,3,2,1].slice(0,3).map(r => {
            const count = feedback.filter(f => f.rating === r).length;
            const pct = Math.round((count / feedback.length) * 100);
            return (
              <div key={r} className="card text-center">
                <p className="text-2xl font-bold text-[var(--text-primary)]">{count}</p>
                <p className="text-xs text-[var(--text-muted)]">{'★'.repeat(r)} ({pct}%)</p>
              </div>
            );
          })}
        </div>
      )}

      {loading ? (
        <div className="space-y-2">
          {[1,2,3].map(i => <div key={i} className="h-16 rounded-lg bg-[var(--bg-card)] border border-[var(--border)] animate-pulse" />)}
        </div>
      ) : feedback.length === 0 ? (
        <div className="card text-center py-12 text-[var(--text-muted)]">
          <Star size={32} className="mx-auto mb-3 opacity-30" />
          <p className="text-sm">No feedback submitted yet.</p>
          <p className="text-xs mt-1">Rate answers in the chat by clicking ★ stars.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {feedback.map(f => (
            <div key={f.id} className="card">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-[var(--text-primary)] truncate">{f.query}</p>
                  {f.comment && (
                    <p className="text-xs text-[var(--text-muted)] mt-1 italic">"{f.comment}"</p>
                  )}
                </div>
                <div className="shrink-0 flex items-center gap-2">
                  <span className="text-yellow-400 text-sm font-medium">{'★'.repeat(f.rating)}{'☆'.repeat(5-f.rating)}</span>
                  <span className="text-xs text-[var(--text-muted)]">{new Date(f.ts).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Admin page ─────────────────────────────────────────────────────────

type Tab = 'documents' | 'logs' | 'feedback';

export default function AdminPage() {
  const [tab, setTab] = useState<Tab>('documents');
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: Toast['type'] = 'success') => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000);
  }, []);

  const dismissToast = (id: string) => setToasts(prev => prev.filter(t => t.id !== id));

  const tabs = [
    { id: 'documents' as Tab, label: 'Documents', icon: FileText },
    { id: 'logs'      as Tab, label: 'Query Logs', icon: BarChart2 },
    { id: 'feedback'  as Tab, label: 'Feedback',  icon: Star },
  ];

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
      {/* Header */}
      <header className="border-b border-[var(--border)] bg-[var(--bg-secondary)]">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex items-center gap-4">
          <Link href="/" className="btn-ghost text-xs py-1.5 px-3">
            <ArrowLeft size={13} /> Chat
          </Link>
          <div>
            <h1 className="font-semibold text-[var(--text-primary)]">Admin Panel</h1>
            <p className="text-xs text-[var(--text-muted)]">Document management & analytics</p>
          </div>
        </div>
        {/* Tabs */}
        <div className="max-w-5xl mx-auto px-4 sm:px-6 flex gap-1 pb-0 border-t border-[var(--border)] mt-3">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-all duration-200
                ${tab === id
                  ? 'border-[var(--brand)] text-[var(--brand)]'
                  : 'border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                }`}
            >
              <Icon size={14} />{label}
            </button>
          ))}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {tab === 'documents' && <DocumentsTab toast={addToast} />}
        {tab === 'logs'      && <LogsTab      toast={addToast} />}
        {tab === 'feedback'  && <FeedbackTab  toast={addToast} />}
      </main>

      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
}
