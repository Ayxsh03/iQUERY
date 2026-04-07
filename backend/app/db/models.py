"""
iQuery — Dataclass models matching the SQLite schema.

These are plain Python dataclasses — no ORM.
Used for type-safe reading/writing across the db layer.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumentRecord:
    id: Optional[int]
    filename: str
    upload_ts: str
    chunk_count: int
    status: str = "indexed"


@dataclass
class QueryLogRecord:
    id: Optional[int]
    query: str
    answer_preview: str
    chunks_retrieved: int
    latency_s: float
    ts: str


@dataclass
class FeedbackRecord:
    id: Optional[int]
    query: str
    answer: str
    rating: int
    comment: Optional[str]
    ts: str
