import uuid
from datetime import datetime, timezone


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.models import ToolInteraction, Message, ToolFeedback

router = APIRouter(prefix="/toolfeedback", tags=["toolfeedback"])


class ToolFeedbackRequest(BaseModel):
    interaction_id: uuid.UUID
    feedback: ToolFeedback
    feedback_text: str | None = None


@router.post("/", response_model=Message)
async def submit_tool_feedback(
    session: SessionDep, request: ToolFeedbackRequest = Depends()
) -> Message:
    """Submit feedback for a tool interaction."""
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
    interaction.feedback = ToolFeedback(request.feedback)
    interaction.feedback_text = request.feedback_text
    interaction.feedback_date = datetime.now(timezone.utc)

    session.add(interaction)
    session.commit()

    return Message(message="Tool feedback submitted successfully")
