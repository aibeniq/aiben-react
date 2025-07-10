from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.services.embeddings import EmbeddingModelInfo, EmbeddingService
from app.services.llms import LlmModelSpec, LlmService

router = APIRouter(prefix="/models", tags=["models"])


# === Embedding Model Registry Endpoints ===


@router.get("/embedding-providers", response_model=list[str])
def get_embedding_providers() -> list[str]:
    """
    Get list of available embedding providers.
    """
    return EmbeddingService.get_providers()


@router.get("/embedding-models", response_model=list[EmbeddingModelInfo])
def get_embedding_models_registry() -> list[EmbeddingModelInfo]:
    """
    Get the registry of available embedding models.
    """
    return EmbeddingService.get_models()


@router.get("/embedding-default", response_model=EmbeddingModelInfo)
def get_default_embedding_model() -> EmbeddingModelInfo:
    """
    Get the default embedding model.
    """
    return EmbeddingService.get_default_model()


# === LLM Model Endpoints ===
# TODO: this doesn't belong here.. or we need to modify the prefix


@router.get("/llm-providers", response_model=list[str])
def get_llm_providers() -> list[str]:
    """Get list of available LLM providers."""
    return LlmService.get_providers()


@router.get("/llm-models", response_model=list[LlmModelSpec])
def get_llm_models() -> list[LlmModelSpec]:
    """Get all LLM models."""
    return LlmService.get_model_specs()


@router.get("/llm-default", response_model=LlmModelSpec)
def get_default_llm_model(
    session: SessionDep,
    current_user: CurrentUser,
) -> LlmModelSpec:
    """Get the default LLM model."""
    return LlmService.get_user_default_model_spec(session, current_user.id)


@router.post("/llm-default", response_model=LlmModelSpec)
def set_default_llm_model(
    model_id: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> LlmModelSpec:
    """Set the default LLM model."""
    return LlmService.set_user_default_model_spec(session, current_user.id, model_id)
