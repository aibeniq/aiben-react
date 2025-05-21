import uuid
import os
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import select, func

from app.api.deps import CurrentUser, SessionDep
from app.services.embeddings import load_embeddings_model
from app.models import (
    EmbeddingModel, 
    EmbeddingModelCreate, 
    EmbeddingModelUpdate,
    EmbeddingModelPublic,
    EmbeddingModelsPublic,
    EmbeddingModelValidate,
    ModelProvider,
    Message
)
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

router = APIRouter(prefix="/embedding-models", tags=["embedding-models"])

# Initialize with default models
def initialize_default_models(session: SessionDep):
    # Check if we already have models in the database
    existing_count = session.exec(select(func.count()).select_from(EmbeddingModel)).one()
    if existing_count > 0:
        return
    
    # Add default models
    default_models = [
        {
            "name": "MiniLM-L6-v2",
            "model_id": "all-MiniLM-L6-v2",
            "provider": ModelProvider.HUGGINGFACE,  # Specify provider explicitly
            "description": "A compact and efficient embedding model, good balance of performance and speed.",
            "is_default": True
        },
        {
            "name": "MPNet Base v2", 
            "model_id": "all-mpnet-base-v2",
            "provider": ModelProvider.HUGGINGFACE,  # Specify provider explicitly
            "description": "Higher quality embeddings, but slower and larger than MiniLM.",
            "is_default": False
        },
        {
            "name": "MiniLM-L12-v2",
            "model_id": "all-MiniLM-L12-v2", 
            "provider": ModelProvider.HUGGINGFACE,  # Specify provider explicitly
            "description": "Larger version of MiniLM with improved performance.",
            "is_default": False
        },
        {
            "name": "Ollama - nomic-embed-text",
            "model_id": "nomic-embed-text",
            "provider": ModelProvider.OLLAMA,
            "description": "A local embedding model running via Ollama.",
            "is_default": False
        }
    ]
    
    for model_data in default_models:
        model = EmbeddingModel(
            name=model_data["name"],
            model_id=model_data["model_id"],
            provider=model_data["provider"],
            description=model_data["description"],
            is_default=model_data["is_default"]
        )
        session.add(model)
    
    session.commit()

