from typing import List
from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.services.embeddings import EmbeddingService, EmbeddingModelInfo
from app.services.llms import LlmModelInfo, LlmService

router = APIRouter(prefix="/embedding-models", tags=["embedding-models"])


# === Embedding Model Registry Endpoints ===


@router.get("/providers", response_model=List[str])
def get_available_providers() -> List[str]:
    """
    Get list of available embedding providers.
    """
    return EmbeddingService.get_providers()


@router.get("/registry", response_model=List[EmbeddingModelInfo])
def get_embedding_models_registry() -> List[EmbeddingModelInfo]:
    """
    Get the registry of available embedding models.
    """
    return EmbeddingService.get_models()


@router.get("/default", response_model=EmbeddingModelInfo)
def get_default_embedding_model() -> EmbeddingModelInfo:
    """
    Get the default embedding model.
    """
    return EmbeddingService.get_default_model()


# === LLM Model Endpoints ===
# TODO: this doesn't belong here.. or we need to modify the prefix


@router.get("/llm", response_model=List[LlmModelInfo])
def get_llm_models(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> List[LlmModelInfo]:
    """Get all LLM models."""
    return LlmService.get_models()
