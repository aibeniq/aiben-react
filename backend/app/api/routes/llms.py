import os
import replicate
import uuid
import threading
import requests
from typing import Any, List, Optional
import boto3
import traceback

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlmodel import select, func

from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.core.ml_imports import (
    get_transformers,
    get_huggingface_pipeline,
    get_transformers_pipeline,
    get_transformers_model_classes,
    check_ml_capabilities,
)
from app.services.llms import create_llm
from app.models import (
    LlmModel,
    LlmModelCreate,
    LlmModelUpdate,
    LlmModelPublic,
    LlmModelsPublic,
    LlmModelsValidate,
    ModelProvider,
    Message,
    User,
)
from datetime import datetime


from langchain_community.chat_models import ChatOllama, BedrockChat
from langchain.chains import LLMChain
from langchain_community.llms import Bedrock
from langchain_core.prompts import PromptTemplate
from langchain_aws import ChatBedrockConverse
from langchain_openai import ChatOpenAI

router = APIRouter(prefix="/llm-models", tags=["llm-models"])


# Initialize with default models
def initialize_default_llm_models(session: SessionDep):
    default_models = [
        {
            "name": "GPT-4o Mini",
            "model_id": "gpt-4o-mini",
            "provider": ModelProvider.OPENAI,
            "description": "OpenAI's GPT-4o Mini model, good balance of performance and speed.",
        },
        {
            "name": "Claude Sonnet 3.7",
            "model_id": "arn:aws:bedrock:eu-north-1:888577032067:inference-profile/eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            "provider": ModelProvider.AWS,
            "description": "Anthropic's Claude 3.7 Sonnet model on AWS Bedrock. Highly capable, fast, and excellent at complex reasoning tasks. Great for enterprise use cases requiring advanced reasoning and understanding.",
        },
        {
            "name": "Llama 3 8B",
            "model_id": "llama3",
            "provider": ModelProvider.OLLAMA,
            "description": "Local Llama 3 8B model running via Ollama.",
        },
        {
            "name": "Mistral 7B",
            "model_id": "mistral",
            "provider": ModelProvider.OLLAMA,
            "description": "Local Mistral 7B model running via Ollama.",
        },
    ]

    for model_data in default_models:
        # Check if this default LLM model already exists (system model: owner_id is None)
        # Use BOTH model_id AND provider to ensure uniqueness
        exists = session.exec(
            select(LlmModel).where(
                LlmModel.model_id == model_data["model_id"],
                LlmModel.provider == model_data["provider"],
                LlmModel.owner_id.is_(None),
            )
        ).first()
        if not exists:
            print(f"Creating default LLM model: {model_data['name']}")
            model = LlmModel(
                name=model_data["name"],
                model_id=model_data["model_id"],
                provider=model_data["provider"],
                description=model_data["description"],
                owner_id=None,  # System model
            )
            session.add(model)
        else:
            print(f"Default LLM model already exists: {model_data['name']}")

    session.commit()


