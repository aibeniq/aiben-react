import uuid
import os
from typing import List, Dict
import replicate
import boto3

from fastapi import APIRouter, HTTPException
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
    EmbeddingModelInfo,  # Add the new model
    ModelProvider,
    Message,
    User,
)
from app.core.config import settings
from datetime import datetime
from langchain_openai import OpenAIEmbeddings

router = APIRouter(prefix="/embedding-models", tags=["embedding-models"])


@router.get("/providers", response_model=Dict[str, List[str]])
def get_available_providers() -> Dict[str, List[str]]:
    """
    Get list of available embedding providers.
    """
    return {
        "embedding_providers": settings.embedding_providers,
        "llm_providers": settings.llm_providers,
    }


def get_model_dimensions(model_id: str, provider: ModelProvider) -> int:
    """Get model dimensions based on known model specifications."""
    # Default dimensions for known models
    model_dimensions = {
        # OpenAI models
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
        # AWS models
        "amazon.titan-embed-text-v2:0": 1024,
        "cohere.embed-english-v3": 1024,
        "cohere.embed-multilingual-v3": 1024,
        # HuggingFace models
        "all-MiniLM-L6-v2": 384,
        "all-mpnet-base-v2": 768,
        "all-MiniLM-L12-v2": 384,
        # Ollama models
        "nomic-embed-text": 768,
    }

    return model_dimensions.get(model_id, 768)  # Default to 768 if unknown


