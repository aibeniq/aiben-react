from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.core.config import settings
from app.models import Message
from app.utils.email_utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
    response_model=Message,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/", response_model=bool)
async def health_check() -> bool:
    return True


@router.get("/system-config")
def get_system_config() -> Dict[str, Any]:
    """
    Get system configuration for frontend.
    """
    return {
        "enable_model_selection": settings.ENABLE_MODEL_SELECTION,
        "force_default_llm": (
            settings.FORCE_DEFAULT_LLM if not settings.ENABLE_MODEL_SELECTION else None
        ),
        "force_default_embedding": (
            settings.FORCE_DEFAULT_EMBEDDING
            if not settings.ENABLE_MODEL_SELECTION
            else None
        ),
    }
