'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { api, ChatResponse, Source } from '@/lib/api';
import Link from 'next/link';
import { Send, Trash2, MessageSquare, BookOpen, Settings, Zap } from 'lucide-react';

// ── Types ──────────────────────────────────────────────────────────────

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  latency?: number;
  timestamp: Date;
};

// ── Sub-components ─────────────────────────────────────────────────────

function TypingDots() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3">
      <div className="dot dot-1" />
      <div className="dot dot-2" />
      <div className="dot dot-3" />
    </div>
  );
}

function SourceCard({ source }: { source: Source }) {
  const [expanded, setExpanded] = useState(false);
  const pct = Math.round(source.relevance * 100);
  const barColor = pct >= 80 ? '#34d399' : pct >= 60 ? '#f59e0b' : '#9196aa';

  return (
    <div
      className="rounded-lg border border-[var(--border)] bg-[var(--bg-secondary)] overflow-hidden
                 hover:border-[var(--border-light)] transition-all duration-200"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 px-3 py-2.5 text-left"
      >
        <BookOpen size={13} className="text-[var(--brand)] shrink-0" />
        <span className="text-xs font-medium text-[var(--text-secondary)] truncate flex-1">
          {source.source}
        </span>
        <span className="text-xs text-[var(--text-muted)] shrink-0">p.{source.page}</span>
        <div className="flex items-center gap-1.5 shrink-0">
          <div className="w-16 h-1.5 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
            <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: barColor }} />
          </div>
          <span className="text-xs" style={{ color: barColor }}>{pct}%</span>
        </div>
      </button>
      {expanded && (
        <div className="px-3 pb-3 border-t border-[var(--border)] animate-fade-in">
          <p className="text-xs text-[var(--text-muted)] mt-2 leading-relaxed italic">
            "{source.excerpt}"
          </p>
        </div>
      )}
    </div>
  );
}

function UserBubble({ message }: { message: Message }) {
  return (
    <div className="flex justify-end animate-slide-up">
      <div className="max-w-[75%]">
        <div className="rounded-2xl rounded-tr-sm px-4 py-3 bg-[var(--brand)] text-white text-sm leading-relaxed">
          {message.content}
        </div>
        <p className="text-right text-xs text-[var(--text-muted)] mt-1 pr-1">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </p>
      </div>
    </div>
  );
}

