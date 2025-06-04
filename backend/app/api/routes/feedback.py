from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.api.deps import CurrentUser, SessionDep
from app.models import LlmInteraction, Message

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    interaction_id: uuid.UUID
    feedback: str  # 'correct' or 'incorrect'
    feedback_text: Optional[str] = None


@router.post("/", response_model=Message)
def submit_feedback(
    session: SessionDep, current_user: CurrentUser, request: FeedbackRequest = Depends()
):
    """Submit feedback for an LLM interaction."""
    # Find the interaction
    interaction = session.get(LlmInteraction, request.interaction_id)

    # Verify that the interaction exists and belongs to the user
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    if interaction.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to provide feedback on this interaction",
        )

    # Update the interaction with the feedback
    interaction.feedback = request.feedback
    interaction.feedback_text = request.feedback_text
    interaction.feedback_date = datetime.utcnow()

    session.add(interaction)
    session.commit()

    return Message(message="Feedback submitted successfully")
