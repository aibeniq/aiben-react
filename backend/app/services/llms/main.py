import os
from pathlib import Path
import replicate
import boto3
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
from langchain_community.chat_models import ChatOllama
from langchain_community.llms import Bedrock
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.language_models import BaseChatModel, BaseLLM
from typing import Optional, List, Dict, Any, Union
from dotenv import load_dotenv
import json
from pydantic import BaseModel
import uuid
from sqlmodel import Session
from app.models import User


# pydantic model for llm model information
class LlmModelInfo(BaseModel):
    """Model for LLM model information."""

    id: str
    provider: str
    model_name: str
    context_length: Optional[int] = None
    max_output_tokens: Optional[int] = None
    cost_per_1k_input_tokens: Optional[float] = None
    cost_per_1k_output_tokens: Optional[float] = None
    supports_streaming: bool = True
    supports_function_calling: bool = False
    supports_vision: bool = False
    description: Optional[str] = None


class LlmService:
    """Service for managing and loading LLM models."""

    # registry of available llm models
    AVAILABLE_MODELS: Dict[str, LlmModelInfo] = {
        # OpenAI Models
        "gpt-4o": LlmModelInfo(
            id="gpt-4o",
            provider="openai",
            model_name="gpt-4o",
            context_length=128000,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=5.0,
            cost_per_1k_output_tokens=15.0,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            description="OpenAI's most advanced multimodal model with vision capabilities",
        ),
        "gpt-4o-mini": LlmModelInfo(
            id="gpt-4o-mini",
            provider="openai",
            model_name="gpt-4o-mini",
            context_length=128000,
            max_output_tokens=16384,
            cost_per_1k_input_tokens=0.15,
            cost_per_1k_output_tokens=0.6,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            description="OpenAI's efficient small model with multimodal capabilities",
        ),
        "gpt-4-turbo": LlmModelInfo(
            id="gpt-4-turbo",
            provider="openai",
            model_name="gpt-4-turbo",
            context_length=128000,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=10.0,
            cost_per_1k_output_tokens=30.0,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            description="OpenAI's powerful turbo model with extended context",
        ),
        "gpt-3.5-turbo": LlmModelInfo(
            id="gpt-3.5-turbo",
            provider="openai",
            model_name="gpt-3.5-turbo",
            context_length=16385,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=0.5,
            cost_per_1k_output_tokens=1.5,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=False,
            description="OpenAI's fast and efficient model for most tasks",
        ),
        # AWS Bedrock Models
        "anthropic.claude-3-5-sonnet-20241022-v2:0": LlmModelInfo(
            id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            provider="aws",
            model_name="anthropic.claude-3-5-sonnet-20241022-v2:0",
            context_length=200000,
            max_output_tokens=8192,
            cost_per_1k_input_tokens=3.0,
            cost_per_1k_output_tokens=15.0,
            supports_streaming=True,
            supports_function_calling=True,
            supports_vision=True,
            description="Anthropic's most capable model with strong reasoning and vision capabilities",
        ),
        "anthropic.claude-3-haiku-20240307-v1:0": LlmModelInfo(
            id="anthropic.claude-3-haiku-20240307-v1:0",
            provider="aws",
            model_name="anthropic.claude-3-haiku-20240307-v1:0",
            context_length=200000,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=0.25,
            cost_per_1k_output_tokens=1.25,
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=True,
            description="Anthropic's fastest model for simple tasks and quick responses",
        ),
        "amazon.titan-text-express-v1": LlmModelInfo(
            id="amazon.titan-text-express-v1",
            provider="aws",
            model_name="amazon.titan-text-express-v1",
            context_length=8192,
            max_output_tokens=8192,
            cost_per_1k_input_tokens=0.8,
            cost_per_1k_output_tokens=1.6,
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            description="Amazon's Titan model optimized for text generation tasks",
        ),
        # Ollama Models (common local models)
        "llama3.1:8b": LlmModelInfo(
            id="llama3.1:8b",
            provider="ollama",
            model_name="llama3.1:8b",
            context_length=128000,
            max_output_tokens=8192,
            cost_per_1k_input_tokens=0.0,  # local model
            cost_per_1k_output_tokens=0.0,  # local model
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            description="Meta's Llama 3.1 8B model running locally via Ollama",
        ),
        "llama3.1:70b": LlmModelInfo(
            id="llama3.1:70b",
            provider="ollama",
            model_name="llama3.1:70b",
            context_length=128000,
            max_output_tokens=8192,
            cost_per_1k_input_tokens=0.0,  # local model
            cost_per_1k_output_tokens=0.0,  # local model
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            description="Meta's Llama 3.1 70B model running locally via Ollama",
        ),
        "mistral:7b": LlmModelInfo(
            id="mistral:7b",
            provider="ollama",
            model_name="mistral:7b",
            context_length=32768,
            max_output_tokens=8192,
            cost_per_1k_input_tokens=0.0,  # local model
            cost_per_1k_output_tokens=0.0,  # local model
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            description="Mistral 7B model running locally via Ollama",
        ),
        # Replicate Models
        "meta/llama-2-70b-chat": LlmModelInfo(
            id="meta/llama-2-70b-chat",
            provider="replicate",
            model_name="meta/llama-2-70b-chat",
            context_length=4096,
            max_output_tokens=4096,
            cost_per_1k_input_tokens=0.65,
            cost_per_1k_output_tokens=2.75,
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            description="Meta's Llama 2 70B Chat model via Replicate",
        ),
        "mistralai/mixtral-8x7b-instruct-v0.1": LlmModelInfo(
            id="mistralai/mixtral-8x7b-instruct-v0.1",
            provider="replicate",
            model_name="mistralai/mixtral-8x7b-instruct-v0.1",
            context_length=32768,
            max_output_tokens=8192,
            cost_per_1k_input_tokens=0.3,
            cost_per_1k_output_tokens=1.0,
            supports_streaming=True,
            supports_function_calling=False,
            supports_vision=False,
            description="Mistral's Mixtral 8x7B Instruct model via Replicate",
        ),
    }

    @classmethod
    def get_models(cls) -> List[LlmModelInfo]:
        """Get list of available models."""
        return list(cls.AVAILABLE_MODELS.values())

    @classmethod
    def get_default_model(cls) -> LlmModelInfo:
        """Get the default model."""
        # import here to avoid circular import
        from app.core.config import settings

        default_model_id = getattr(settings, "DEFAULT_LLM_MODEL", "gpt-4o-mini")

        if not cls.is_valid_model_id(default_model_id):
            available_models = ", ".join(cls.AVAILABLE_MODELS.keys())
            raise ValueError(
                f"Configured default LLM model '{default_model_id}' not found in registry. "
                f"Available models: {available_models}"
            )

        return cls.AVAILABLE_MODELS[default_model_id]

    @classmethod
    def get_user_default_model(
        cls, session: Session, user_id: uuid.UUID
    ) -> LlmModelInfo:
        """Get the user's default model."""
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        if not user.default_llm:
            raise ValueError(f"User with id {user_id} has no default LLM model")
        return cls.get_model_spec(user.default_llm)

    @classmethod
    def get_providers(cls) -> List[str]:
        """Get list of available providers."""
        return list(set(spec.provider for spec in cls.AVAILABLE_MODELS.values()))

    @classmethod
    def get_model_ids(cls) -> List[str]:
        """Get list of available model IDs."""
        return list(cls.AVAILABLE_MODELS.keys())

    @classmethod
    def is_valid_model_id(cls, model_id: str) -> bool:
        """Check if a model ID is valid."""
        return model_id in cls.AVAILABLE_MODELS

    @classmethod
    def get_model_spec(cls, model_id: str) -> Optional[LlmModelInfo]:
        """Get specification for a specific model."""
        return cls.AVAILABLE_MODELS.get(model_id)

    @classmethod
    def get_models_by_provider(cls, provider: str) -> List[LlmModelInfo]:
        """Get all models for a specific provider."""
        return [
            spec for spec in cls.AVAILABLE_MODELS.values() if spec.provider == provider
        ]

    @classmethod
    def validate_model(
        cls, model_id: str, api_key: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if a model is available and properly configured.

        Returns:
            tuple: (is_valid, error_message)
        """
        # check if model exists in registry
        if model_id not in cls.AVAILABLE_MODELS:
            available = ", ".join(cls.AVAILABLE_MODELS.keys())
            return False, f"Model '{model_id}' not found. Available models: {available}"

        spec = cls.AVAILABLE_MODELS[model_id]

        # validate provider-specific requirements
        if spec.provider == "openai":
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                return (
                    False,
                    f"OPENAI_API_KEY environment variable required for model '{model_id}'",
                )
        elif spec.provider == "aws":
            # check for required AWS credentials
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            if not aws_access_key or not aws_secret_key:
                return (
                    False,
                    f"AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables required for model '{model_id}'",
                )

            # validate AWS region is set
            aws_region = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")
            if not aws_region:
                return (
                    False,
                    f"AWS_DEFAULT_REGION or AWS_REGION environment variable required for model '{model_id}'",
                )
        elif spec.provider == "ollama":
            # check if ollama server is accessible
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            # basic validation - could be enhanced with actual connectivity check
            if not ollama_host:
                return (
                    False,
                    f"OLLAMA_HOST environment variable required for model '{model_id}'",
                )
        elif spec.provider == "replicate":
            api_key = api_key or os.getenv("REPLICATE_API_TOKEN")
            if not api_key:
                return (
                    False,
                    f"REPLICATE_API_TOKEN environment variable required for model '{model_id}'",
                )

        return True, None

    @classmethod
    def get_model(
        cls, model_id: str, api_key: Optional[str] = None, **kwargs
    ) -> Union[BaseChatModel, BaseLLM]:
        """
        Get an LLM model by ID.

        Args:
            model_id: The model identifier from the registry
            api_key: Optional API key override
            **kwargs: Additional model parameters

        Returns:
            An initialized LLM model

        Raises:
            ValueError: If model is invalid or cannot be loaded
        """
        # validate model
        is_valid, error_msg = cls.validate_model(model_id, api_key)
        if not is_valid:
            raise ValueError(error_msg)

        spec = cls.AVAILABLE_MODELS[model_id]

        # load model based on provider
        try:
            if spec.provider == "openai":
                return ChatOpenAI(
                    model=spec.model_name,
                    openai_api_key=api_key,
                    temperature=kwargs.get("temperature", 0.0),
                    max_tokens=kwargs.get("max_tokens", spec.max_output_tokens),
                    streaming=kwargs.get("streaming", False),
                    **{
                        k: v
                        for k, v in kwargs.items()
                        if k not in ["temperature", "max_tokens", "streaming"]
                    },
                )
            elif spec.provider == "aws":
                # get AWS region from environment
                aws_region = os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION")

                if "anthropic.claude" in spec.model_name:
                    return ChatBedrock(
                        model_id=spec.model_name,
                        region_name=aws_region,
                        model_kwargs={
                            "temperature": kwargs.get("temperature", 0.0),
                            "max_tokens": kwargs.get(
                                "max_tokens", spec.max_output_tokens
                            ),
                        },
                        streaming=kwargs.get("streaming", False),
                        **{
                            k: v
                            for k, v in kwargs.items()
                            if k not in ["temperature", "max_tokens", "streaming"]
                        },
                    )
                else:
                    return BedrockLlm(
                        model_id=spec.model_name,
                        temperature=kwargs.get("temperature", 0.0),
                        **kwargs,
                    )
            elif spec.provider == "ollama":
                ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
                return ChatOllama(
                    model=spec.model_name,
                    base_url=ollama_host,
                    temperature=kwargs.get("temperature", 0.0),
                    **{k: v for k, v in kwargs.items() if k not in ["temperature"]},
                )
            elif spec.provider == "replicate":
                return ReplicateLlm(
                    model_id=spec.model_name,
                    api_key=api_key,
                    temperature=kwargs.get("temperature", 0.0),
                    **kwargs,
                )
            else:
                raise ValueError(f"Unsupported provider: {spec.provider}")

        except Exception as e:
            raise ValueError(f"Failed to load model '{model_id}': {str(e)}")

    @staticmethod
    def record_llm_interaction(
        session: Session,
        user_id: uuid.UUID,
        functionality: str,
        input_data: Any,
        output_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> uuid.UUID:
        """
        Records an interaction with an LLM to the database.

        Args:
            session: SQLModel session
            user_id: ID of the user who initiated the request
            functionality: Service used ('chatbot', 'veradoc', 'formconnect', 'reportgenie')
            input_data: The input prompt or data sent to the LLM
            output_data: The output generated by the LLM
            metadata: Any additional information to store
        """
        # Import here to avoid circular imports
        from app.models import User, LlmInteraction

        if metadata is None:
            metadata = {}

        # Convert input and output to strings if they're not already
        if not isinstance(input_data, str):
            # Try to preserve structure by using JSON
            try:
                input_data = json.dumps(input_data)
            except:
                input_data = str(input_data)

        if not isinstance(output_data, str):
            # Try to preserve structure by using JSON
            try:
                output_data = json.dumps(output_data)
            except:
                output_data = str(output_data)

        # Get user and their default LLM info
        user = session.get(User, user_id)
        if user and user.default_llm:
            # Use the service to get model information
            model_spec = LlmService.get_model_spec(user.default_llm)
            if model_spec:
                # Add LLM info to metadata
                metadata["llm_model_id"] = model_spec.id
                metadata["llm_provider"] = model_spec.provider

        # Create and save interaction record
        interaction = LlmInteraction(
            user_id=user_id,
            functionality=functionality,
            input_data=input_data,
            output_data=output_data,
            extra_data=metadata,
        )

        session.add(interaction)
        session.commit()
        session.refresh(interaction)
        return interaction.id


class ReplicateLlm:
    """LLM implementation using Replicate API."""

    current_dir = Path(__file__).resolve().parent
    root_dir = current_dir.parent.parent.parent
    load_dotenv(dotenv_path=os.path.join(root_dir, ".env"), override=True)

    def __init__(
        self,
        model_id: str,
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """Initialize Replicate LLM.

        Args:
            model_id: The model identifier on Replicate
            temperature: Temperature for generation
            api_key: Optional API key for Replicate
            **kwargs: Additional model parameters
        """
        self.model_id = model_id
        self.temperature = temperature
        self.kwargs = kwargs

        # set API key if provided
        if api_key:
            os.environ["REPLICATE_API_TOKEN"] = api_key

        # check if we have a modelversion format (owner/model:version)
        if ":" in model_id:
            self.owner_model, self.version = model_id.split(":")
        else:
            self.owner_model = model_id
            self.version = None

    def invoke(self, prompt: Union[str, List[BaseMessage]], **kwargs) -> str:
        """Generate text using the Replicate model."""
        # format prompt based on input type
        if isinstance(prompt, str):
            input_text = prompt
            system_prompt = self.kwargs.get("system_prompt", "")
        elif isinstance(prompt, list):
            # handle list of messages
            system_messages = [
                msg.content
                for msg in prompt
                if hasattr(msg, "type") and msg.type == "system"
            ]
            user_messages = [
                msg.content
                for msg in prompt
                if hasattr(msg, "content")
                and not (hasattr(msg, "type") and msg.type == "system")
            ]

            system_prompt = (
                system_messages[0]
                if system_messages
                else self.kwargs.get("system_prompt", "")
            )
            input_text = "\n".join(user_messages)
        else:
            input_text = str(prompt)
            system_prompt = self.kwargs.get("system_prompt", "")

        try:
            # prepare input parameters
            input_params = {
                "prompt": input_text,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", 4096),
            }

            # add system prompt if available
            if system_prompt:
                input_params["system_prompt"] = system_prompt

            # add any additional parameters
            for key, value in {**self.kwargs, **kwargs}.items():
                if key not in ["system_prompt", "temperature", "max_tokens"]:
                    input_params[key] = value

            # use streaming if requested
            if kwargs.get("streaming", False):
                chunks = []
                for chunk in replicate.stream(self.model_id, input=input_params):
                    chunks.append(chunk)
                return "".join(chunks)
            else:
                output = replicate.run(self.model_id, input=input_params)

                # handle various output formats
                if isinstance(output, list):
                    return output[0] if len(output) == 1 else "".join(output)
                return str(output)

        except Exception as e:
            raise ValueError(f"Error generating text with Replicate: {str(e)}")

    def __or__(self, other):
        """Support for pipe operator."""

        def chain_func(inputs):
            if isinstance(inputs, dict):
                prompt_parts = []
                for key, value in inputs.items():
                    prompt_parts.append(f"{key}: {value}")
                prompt = "\n".join(prompt_parts)
            else:
                prompt = str(inputs)

            result = self.invoke(prompt)
            return type("obj", (object,), {"content": result})()

        return chain_func


class BedrockLlm:
    """LLM implementation using AWS Bedrock API."""

    def __init__(self, model_id: str, temperature: float = 0.0, **kwargs):
        """Initialize Bedrock LLM.

        Args:
            model_id: The model identifier on AWS Bedrock
            temperature: Temperature for generation
            **kwargs: Additional model parameters
        """
        self.model_id = model_id
        self.temperature = temperature
        self.kwargs = kwargs

        # initialize AWS Bedrock client
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=os.environ.get("AWS_REGION", "us-east-1"),
        )

        # create the appropriate LangChain instance
        if "anthropic.claude" in self.model_id:
            self.bedrock = ChatBedrock(
                model_id=self.model_id,
                client=self.client,
                model_kwargs={"temperature": self.temperature},
                **{k: v for k, v in kwargs.items() if k not in ["system_prompt"]},
            )
        else:
            self.bedrock = Bedrock(
                model_id=self.model_id,
                client=self.client,
                model_kwargs={"temperature": self.temperature},
                **{k: v for k, v in kwargs.items() if k not in ["system_prompt"]},
            )

    def invoke(self, prompt: Union[str, List[BaseMessage]], **kwargs) -> str:
        """Generate text using the Bedrock model."""
        system_prompt = self.kwargs.get("system_prompt", "")

        if "anthropic.claude" in self.model_id:
            # for Claude models using ChatBedrock
            messages = []

            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))

            if isinstance(prompt, str):
                messages.append(HumanMessage(content=prompt))
            elif isinstance(prompt, list):
                messages = prompt
            else:
                messages.append(HumanMessage(content=str(prompt)))

            try:
                response = self.bedrock.invoke(messages)
                return (
                    response.content if hasattr(response, "content") else str(response)
                )
            except Exception as e:
                raise ValueError(f"Error calling AWS Bedrock Chat: {str(e)}")
        else:
            # for non-Claude models
            if isinstance(prompt, str):
                input_text = prompt
            elif isinstance(prompt, list):
                user_messages = [
                    msg.content for msg in prompt if hasattr(msg, "content")
                ]
                input_text = "\n".join(user_messages)
            else:
                input_text = str(prompt)

            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{input_text}"
            else:
                full_prompt = input_text

            try:
                response = self.bedrock.invoke(full_prompt)
                return response if isinstance(response, str) else str(response)
            except Exception as e:
                raise ValueError(f"Error calling AWS Bedrock: {str(e)}")

    def __or__(self, other):
        """Support for pipe operator."""

        def chain_func(inputs):
            if isinstance(inputs, dict):
                prompt_parts = []
                for key, value in inputs.items():
                    prompt_parts.append(f"{key}: {value}")
                prompt = "\n".join(prompt_parts)
            else:
                prompt = str(inputs)

            result = self.invoke(prompt)
            return type("obj", (object,), {"content": result})()

        return chain_func


class LlmInferenceService:
    """Service for handling LLM inference operations."""

    def __init__(self, model_id: str, api_key: Optional[str] = None, **kwargs):
        """Initialize the inference service with a specific model."""
        self.model_id = model_id
        self.model = LlmService.get_model(model_id, api_key, **kwargs)
        self.model_spec = LlmService.get_model_spec(model_id)

    def generate_text(
        self,
        prompt: Union[str, List[BaseMessage]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
        **kwargs,
    ) -> str:
        """Generate text using the configured model."""
        # prepare generation parameters
        generation_kwargs = {}

        if temperature is not None:
            generation_kwargs["temperature"] = temperature
        if max_tokens is not None:
            generation_kwargs["max_tokens"] = max_tokens
        if streaming:
            generation_kwargs["streaming"] = streaming

        # add any additional parameters
        generation_kwargs.update(kwargs)

        try:
            # handle system prompt
            if system_prompt and isinstance(prompt, str):
                if hasattr(self.model, "invoke"):
                    # for custom wrappers
                    if hasattr(self.model, "kwargs"):
                        self.model.kwargs["system_prompt"] = system_prompt
                    return self.model.invoke(prompt, **generation_kwargs)
                else:
                    # for langchain models
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=prompt),
                    ]
                    response = self.model.invoke(messages, **generation_kwargs)
                    return (
                        response.content
                        if hasattr(response, "content")
                        else str(response)
                    )
            else:
                # direct invocation
                if hasattr(self.model, "invoke"):
                    response = self.model.invoke(prompt, **generation_kwargs)
                    return (
                        response.content
                        if hasattr(response, "content")
                        else str(response)
                    )
                else:
                    response = self.model.invoke(prompt, **generation_kwargs)
                    return (
                        response.content
                        if hasattr(response, "content")
                        else str(response)
                    )

        except Exception as e:
            raise ValueError(f"Error generating text: {str(e)}")

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Generate a chat response from a list of messages."""
        # convert messages to langchain format
        langchain_messages = []
        for msg in messages:
            if msg["role"] == "system":
                langchain_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            # could add AssistantMessage for assistant messages if needed

        return self.generate_text(
            langchain_messages, temperature=temperature, max_tokens=max_tokens, **kwargs
        )

    def validate_model_connection(self) -> tuple[bool, Optional[str]]:
        """Test if the model is properly configured and accessible."""
        try:
            # simple test prompt
            test_response = self.generate_text(
                "Hello, please respond with 'OK' if you can process this message.",
                max_tokens=10,
            )
            return True, f"Model responded: {test_response[:50]}..."
        except Exception as e:
            return False, f"Model validation failed: {str(e)}"

    def get_model_info(self) -> LlmModelInfo:
        """Get information about the current model."""
        return self.model_spec or LlmModelInfo(
            id=self.model_id,
            provider="unknown",
            model_name=self.model_id,
            description="Model information not available",
        )
