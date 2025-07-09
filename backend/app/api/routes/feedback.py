import uuid
from datetime import datetime, timezone


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.models import ToolInteraction, Message

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    interaction_id: uuid.UUID
    feedback: str  # 'correct' or 'incorrect'
    feedback_text: str | None = None


@router.post("/", response_model=Message)
async def submit_feedback(
    session: SessionDep, request: FeedbackRequest = Depends()
) -> Message:
    """Submit feedback for an LLM interaction."""
    # Find the interaction
    interaction = session.get(ToolInteraction, request.interaction_id)

    # Verify that the interaction exists and belongs to the user
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    # Not needed as now users can give feedback to each other
    # if interaction.user_id != current_user.id:
    #    raise HTTPException(
    #        status_code=403,
    #        detail="Not authorized to provide feedback on this interaction",
    #    )

    # Update the interaction with the feedback
    interaction.feedback = request.feedback
    interaction.feedback_text = request.feedback_text
    interaction.feedback_date = datetime.now(timezone.utc)

    session.add(interaction)
    session.commit()

    return Message(message="Feedback submitted successfully")