function AssistantBubble({ message }: { message: Message }) {
  const [feedbackSent, setFeedbackSent] = useState<number | null>(null);
  const [feedbackError, setFeedbackError] = useState('');

  const handleFeedback = async (rating: number) => {
    try {
      await api.submitFeedback({ query: message.content, answer: message.content, rating });
      setFeedbackSent(rating);
    } catch {
      setFeedbackError('Could not save feedback');
    }
  };

  return (
    <div className="flex gap-3 animate-slide-up">
      {/* Avatar */}
      <div className="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--brand)] to-purple-600
                      flex items-center justify-center text-white text-xs font-bold shadow-lg">
        iQ
      </div>
      <div className="flex-1 min-w-0">
        <div className="rounded-2xl rounded-tl-sm px-4 py-3 bg-[var(--bg-card)] border border-[var(--border)] text-sm leading-relaxed text-[var(--text-primary)] whitespace-pre-wrap">
          {message.content}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 space-y-1.5">
            <p className="text-xs font-medium text-[var(--text-muted)] flex items-center gap-1.5">
              <BookOpen size={11} /> Sources ({message.sources.length})
            </p>
            {message.sources.map((s, i) => (
              <SourceCard key={i} source={s} />
            ))}
          </div>
        )}

        {/* Footer: latency + feedback */}
        <div className="flex items-center gap-3 mt-2">
          {message.latency !== undefined && (
            <span className="flex items-center gap-1 text-xs text-[var(--text-muted)]">
              <Zap size={10} /> {message.latency.toFixed(2)}s
            </span>
          )}
          {!feedbackSent ? (
            <div className="flex items-center gap-1 ml-auto">
              {[1, 2, 3, 4, 5].map(r => (
                <button
                  key={r}
                  onClick={() => handleFeedback(r)}
                  className="text-[var(--text-muted)] hover:text-yellow-400 transition-colors text-xs"
                  title={`Rate ${r}/5`}
                >★</button>
              ))}
              {feedbackError && <span className="text-xs text-red-400 ml-1">{feedbackError}</span>}
            </div>
          ) : (
            <span className="text-xs text-[var(--success)] ml-auto">
              Thanks! Rated {feedbackSent}/5 ★
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-8 pb-20 px-4">
      <div className="text-center space-y-3">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--brand)] to-purple-600
                        flex items-center justify-center text-white text-2xl font-bold shadow-2xl mx-auto">
          iQ
        </div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">iQuery</h1>
        <p className="text-[var(--text-secondary)] max-w-sm">
          Your internal knowledge assistant. Ask anything about your company documents.
        </p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md">
        {[
          'What is the annual leave policy?',
          'How do I submit an expense report?',
          'What are the IT security guidelines?',
          'Who do I contact for onboarding help?',
        ].map(q => (
          <div key={q} className="card text-sm text-[var(--text-secondary)] cursor-default
                                  hover:border-[var(--border-light)] hover:text-[var(--text-primary)]
                                  transition-all duration-200 text-center py-3 px-3">
            {q}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Main page ──────────────────────────────────────────────────────────

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Persist chat history in localStorage
  useEffect(() => {
    const saved = localStorage.getItem('iquery_chat');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setMessages(parsed.map((m: Message) => ({ ...m, timestamp: new Date(m.timestamp) })));
      } catch { /* ignore */ }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('iquery_chat', JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = useCallback(async () => {
    const q = input.trim();
    if (!q || loading) return;

    setInput('');
    setError('');

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: q,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const data: ChatResponse = await api.chat(q);
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        latency: data.latency_s,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setError(msg.includes('No documents') ? '⚠️ No documents indexed yet. Upload files in Admin first.' : `Error: ${msg}`);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading]);

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="flex items-center justify-between px-4 sm:px-6 py-3.5
                         border-b border-[var(--border)] bg-[var(--bg-secondary)] shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--brand)] to-purple-600
                          flex items-center justify-center text-white text-xs font-bold">
            iQ
          </div>
          <div>
            <h1 className="font-semibold text-sm text-[var(--text-primary)]">iQuery</h1>
            <p className="text-xs text-[var(--text-muted)]">Internal Knowledge Chatbot</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/admin" className="btn-ghost text-xs py-1.5 px-3">
            <Settings size={13} /> Admin
          </Link>
          {messages.length > 0 && (
            <button onClick={() => { setMessages([]); localStorage.removeItem('iquery_chat'); }}
              className="btn-ghost text-xs py-1.5 px-3 text-red-400 hover:text-red-300">
              <Trash2 size={13} /> Clear
            </button>
          )}
        </div>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
        <div className="max-w-3xl mx-auto">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="space-y-6">
              {messages.map(m =>
                m.role === 'user'
                  ? <UserBubble key={m.id} message={m} />
                  : <AssistantBubble key={m.id} message={m} />
              )}
              {loading && (
                <div className="flex gap-3">
                  <div className="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--brand)] to-purple-600
                                  flex items-center justify-center text-white text-xs font-bold">
                    iQ
                  </div>
                  <div className="rounded-2xl rounded-tl-sm bg-[var(--bg-card)] border border-[var(--border)]">
                    <TypingDots />
                  </div>
                </div>
              )}
            </div>
          )}
          {error && (
            <div className="mt-4 p-3 rounded-lg bg-red-900/20 border border-red-800/50 text-red-300 text-sm animate-fade-in">
              {error}
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input */}
      <footer className="shrink-0 px-4 sm:px-6 py-4 border-t border-[var(--border)] bg-[var(--bg-secondary)]">
        <div className="max-w-3xl mx-auto">
          <div className="relative flex items-end gap-2 rounded-xl border border-[var(--border)]
                          bg-[var(--bg-tertiary)] p-2 focus-within:border-[var(--brand)]
                          transition-colors duration-200">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask a question about your documents..."
              rows={1}
              className="flex-1 resize-none bg-transparent px-2 py-1.5 text-sm
                         text-[var(--text-primary)] placeholder-[var(--text-muted)]
                         outline-none max-h-40 leading-relaxed"
              style={{ scrollbarWidth: 'none' }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="btn-primary shrink-0 rounded-lg px-3 py-2"
            >
              <Send size={15} />
            </button>
          </div>
          <p className="text-xs text-[var(--text-muted)] text-center mt-2">
            <MessageSquare className="inline w-3 h-3 mr-1" />
            Answers are grounded in your uploaded documents · Enter to send · Shift+Enter for newline
          </p>
        </div>
      </footer>
    </div>
  );
}