@router.get("/", response_model=LlmModelsPublic)
def get_llm_models(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> LlmModelsPublic:
    """
    Get all LLMs.
    """
    # Initialize default models if none exist
    initialize_default_llm_models(session)

    # Get models (both system and user-specific)
    models = session.exec(
        select(LlmModel)
        .where((LlmModel.owner_id.is_(None)) | (LlmModel.owner_id == current_user.id))
        .offset(skip)
        .limit(limit)
    ).all()

    return LlmModelsPublic(data=models, count=len(models))


@router.get("/default", response_model=LlmModelPublic)
def get_default_llm_model(
    session: SessionDep, current_user: CurrentUser
) -> LlmModelPublic:
    """
    Get the user's default LLM model (database record).
    """
    # Initialize default models if none exist
    initialize_default_llm_models(session)

    # If model selection is disabled, force the configured default
    if not settings.ENABLE_MODEL_SELECTION:
        model = session.exec(
            select(LlmModel).where(
                LlmModel.model_id == settings.FORCE_DEFAULT_LLM,
                LlmModel.owner_id.is_(None),
            )
        ).first()
        if model:
            return model

    # Try to get the user's default LLM model
    user = session.get(User, current_user.id)
    if user and user.default_llm:
        model = session.get(LlmModel, user.default_llm)
        if model:
            return model

    # Fallback to system default
    enabled_providers = settings.llm_providers

    # Get all system default models
    system_defaults = session.exec(
        select(LlmModel).where(LlmModel.owner_id.is_(None))
    ).all()

    # If model selection disabled, prioritize the forced default
    if not settings.ENABLE_MODEL_SELECTION:
        for model in system_defaults:
            if (
                model.model_id == settings.FORCE_DEFAULT_LLM
                and model.provider.value.lower() in enabled_providers
            ):
                return model

    # Find the first system model with an enabled provider
    for model in system_defaults:
        if model.provider.value.lower() in enabled_providers:
            return model

    if not system_defaults:
        raise HTTPException(status_code=404, detail="No default LLM found")

    # Return first available model if no enabled provider match
    return system_defaults[0]


@router.post("/", response_model=LlmModelPublic)
def create_llm_model(
    model_in: LlmModelCreate, session: SessionDep, current_user: CurrentUser
) -> LlmModelPublic:
    """
    Create a new LLM and trigger model download for supported providers.
    """
    # Create the model record first
    model = LlmModel(
        **model_in.model_dump(),
        owner_id=current_user.id,
        date_created=datetime.utcnow(),
        date_modified=datetime.utcnow(),
    )
    session.add(model)
    session.commit()
    session.refresh(model)

    # Trigger model download for supported providers
    _trigger_model_download(model_in.provider, model_in.model_id)

    return model


def _trigger_model_download(provider: ModelProvider, model_id: str):
    """
    Trigger model download for providers that support it.
    This runs in the background to avoid blocking the API response.
    """
    import threading

    def download_task():
        try:
            if provider == ModelProvider.OLLAMA:
                _download_ollama_model(model_id)
            elif provider == ModelProvider.HUGGINGFACE:
                _download_huggingface_model(model_id)
            # Add other providers as needed
        except Exception as e:
            print(
                f"Error downloading model {model_id} for provider {provider}: {str(e)}"
            )

    # Start download in background thread
    thread = threading.Thread(target=download_task)
    thread.daemon = True
    thread.start()


def _download_ollama_model(model_id: str):
    """Download an Ollama model."""
    import requests

    base_url = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
    print(f"Triggering download for Ollama model: {model_id}")

    try:
        response = requests.post(
            f"{base_url}/api/pull",
            json={"name": model_id},
            timeout=300,  # 5 minute timeout for initial pull request
        )

        if response.status_code == 200:
            print(f"Successfully triggered download for Ollama model: {model_id}")
        else:
            print(
                f"Failed to trigger download for Ollama model {model_id}: {response.text}"
            )
    except Exception as e:
        print(f"Error triggering Ollama model download: {str(e)}")


def _download_huggingface_model(model_id: str):
    """Pre-download a HuggingFace model."""
    try:
        # Use lazy loading for transformers
        transformers_classes = get_transformers()
        if transformers_classes is None:
            print(
                f"Cannot download HuggingFace model {model_id}: ML capabilities not available. Install PyTorch to enable HuggingFace models."
            )
            return

        AutoTokenizer, AutoModel = transformers_classes

        print(f"Pre-downloading HuggingFace model: {model_id}")

        # Download tokenizer and model to cache
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)

        print(f"Successfully pre-downloaded HuggingFace model: {model_id}")
    except Exception as e:
        print(f"Error pre-downloading HuggingFace model: {str(e)}")
        # Don't raise - this is a background operation


@router.delete("/{model_id}", response_model=Message)
def delete_llm_model(
    model_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Message:
    """
    Delete an LLM.
    """
    model = session.get(LlmModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="LLM not found")
    if model.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this model"
        )
    session.delete(model)
    session.commit()
    return Message(message="LLM deleted successfully")


