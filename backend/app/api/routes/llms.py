import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select, func

from app.api.deps import CurrentUser, SessionDep
from app.services.llms import create_llm
from app.models import (
    LlmModel, 
    LlmModelCreate, 
    LlmModelUpdate,
    LlmModelPublic,
    LlmModelsPublic,
    ModelProvider,
    Message
)
from datetime import datetime

router = APIRouter(prefix="/llm-models", tags=["llm-models"])

# Initialize with default models
def initialize_default_llm_models(session: SessionDep):
    # Check if we already have models in the database
    existing_count = session.exec(select(func.count()).select_from(LlmModel)).one()
    if existing_count > 0:
        return
    
    # Add default models
    default_models = [
        {
            "name": "GPT-4o Mini",
            "model_id": "gpt-4o-mini",
            "provider": ModelProvider.OPENAI,
            "description": "OpenAI's GPT-4o Mini model, good balance of performance and speed.",
            "is_default": True
        },
        {
            "name": "Llama 3 8B",
            "model_id": "llama3",
            "provider": ModelProvider.OLLAMA,
            "description": "Local Llama 3 8B model running via Ollama.",
            "is_default": False
        },
        {
            "name": "Mistral 7B",
            "model_id": "mistral",
            "provider": ModelProvider.OLLAMA,
            "description": "Local Mistral 7B model running via Ollama.",
            "is_default": False
        }
    ]
    
    for model_data in default_models:
        model = LlmModel(
            name=model_data["name"],
            model_id=model_data["model_id"],
            provider=model_data["provider"],
            description=model_data["description"],
            is_default=model_data["is_default"]
        )
        session.add(model)
    
    session.commit()

@router.get("/", response_model=LlmModelsPublic)
def get_llm_models(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> LlmModelsPublic:
    """
    Get all LLM models.
    """
    # Initialize default models if none exist
    initialize_default_llm_models(session)
    
    # Get models (both system and user-specific)
    models = session.exec(
        select(LlmModel)
        .where((LlmModel.owner_id.is_(None)) | 
               (LlmModel.owner_id == current_user.id))
        .offset(skip)
        .limit(limit)
    ).all()
    
    return LlmModelsPublic(data=models)

@router.get("/default", response_model=LlmModelPublic)
def get_default_llm_model(session: SessionDep) -> LlmModelPublic:
    """
    Get the default LLM model.
    """
    # Initialize default models if none exist
    initialize_default_llm_models(session)
    
    model = session.exec(
        select(LlmModel)
        .where(LlmModel.is_default == True)
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="No default LLM model found")
    
    return model

# Add additional endpoints similar to your embedding models for create, update, delete, etc.