import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import select, func

from app.api.deps import CurrentUser, SessionDep
from app.services.llms import create_llm
from app.models import (
    LlmModel, 
    LlmModelCreate, 
    LlmModelUpdate,
    LlmModelPublic,
    LlmModelsPublic,
    LlmModelsValidate,
    ModelProvider,
    Message
)
from datetime import datetime


from langchain_community.chat_models import ChatOllama
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from langchain_openai import ChatOpenAI

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
    
    print(f"Loading default LLM model: {model.name} ({model.model_id}, provider: {model.provider})")
    
    return model

@router.post("/", response_model=LlmModelPublic)
def create_llm_model(
    model_in: LlmModelCreate, session: SessionDep, current_user: CurrentUser
) -> LlmModelPublic:
    """
    Create a new LLM model.
    """
    # Optionally, validate model_id/provider here (e.g., try to instantiate the model)
    # For now, just create the model
    model = LlmModel(
        **model_in.model_dump(),
        owner_id=current_user.id,
        date_created=datetime.utcnow(),
        date_modified=datetime.utcnow()
    )
    session.add(model)
    session.commit()
    session.refresh(model)
    return model

@router.delete("/{model_id}", response_model=Message)
def delete_llm_model(
    model_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Message:
    """
    Delete an LLM model.
    """
    model = session.get(LlmModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="LLM model not found")
    if model.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this model")
    session.delete(model)
    session.commit()
    return Message(message="LLM model deleted successfully")

@router.post("/validate", response_model=Message)
def validate_llm_model(
    session: SessionDep,
    model_data: LlmModelsValidate,
) -> Message:
    """
    Validate if an LLM model ID is valid for the specified provider.
    """
    try:
        # Extract the provider and model_id
        provider = model_data.provider
        model_id = model_data.model_id
        
        print(f"Validating LLM model: {model_id} (provider: {provider})")
        
        if provider == ModelProvider.OPENAI:
            # For OpenAI, attempt to create the model with a simple test
            
            # Get API key from environment or request
            #api_key = None  # You can add API key passing if needed
            
            llm = ChatOpenAI(
                model=model_id,
                temperature=0.0,
                #openai_api_key=api_key,
                max_tokens=5  # Minimum tokens for test
            )
            
            # Test with a simple query to verify the model exists
            response = llm.invoke("Hello")
            print(f"OpenAI model validation successful: {model_id}")
            
        elif provider == ModelProvider.HUGGINGFACE:
            # For HuggingFace, try to load the model
            from langchain_huggingface import HuggingFacePipeline
            
            print(f"Loading HuggingFace model: {model_id}")
            
            # Just check if the model exists - don't fully load it to save resources
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            print(f"HuggingFace tokenizer loaded successfully for {model_id}")
            
            # Optional: Check model card to verify it's a language model
            # from huggingface_hub import model_info
            # info = model_info(model_id)
            # if "text-generation" not in info.pipeline_tag and "text2text-generation" not in info.pipeline_tag:
            #     raise ValueError(f"Model {model_id} is not a language model")
            
        elif provider == ModelProvider.OLLAMA:
            # For Ollama, check if the model is available
            
            # Try to connect to Ollama server and verify model
            llm = ChatOllama(
                model=model_id,
                temperature=0.0,
                # Use default Ollama URL, or configure as needed
                base_url="http://localhost:11434"
            )
            
            # Simple test to verify the model is available
            response = llm.invoke("Hello")
            print(f"Ollama model validation successful: {model_id}")
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return Message(message=f"LLM model {model_id} is valid for provider {provider}")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"LLM validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid LLM model: {str(e)}"
        )
    
@router.post("/{model_id}/set-default", response_model=LlmModelPublic)
def set_default_llm_model(
    model_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> LlmModelPublic:
    """
    Set an LLM model as the default.
    """
    model = session.get(LlmModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="LLM model not found")
    
    # Check if the model is system-owned or owned by the current user
    if model.owner_id is not None and model.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, 
            detail="Not authorized to modify this model"
        )
    
    # Get all models (both system and user models)
    all_models = session.exec(
        select(LlmModel)
        .where((LlmModel.owner_id.is_(None)) | 
               (LlmModel.owner_id == current_user.id))
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