from typing import List
from fastapi import APIRouter
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    LlmModel,
    LlmModelsPublic,
)
from app.services.embeddings import EmbeddingService, EmbeddingModelInfo

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


@router.get("/llm/", response_model=LlmModelsPublic)
def get_llm_models(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> LlmModelsPublic:
    """
    Get all LLM models.
    """
    # First get system models (no owner_id)
    system_models = session.exec(
        select(LlmModel).where(LlmModel.owner_id.is_(None))
    ).all()

    # Then get user's custom models
    user_models = session.exec(
        select(LlmModel).where(LlmModel.owner_id == current_user.id)
    ).all()

    # Combine the results
    models = system_models + user_models
    count = len(models)

    # Apply pagination
    models = models[skip : skip + limit]

    return LlmModelsPublic(data=models, count=count)
