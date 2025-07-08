from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.models import Message, User
from app.services.llms import LlmModelSpec, LlmService

router = APIRouter(prefix="/llm-models", tags=["llm-models"])


@router.get("/", response_model=list[LlmModelSpec])
def get_llm_models() -> list[LlmModelSpec]:
    """Get all LLMs."""
    return LlmService.get_model_specs()


@router.get("/providers", response_model=list[str])
def get_available_providers() -> list[str]:
    """Get all available LLM providers."""
    return LlmService.get_providers()


@router.get("/default", response_model=LlmModelSpec)
def get_default_llm_model(
    session: SessionDep, current_user: CurrentUser
) -> LlmModelSpec:
    """Get the user's default LLM model (database record)."""
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.default_llm:
        raise HTTPException(
            status_code=404, detail=f"No default LLM found for user {user.id}"
        )
    try:
        return LlmService.get_model_spec(user.default_llm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=Message)
def validate_llm_model(
    model_id: str,
) -> Message:
    """Validate if an LLM ID is valid for the specified provider."""
    try:
        LlmService.get_model_spec(model_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Message(message="Model is valid")


@router.post("/check-api-key", response_model=Message)
def check_api_key_configured(provider: str) -> Message:
    """Check if API key is configured for the specified provider."""
    try:
        models = LlmService.get_model_specs_by_provider(provider)
        if not models:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")
        test_model_id = models[0].id
        LlmService.get_model_spec(test_model_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Message(message="API key is configured")


@router.post("/{model_id}/set-default", response_model=LlmModelSpec)
def set_default_llm_model(
    model_id: str, session: SessionDep, current_user: CurrentUser
) -> LlmModelSpec:
    """
    Set an LLM as the default.
    """
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        spec = LlmService.get_model_spec(model_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    user.default_llm = spec.id
    session.add(user)
    session.commit()
    session.refresh(user)
    return spec