@router.get("/", response_model=EmbeddingModelsPublic)
def get_embedding_models(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> EmbeddingModelsPublic:
    """
    Get all embedding models.
    """
    # Initialize default models if none exist
    initialize_default_models(session)
    
    # First get system models (no owner_id)
    system_models = session.exec(
        select(EmbeddingModel)
        .where(EmbeddingModel.owner_id.is_(None))
    ).all()
    
    # Then get user's custom models
    user_models = session.exec(
        select(EmbeddingModel)
        .where(EmbeddingModel.owner_id == current_user.id)
    ).all()
    
    # Combine the results
    models = system_models + user_models
    count = len(models)
    
    # Apply pagination
    models = models[skip:skip + limit]
    
    return EmbeddingModelsPublic(data=models, count=count)

@router.get("/{model_id}", response_model=EmbeddingModelPublic)
def get_embedding_model(
    model_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> EmbeddingModelPublic:
    """
    Get a specific embedding model by ID.
    """
    model = session.get(EmbeddingModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Embedding model not found")
    
    # Check if the model is system-owned or owned by the current user
    if model.owner_id is not None and model.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this model")
    
    return model

@router.get("/default", response_model=EmbeddingModelPublic)
def get_default_embedding_model(session: SessionDep) -> EmbeddingModelPublic:
    """
    Get the default embedding model.
    """
    # Initialize default models if none exist
    initialize_default_models(session)
    
    model = session.exec(
        select(EmbeddingModel)
        .where(EmbeddingModel.is_default == True)
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="No default embedding model found")
    
    return model

@router.post("/", response_model=EmbeddingModelPublic)
def create_embedding_model(
    model_in: EmbeddingModelCreate, session: SessionDep, current_user: CurrentUser
) -> EmbeddingModelPublic:
    """
    Create a new embedding model.
    """
    # Check if the model_id is valid by trying to load it
    try:
        _ = HuggingFaceEmbeddings(model_name=model_in.model_id)
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid HuggingFace model ID: {str(e)}"
        )
    
    # If this is set as default, unset any previous default models owned by the user
    if model_in.is_default:
        previous_defaults = session.exec(
            select(EmbeddingModel)
            .where(
                EmbeddingModel.is_default == True,
                EmbeddingModel.owner_id == current_user.id
            )
        ).all()
        
        for model in previous_defaults:
            model.is_default = False
            session.add(model)
    
    # Create the new model
    model = EmbeddingModel(
        **model_in.model_dump(),
        owner_id=current_user.id,
        date_created=datetime.utcnow(),
        date_modified=datetime.utcnow()
    )
    
    session.add(model)
    session.commit()
    session.refresh(model)
    
    return model

@router.put("/{model_id}", response_model=EmbeddingModelPublic)
def update_embedding_model(
    model_id: uuid.UUID,
    model_in: EmbeddingModelUpdate,
    session: SessionDep,
    current_user: CurrentUser
) -> EmbeddingModelPublic:
    """
    Update an embedding model.
    """
    model = session.get(EmbeddingModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Embedding model not found")
    
    # Check if user owns this model
    if model.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to update this model"
        )
    
    # Check if model_id is changed and valid
    update_data = model_in.model_dump(exclude_unset=True)
    if "model_id" in update_data:
        try:
            _ = HuggingFaceEmbeddings(model_name=update_data["model_id"])
        except Exception as e:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid HuggingFace model ID: {str(e)}"
            )
    
    # If setting as default, unset previous defaults
    if update_data.get("is_default", False):
        previous_defaults = session.exec(
            select(EmbeddingModel)
            .where(
                EmbeddingModel.is_default == True,
                EmbeddingModel.owner_id == current_user.id,
                EmbeddingModel.id != model_id
            )
        ).all()
        
        for prev_model in previous_defaults:
            prev_model.is_default = False
            session.add(prev_model)
    
    # Update the model
    for key, value in update_data.items():
        setattr(model, key, value)
    
    model.date_modified = datetime.utcnow()
    
    session.add(model)
    session.commit()
    session.refresh(model)
    
    return model

@router.delete("/{model_id}", response_model=Message)
def delete_embedding_model(
    model_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Message:
    """
    Delete an embedding model.
    """
    model = session.get(EmbeddingModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Embedding model not found")
    
    # Only allow deletion of user-owned models
    if model.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to delete this model"
        )
    
    session.delete(model)
    session.commit()
    
    return Message(message="Embedding model deleted successfully")

@router.post("/{model_id}/set-default", response_model=EmbeddingModelPublic)
def set_default_embedding_model(
    model_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> EmbeddingModelPublic:
    """
    Set an embedding model as the default.
    """
    model = session.get(EmbeddingModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Embedding model not found")
    
    # Check if the model is system-owned or owned by the current user
    if model.owner_id is not None and model.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to modify this model"
        )
    
    # Get all models (both system and user models)
    all_models = session.exec(
        select(EmbeddingModel)
        .where((EmbeddingModel.owner_id.is_(None)) | 
               (EmbeddingModel.owner_id == current_user.id))
    ).all()
    
    # Unset all as default
    for m in all_models:
        if m.is_default:
            m.is_default = False
            m.date_modified = datetime.utcnow()
            session.add(m)
    
    # Set the selected model as default
    model.is_default = True
    model.date_modified = datetime.utcnow()
    session.add(model)
    
    session.commit()
    session.refresh(model)
    
    return model

@router.post("/validate", response_model=Message)
def validate_embedding_model(
    model_data: EmbeddingModelValidate
) -> Message:
    """
    Validate if an embedding model ID is valid for the specified provider.
    """
    print("Validating embedding model with the following parameters:")
    print("Provider:", model_data.provider)
    print("Model ID:", model_data.model_id)	
    try:
        # Initialize the embeddings model based on provider
        embeddings = load_embeddings_model(
            provider=model_data.provider,
            model_id=model_data.model_id
        )
        
        # Test the model with a simple query
        test_query = "This is a test query to validate the embedding model."
        _ = embeddings.embed_query(test_query)
        
        return Message(message=f"Model is valid for provider {model_data.provider}")
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid embedding model: {str(e)}"
        )
    
# Add this new endpoint to your modelselection.py router
@router.get("/check-api-key/{provider}", response_model=Message)
def check_api_key_configured(provider: str) -> Message:
    """
    Check if the API key for a specific provider is configured in the backend.
    """
    print("Checking API key configuration for provider:", provider)
    if provider == "openai":
        # Check for OpenAI API key in environment
        print("Checking OpenAI API key configuration...")
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            return Message(message="API key is configured")
        else:
            raise HTTPException(
                status_code=404,
                detail="OpenAI API key is not configured in the backend"
            )
    elif provider == "huggingface":
        # For HuggingFace, check for token if needed
        return Message(message="No API key needed for this provider")
    else:
        return Message(message="No API key needed for this provider")