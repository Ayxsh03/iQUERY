"""
LLM Generation module — sends a grounded prompt to Groq (primary) or
Ollama (fallback) and returns the model's answer.

Design principle:
- The prompt strictly confines the model to the retrieved context.
- If context is insufficient, the model is instructed to say so rather
  than hallucinate.
"""

import time
from typing import List, Dict, Any, Tuple

import httpx
from groq import Groq

from app.config import get_settings


# ── Prompt templates ──────────────────────────────────────────────────

SYSTEM_PROMPT = """You are iQuery, an internal knowledge assistant for employees.

Your ONLY job is to answer questions using the CONTEXT provided below.

Rules you MUST follow:
1. Answer ONLY based on the provided context. Do NOT use outside knowledge.
2. If the context does not contain enough information, respond with:
   "I don't have enough information in the uploaded documents to answer this question."
3. Be concise and direct. Avoid unnecessary preamble.
4. When quoting or referencing specific details, mention the source document name.
5. Never make up facts, policies, numbers, or names.
"""

USER_PROMPT_TEMPLATE = """CONTEXT (retrieved from company documents):
{context}

---

QUESTION: {question}

Provide a clear, direct answer based only on the context above. If you reference specific information, mention which document it came from."""


def _build_context_string(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks into a readable context block."""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "unknown")
        page = chunk.get("page", "?")
        text = chunk.get("text", "").strip()
        context_parts.append(f"[{i}] Source: {source} (Page {page})\n{text}")

    return "\n\n".join(context_parts)


def generate_answer(
    query: str,
    chunks: List[Dict[str, Any]],
) -> Tuple[str, float]:
    """
    Generate an answer from retrieved chunks using the configured LLM.

    Args:
        query:  The user's question.
        chunks: Retrieved context chunks from the retriever.

    Returns:
        Tuple of (answer_text, latency_seconds)
    """
    settings = get_settings()
    context = _build_context_string(chunks)
    user_message = USER_PROMPT_TEMPLATE.format(context=context, question=query)

    start_time = time.time()

    if settings.llm_provider == "groq":
        answer = _generate_groq(user_message, settings)
    elif settings.llm_provider == "ollama":
        answer = _generate_ollama(user_message, settings)
    else:
        raise ValueError(f"Unknown LLM provider: '{settings.llm_provider}'")

    latency = round(time.time() - start_time, 3)
    return answer, latency


def _generate_groq(user_message: str, settings) -> str:
    """Call the Groq API and return the completion text."""
    if not settings.groq_api_key:
        raise ValueError(
            "GROQ_API_KEY is not set. Add it to your .env file."
        )

    client = Groq(api_key=settings.groq_api_key)

    completion = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,   # low temperature for factual grounding
        max_tokens=1024,
    )

    return completion.choices[0].message.content.strip()


def _generate_ollama(user_message: str, settings) -> str:
    """Call a local Ollama instance and return the completion text."""
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }

    response = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        json=payload,
        timeout=120.0,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"].strip()
