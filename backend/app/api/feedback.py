"""
Feedback API router.

Allows users to submit a rating (1–5) and optional comment
for any chatbot answer. Data is stored in SQLite.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.db.database import get_db

router = APIRouter(prefix="/api", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="The original user query")
    answer: str = Field(..., min_length=1, max_length=5000, description="The chatbot's answer")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    comment: Optional[str] = Field(default=None, max_length=1000, description="Optional text comment")


class FeedbackResponse(BaseModel):
    id: int
    message: str


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit feedback for a chatbot answer",
)
async def submit_feedback(payload: FeedbackRequest):
    """
    Log user feedback (rating + optional comment) for a given query/answer pair.
    Used to evaluate RAG quality over time.
    """
    ts = datetime.now(timezone.utc).isoformat()

    try:
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO feedback (query, answer, rating, comment, ts) VALUES (?, ?, ?, ?, ?)",
                (
                    payload.query,
                    payload.answer[:1000],  # truncate long answers for storage
                    payload.rating,
                    payload.comment,
                    ts,
                ),
            )
            new_id = cursor.lastrowid

        return FeedbackResponse(
            id=new_id,
            message="Thank you! Your feedback has been recorded.",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {str(e)}")