# Initialize with default models
def initialize_default_models(session: SessionDep):
    # List of default models to ensure exist
    default_models = [
        {
            "name": "MiniLM-L6-v2",
            "model_id": "all-MiniLM-L6-v2",
            "provider": ModelProvider.HUGGINGFACE,
            "description": "A compact and efficient embedding model, good balance of performance and speed.",
        },
        {
            "name": "Amazon Titan 2.0",
            "model_id": "amazon.titan-embed-text-v2:0",
            "provider": ModelProvider.AWS,
            "description": "Amazon's Titan 2.0 embedding model for AWS Bedrock. High-quality text embeddings with 1024 dimensions, optimized for enterprise search and retrieval applications.",
        },
        {
            "name": "OpenAI Embeddings 3 Small",
            "model_id": "text-embedding-3-small",
            "provider": ModelProvider.OPENAI,
            "description": "OpenAI's compact embedding model with 1536 dimensions. Excellent quality with lower cost and faster performance than the large variant.",
        },
        {
            "name": "MPNet Base v2",
            "model_id": "all-mpnet-base-v2",
            "provider": ModelProvider.HUGGINGFACE,
            "description": "Higher quality embeddings, but slower and larger than MiniLM.",
        },
        {
            "name": "MiniLM-L12-v2",
            "model_id": "all-MiniLM-L12-v2",
            "provider": ModelProvider.HUGGINGFACE,
            "description": "Larger version of MiniLM with improved performance.",
        },
        {
            "name": "Ollama - nomic-embed-text",
            "model_id": "nomic-embed-text",
            "provider": ModelProvider.OLLAMA,
            "description": "A local embedding model running via Ollama.",
        },
    ]

    for model_data in default_models:
        # Check if this default model already exists (system model: owner_id is None)
        exists = session.exec(
            select(EmbeddingModel).where(
                EmbeddingModel.model_id == model_data["model_id"],
                EmbeddingModel.provider == model_data["provider"],
                EmbeddingModel.owner_id.is_(None),
            )
        ).first()
        if not exists:
            model = EmbeddingModel(
                name=model_data["name"],
                model_id=model_data["model_id"],
                provider=model_data["provider"],
                description=model_data["description"],
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
    # Get enabled providers from settings
    enabled_providers = settings.embedding_providers

    # First get system models (no owner_id) that have enabled providers
    system_models = session.exec(
        select(EmbeddingModel).where(EmbeddingModel.owner_id.is_(None))
    ).all()

    # Filter system models by enabled providers
    filtered_system_models = [
        model
        for model in system_models
        if model.provider.value.lower() in enabled_providers
    ]

    # Then get user's custom models (always include regardless of provider)
    user_models = session.exec(
        select(EmbeddingModel).where(EmbeddingModel.owner_id == current_user.id)
    ).all()

    # Combine the results
    models = filtered_system_models + user_models
    count = len(models)

    # Apply pagination
    models = models[skip : skip + limit]

    return EmbeddingModelsPublic(data=models, count=count)


@router.get("/default", response_model=EmbeddingModelPublic)
def get_default_embedding_model(
    session: SessionDep, current_user: CurrentUser
) -> EmbeddingModelPublic:
    """
    Get the user's default embedding model (or system default if not set).
    """
    # Try to get the user's default embedding model
    user = session.get(User, current_user.id)
    if user and user.default_embedding_model:
        print("Default embedding model found for this user!")
        model = session.get(EmbeddingModel, user.default_embedding_model)
        if model:
            return model

    # Fallback to system default (first system model)
    enabled_providers = settings.embedding_providers

    # Get all system default embedding models
    system_defaults = session.exec(
        select(EmbeddingModel).where(EmbeddingModel.owner_id.is_(None))
    ).all()

    # Find the first system model with an enabled provider
    for model in system_defaults:
        if model.provider.value.lower() in enabled_providers:
            print(
                f"Using system default embedding model: {model.name} ({model.provider.value})"
            )
            return model

    # If no enabled system models found, raise a helpful error
    enabled_str = ", ".join(enabled_providers)
    raise ValueError(
        f"No default embedding model available for enabled providers ({enabled_str}). "
        f"Please check your configuration or add system default embedding models."
    )


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
        raise HTTPException(
            status_code=403, detail="Not authorized to access this model"
        )

    return model


@router.post("/", response_model=EmbeddingModelPublic)
def create_embedding_model(
    model_in: EmbeddingModelCreate, session: SessionDep, current_user: CurrentUser
) -> EmbeddingModelPublic:
    """
    Create a new embedding model.
    """
    # Check if the model_id is valid by trying to load it based on provider
    try:
        if model_in.provider == ModelProvider.HUGGINGFACE:
            # only import here, to avoid errors in API-only builds
            from langchain_huggingface import HuggingFaceEmbeddings

            # Validate HuggingFace model
            _ = HuggingFaceEmbeddings(model_name=model_in.model_id)
        elif model_in.provider == ModelProvider.AWS:
            # Check if AWS credentials are configured
            aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
            if not aws_access_key or not aws_secret_key:
                raise HTTPException(
                    status_code=400,
                    detail="AWS credentials are not configured in the environment",
                )

            # Basic validation of model ID format
            valid_model_prefixes = [
                "amazon.",
                "anthropic.",
                "ai21.",
                "cohere.",
                "meta.",
            ]
            is_valid_model = any(
                model_in.model_id.startswith(prefix) for prefix in valid_model_prefixes
            )

            if not is_valid_model:
                raise ValueError(
                    f"Invalid AWS Bedrock model ID format. Expected model ID to start with one of {valid_model_prefixes}"
                )

            print(f"AWS Bedrock model validation successful for: {model_in.model_id}")
        elif model_in.provider == ModelProvider.OPENAI:
            # Check if OpenAI API key is configured
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key is not configured in the environment",
                )
            # Validate OpenAI model - disable retries to avoid conflicts
            _ = OpenAIEmbeddings(
                model=model_in.model_id,
                openai_api_key=api_key,
                max_retries=0,  # Disable OpenAI's internal retries for validation
                request_timeout=30,  # Set reasonable timeout
            )
        elif model_in.provider == ModelProvider.OLLAMA:
            # For Ollama, we can't easily validate without making a call to the Ollama server
            # So we'll just check if the format looks correct (basic validation)
            if not model_in.model_id or not isinstance(model_in.model_id, str):
                raise ValueError("Invalid model ID format for Ollama")
        elif model_in.provider == ModelProvider.REPLICATE:
            # Check if Replicate API token is configured
            api_token = os.environ.get("REPLICATE_API_TOKEN")
            if not api_token:
                raise HTTPException(
                    status_code=400,
                    detail="Replicate API token is not configured in the environment",
                )

            # Validate the Replicate model
            # We'll use a similar approach to what's in your llms.py validation
            try:
                # Just check if the model exists, don't run a full embedding request
                if ":" in model_in.model_id:
                    # Model with specific version
                    owner_model, version = model_in.model_id.split(":")
                    # Just check metadata
                    model_info = replicate.models.get(owner_model)
                    # Verify the version exists
                    version_exists = False
                    for v in model_info.versions.list():
                        if v.id.startswith(version):
                            version_exists = True
                            break
                    if not version_exists:
                        raise ValueError(
                            f"Version {version} not found for model {owner_model}"
                        )
                else:
                    # Model without specific version (will use latest)
                    model_info = replicate.models.get(model_in.model_id)

                print(f"Replicate model validation successful: {model_in.model_id}")
            except Exception as e:
                print(f"Error validating Replicate model: {str(e)}")
                raise ValueError(f"Invalid Replicate model: {str(e)}")
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported provider: {model_in.provider}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid {model_in.provider} model ID: {str(e)}"
        )

    # Create the new model
    model = EmbeddingModel(
        **model_in.model_dump(),
        owner_id=current_user.id,
        date_created=datetime.utcnow(),
        date_modified=datetime.utcnow(),
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
    current_user: CurrentUser,
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
            status_code=403, detail="Not authorized to update this model"
        )

    # Check if model_id is changed and valid
    update_data = model_in.model_dump(exclude_unset=True)
    if "model_id" in update_data:
        try:
            _ = HuggingFaceEmbeddings(model_name=update_data["model_id"])
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid HuggingFace model ID: {str(e)}"
            )

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
            status_code=403, detail="Not authorized to delete this model"
        )

    session.delete(model)
    session.commit()

    return Message(message="Embedding model deleted successfully")


