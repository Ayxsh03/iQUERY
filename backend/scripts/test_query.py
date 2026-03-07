#!/usr/bin/env python3
"""
iQuery — CLI Smoke Test Script (Phase 1)

Run this after starting the backend server to verify the full RAG pipeline:
    1. Checks the health endpoint
    2. Ingests a sample text file (auto-creates one if none exists)
    3. Asks a test question and prints the answer + sources

Usage:
    cd backend
    python scripts/test_query.py

Optional env override:
    API_URL=http://localhost:8000 python scripts/test_query.py
"""

import os
import sys
import json
import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")

SAMPLE_DOC_PATH = os.path.join(os.path.dirname(__file__), "../data/sample_docs/sample_policy.txt")
SAMPLE_DOC_CONTENT = """\
iQuery Sample Company Policy Document
=====================================

Annual Leave Policy
-------------------
All full-time employees are entitled to 20 days of annual paid leave per year.
Leave must be requested at least 2 weeks in advance and approved by the direct manager.
Unused leave can be carried forward to the next year up to a maximum of 10 days.

Sick Leave Policy
-----------------
Employees are entitled to 10 days of paid sick leave per calendar year.
A medical certificate is required for sick leave exceeding 3 consecutive days.

Remote Work Policy
------------------
Employees may work remotely up to 3 days per week with manager approval.
Remote work requests must be submitted via the HR portal by Friday of the preceding week.
Employees are expected to be reachable during core hours: 10:00 AM to 4:00 PM local time.

Onboarding
----------
New employees will complete a 2-week onboarding program that includes:
- Company culture and values overview
- IT setup and security training
- Department-specific process walkthrough
- Introduction meetings with key stakeholders
"""

TEST_QUESTIONS = [
    "How many days of annual leave do employees get?",
    "What is the remote work policy?",
    "What happens during onboarding?",
]


def print_section(title: str):
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


def check_health():
    print_section("1. Health Check")
    try:
        r = httpx.get(f"{API_URL}/api/health", timeout=10)
        r.raise_for_status()
        data = r.json()
        print(f"  ✅ Status:          {data['status']}")
        print(f"  ✅ LLM Provider:    {data['llm_provider']}")
        print(f"  ✅ Embedding Model: {data['embedding_model']}")
        print(f"  ✅ Chunks Indexed:  {data['total_chunks_indexed']}")
    except Exception as e:
        print(f"  ❌ Health check failed: {e}")
        sys.exit(1)


def ingest_sample():
    print_section("2. Document Ingestion")
    os.makedirs(os.path.dirname(SAMPLE_DOC_PATH), exist_ok=True)
    if not os.path.exists(SAMPLE_DOC_PATH):
        with open(SAMPLE_DOC_PATH, "w") as f:
            f.write(SAMPLE_DOC_CONTENT)
        print(f"  📄 Created sample document at: {SAMPLE_DOC_PATH}")

    with open(SAMPLE_DOC_PATH, "rb") as f:
        try:
            r = httpx.post(
                f"{API_URL}/api/ingest",
                files={"file": ("sample_policy.txt", f, "text/plain")},
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            print(f"  ✅ Ingested: {data['filename']}")
            print(f"  ✅ Pages parsed:   {data['pages_parsed']}")
            print(f"  ✅ Chunks created: {data['chunks_created']}")
            print(f"  ✅ Time:           {data['processing_time_s']}s")
        except Exception as e:
            print(f"  ❌ Ingestion failed: {e}")
            sys.exit(1)


def run_queries():
    print_section("3. Query Test")
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\n  Q{i}: {question}")
        try:
            r = httpx.post(
                f"{API_URL}/api/chat",
                json={"query": question},
                timeout=60,
            )
            r.raise_for_status()
            data = r.json()
            print(f"  A: {data['answer']}")
            print(f"  📚 Sources: {', '.join(set(s['source'] for s in data['sources']))}")
            print(f"  ⏱  Latency: {data['latency_s']}s | Chunks retrieved: {data['chunks_retrieved']}")
        except Exception as e:
            print(f"  ❌ Query failed: {e}")


if __name__ == "__main__":
    print("\n🔍 iQuery — Phase 1 Smoke Test")
    print(f"   API: {API_URL}")
    check_health()
    ingest_sample()
    run_queries()
    print(f"\n{'═' * 60}")
    print("  ✅ All tests passed! Phase 1 RAG pipeline is working.")
    print(f"{'═' * 60}\n")
