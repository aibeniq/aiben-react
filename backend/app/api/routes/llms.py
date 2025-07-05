from typing import List

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.services.llms import LlmService, LlmModelInfo
from app.models import Message, User

router = APIRouter(prefix="/llm-models", tags=["llm-models"])


@router.get("/", response_model=List[LlmModelInfo])
def get_llm_models() -> List[LlmModelInfo]:
    """Get all LLMs."""
    return LlmService.get_models()


@router.get("/providers", response_model=List[str])
def get_available_providers() -> List[str]:
    """Get all available LLM providers."""
    return LlmService.get_providers()


@router.get("/default", response_model=LlmModelInfo)
def get_default_llm_model(
    session: SessionDep, current_user: CurrentUser
) -> LlmModelInfo:
    """Get the user's default LLM model (database record)."""
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.default_llm:
        raise HTTPException(
            status_code=404, detail=f"No default LLM found for user {user.id}"
        )
    model_spec = LlmService.get_model_spec(user.default_llm)
    if not model_spec:
        raise HTTPException(
            status_code=404,
            detail=f"User's default LLM model {user.default_llm} not found",
        )
    return model_spec


@router.post("/validate", response_model=Message)
def validate_llm_model(
    model_id: str,
) -> Message:
    """Validate if an LLM ID is valid for the specified provider."""
    is_valid, error_message = LlmService.validate_model(model_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    return Message(message="Model is valid")


@router.post("/check-api-key", response_model=Message)
def check_api_key_configured(provider: str) -> Message:
    """Check if API key is configured for the specified provider."""
    provider_models = LlmService.get_models_by_provider(provider)
    if not provider_models:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

    # Check with the first model of this provider
    test_model_id = provider_models[0].id
    is_valid, error_message = LlmService.validate_model(test_model_id)

    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    return Message(message="API key is configured")


@router.post("/{model_id}/set-default", response_model=LlmModelInfo)
def set_default_llm_model(
    model_id: str, session: SessionDep, current_user: CurrentUser
) -> LlmModelInfo:
    """
    Set an LLM as the default.
    """
    is_valid, error_message = LlmService.validate_model(model_id)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    model_spec = LlmService.get_model_spec(model_id)
    if not model_spec:
        raise HTTPException(
            status_code=404, detail=f"Model {model_id} not found in registry"
        )
    user.default_llm = model_spec.id
    session.add(user)
    session.commit()
    session.refresh(user)
    return model_spec