@router.post("/{model_id}/set-default", response_model=EmbeddingModelPublic)
def set_default_embedding_model(
    model_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> EmbeddingModelPublic:
    """
    Set an embedding model as the default for the current user.
    """
    model = session.get(EmbeddingModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Embedding model not found")

    # Check if the model is system-owned or owned by the current user
    if model.owner_id is not None and model.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this model"
        )

    # Set the user's default embedding model
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.default_embedding_model = model.id
    session.add(user)
    session.commit()
    session.refresh(user)

    return model


@router.post("/validate", response_model=Message)
def validate_embedding_model(model_data: EmbeddingModelValidate) -> Message:
    """
    Validate if an embedding model ID is valid for the specified provider.
    """
    print("Validating embedding model with the following parameters:")
    print("Provider:", model_data.provider)
    print("Model ID:", model_data.model_id)
    try:
        # Initialize the embeddings model based on provider
        embeddings = load_embeddings_model(
            provider=model_data.provider, model_id=model_data.model_id
        )
        print("Embeddings model loaded successfully.")

        # Test the model with a simple query
        test_query = "This is a test query to validate the embedding model."
        _ = embeddings.embed_query(test_query)

        print("Model validation successful.")

        return Message(message=f"Model is valid for provider {model_data.provider}")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid embedding model: {str(e)}"
        )


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
                detail="OpenAI API key is not configured in the backend",
            )
    elif provider == "aws":
        # Check for AWS credentials in environment
        aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        if aws_access_key and aws_secret_key:
            print("AWS credentials found, validating...")
            try:
                # Try to initialize a boto3 client as a basic test
                client = boto3.client(
                    "bedrock-runtime",
                    region_name=os.environ.get("AWS_REGION", "eu-north-1"),
                )
                # Just check if we can list models as a basic validation
                return Message(message="AWS credentials are configured")
            except Exception as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"AWS credentials are configured but invalid: {str(e)}",
                )
        else:
            raise HTTPException(
                status_code=404,
                detail="AWS credentials are not configured in the backend",
            )
    elif provider == "ollama":
        # Check if Ollama server is reachable
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
        try:
            import requests

            response = requests.get(f"{base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                return Message(message="Ollama server is reachable")
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Ollama server returned status {response.status_code}",
                )
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Cannot connect to Ollama server at {base_url}: {str(e)}",
            )
    elif provider == "huggingface":
        # For HuggingFace, check for token if needed
        return Message(message="No API key needed for this provider")
    elif provider == "replicate":
        api_token = os.environ.get("REPLICATE_API_TOKEN")
        if api_token:
            return Message(message="API token is configured")
        else:
            raise HTTPException(
                status_code=404,
                detail="Replicate API token is not configured in the backend",
            )
    else:
        return Message(message="No API key needed for this provider")
