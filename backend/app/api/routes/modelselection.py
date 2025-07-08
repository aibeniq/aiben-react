from fastapi import APIRouter

from app.services.embeddings import EmbeddingModelInfo, EmbeddingService
from app.services.llms import LlmModelSpec, LlmService

router = APIRouter(prefix="/embedding-models", tags=["embedding-models"])


# === Embedding Model Registry Endpoints ===


@router.get("/providers", response_model=list[str])
def get_available_providers() -> list[str]:
    """
    Get list of available embedding providers.
    """
    return EmbeddingService.get_providers()


@router.get("/registry", response_model=list[EmbeddingModelInfo])
def get_embedding_models_registry() -> list[EmbeddingModelInfo]:
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


@router.get("/llm", response_model=list[LlmModelSpec])
def get_llm_models() -> list[LlmModelSpec]:
    """Get all LLM models."""
    return LlmService.get_model_specs()