@router.post("/validate", response_model=Message)
def validate_llm_model(
    session: SessionDep,
    model_data: LlmModelsValidate,
) -> Message:
    """
    Validate if an LLM ID is valid for the specified provider.
    """
    print(
        f"Validating LLM model: {model_data.model_id} for provider {model_data.provider}"
    )
    try:
        # Extract the provider and model_id
        provider = model_data.provider
        model_id = model_data.model_id

        print(f"Validating LLM: {model_id} (provider: {provider})")

        if provider == ModelProvider.OPENAI:
            # For OpenAI, attempt to create the model with a simple test

            # Get API key from environment or request
            # api_key = None  # You can add API key passing if needed

            llm = ChatOpenAI(
                model=model_id,
                temperature=0.0,
                # openai_api_key=api_key,
                max_tokens=5,  # Minimum tokens for test
                max_retries=0,  # Disable OpenAI's internal retries for validation
                request_timeout=30,  # Set reasonable timeout
            )

            # Test with a simple query to verify the model exists
            response = llm.invoke("Hello")
            print(f"OpenAI model validation successful: {model_id}")

        elif model_data.provider == ModelProvider.AWS:
            print("Now attempting to validate AWS Bedrock model...")
            try:
                # Check if AWS credentials are configured
                aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
                aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
                aws_region = os.environ.get("AWS_REGION", "eu-north-1")

                if not aws_access_key or not aws_secret_key:
                    print("AWS credentials not found in environment variables")
                    raise HTTPException(
                        status_code=400,
                        detail="AWS credentials are not configured in the environment",
                    )

                print(
                    f"Initializing Bedrock client with model: {model_id} in region: {aws_region}"
                )

                bedrock_client = boto3.client(
                    "bedrock",
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region,
                )
                print("Now listing available foundation models in AWS Bedrock...")
                print(bedrock_client.list_foundation_models())

                # Initialize Bedrock LLM using environment variables
                if "anthropic.claude" in model_id:
                    print(f"Using BedrockChat for Claude model: {model_id}")
                    # Use BedrockChat for Claude models]

                    # Create the bedrock-runtime client for regular operations
                    runtime_client = boto3.client(
                        "bedrock-runtime",
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=aws_region,
                    )

                    bedrock_llm = ChatBedrock(
                        model_id=model_id,
                        model_kwargs={"temperature": 0.0},
                        provider="anthropic" if "claude" in model_id else "amazon",
                    )

                    messages = [
                        HumanMessage(
                            content="Translate this sentence from English to French. I love programming."
                        )
                    ]
                    response = bedrock_llm.invoke(messages)

                else:
                    # Use standard Bedrock for other models like Titan
                    print(f"Using standard Bedrock for model: {model_id}")

                    bedrock_client = boto3.client(
                        "bedrock-runtime",
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=aws_region,
                    )

                    bedrock_llm = Bedrock(
                        model_id=model_id, region_name=aws_region, client=bedrock_client
                    )

                    prompt_template = "What is the capital city of {country}?"

                    prompt = PromptTemplate(
                        input_variables=["country"], template=prompt_template
                    )

                    llm = LLMChain(llm=bedrock_llm, prompt=prompt)

                    response = llm.invoke({"country": "Canada"})

                print(f"Received response from AWS Bedrock: {response}")
                print(f"AWS Bedrock model validation successful: {model_id}")

            except Exception as e:
                traceback.print_exc()
                error_msg = str(e)
                print(f"Error validating AWS Bedrock model: {error_msg}")

                if (
                    "not authorized" in error_msg.lower()
                    or "access denied" in error_msg.lower()
                ):
                    detail = (
                        "AWS credentials not authorized to access Bedrock or this model"
                    )
                elif (
                    "not found" in error_msg.lower()
                    or "does not exist" in error_msg.lower()
                ):
                    detail = f"Model {model_id} not found in AWS Bedrock"
                elif (
                    "quota exceeded" in error_msg.lower()
                    or "limit" in error_msg.lower()
                ):
                    detail = "AWS Bedrock quota exceeded or limits reached"
                else:
                    detail = f"Invalid AWS Bedrock model or configuration: {error_msg}"

                raise HTTPException(status_code=400, detail=detail)

        elif provider == ModelProvider.HUGGINGFACE:
            # Use lazy loading for HuggingFace models
            HuggingFacePipeline = get_huggingface_pipeline()
            model_classes = get_transformers_model_classes()
            pipeline = get_transformers_pipeline()

            if HuggingFacePipeline is None or model_classes is None or pipeline is None:
                raise HTTPException(
                    status_code=503,
                    detail="HuggingFace models not available. ML capabilities are not installed. Use OpenAI, AWS, or Ollama providers instead.",
                )

            AutoModelForCausalLM, AutoTokenizer = model_classes

            # For HuggingFace, try to load the model
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
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://ollama:11434")
            # Try to connect to Ollama server and verify model
            llm = ChatOllama(
                model=model_id,
                temperature=0.0,
                # Use default Ollama URL, or configure as needed
                base_url=base_url,
            )

            # Simple test to verify the model is available
            response = llm.invoke("Hello")
            print(f"Ollama model validation successful: {model_id}")

        elif provider == ModelProvider.REPLICATE:
            try:
                # Check if API token is configured
                if "REPLICATE_API_TOKEN" not in os.environ:
                    raise ValueError(
                        "REPLICATE_API_TOKEN not set in environment variables"
                    )

                # Try to get model info - this will fail if the model doesn't exist
                # Parse model ID to get the correct format
                if ":" in model_id:
                    owner_model, version = model_id.split(":")
                    # Get the model directly with version
                    output = replicate.run(
                        model_id, input={"prompt": "Hello"}, use_file_output=False
                    )
                else:
                    # Try using the model without explicit version
                    output = replicate.run(
                        model_id, input={"prompt": "Hello"}, use_file_output=False
                    )

                print(f"Replicate model validation successful: {model_id}")

            except Exception as e:
                print(f"Error validating Replicate model: {str(e)}")
                raise ValueError(f"Invalid Replicate model: {str(e)}")

        else:
            raise ValueError(f"Unsupported provider: {provider}")

        return Message(message=f"LLM {model_id} is valid for provider {provider}")

    except Exception as e:
        traceback.print_exc()
        print(f"LLM validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid LLM: {str(e)}")


@router.post("/{model_id}/set-default", response_model=LlmModelPublic)
def set_default_llm_model(
    model_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> LlmModelPublic:
    """
    Set an LLM as the default.
    """
    model = session.get(LlmModel, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="LLM not found")

    # Check if the model is system-owned or owned by the current user
    if model.owner_id is not None and model.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this model"
        )

    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.default_llm = model.id
    session.add(user)
    session.commit()
    session.refresh(user)
    return model
