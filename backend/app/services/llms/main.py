import json
import os
import uuid
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel
from sqlmodel import Session

from app.models import Tool, User, ToolInteraction, ToolInteractionExtraData


# pydantic model for llm model information
class LlmProvider(BaseModel):
    """Model for LLM provider information."""

    id: str  # used by langchain to identify the provider
    name: str  # used by the UI to display the provider name
    required_env_vars: list[str]  # required environment variables (api keys, etc.)


# pydantic model for llm model information
class LlmModelSpec(BaseModel):
    """Model for LLM model information."""

    id: str
    provider: LlmProvider
    model_name: str
    context_length: int | None = None
    max_output_tokens: int | None = None
    cost_per_1M_input_tokens: float | None = None
    cost_per_1M_output_tokens: float | None = None
    supports_streaming: bool = True
    supports_function_calling: bool = False
    supports_vision: bool = False
    description: str | None = None


PROVIDERS: dict[str, LlmProvider] = {
    "openai": LlmProvider(
        id="openai",
        name="OpenAI",
        required_env_vars=["OPENAI_API_KEY"],
    ),
    "bedrock": LlmProvider(
        id="bedrock",
        name="Bedrock",
        required_env_vars=["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION"],
    ),
    "ollama": LlmProvider(
        id="ollama",
        name="Ollama",
        required_env_vars=["OLLAMA_BASE_URL"],
    ),
    "replicate": LlmProvider(
        id="replicate",
        name="Replicate",
        required_env_vars=["REPLICATE_API_TOKEN"],
    ),
    "together": LlmProvider(
        id="together",
        name="Together",
        required_env_vars=["TOGETHER_API_KEY"],
    ),
}

MODELS: dict[str, LlmModelSpec] = {
    "gpt-4o": LlmModelSpec(
        id="gpt-4o",
        provider=PROVIDERS["openai"],
        model_name="gpt-4o",
        context_length=128000,
        max_output_tokens=16384,
        cost_per_1M_input_tokens=2.5,
        cost_per_1M_output_tokens=10.0,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
        description="Fast, intelligent, flexible GPT model",
    ),
    "gpt-4o-mini": LlmModelSpec(
        id="gpt-4o-mini",
        provider=PROVIDERS["openai"],
        model_name="gpt-4o-mini",
        context_length=128000,
        max_output_tokens=16384,
        cost_per_1M_input_tokens=0.15,
        cost_per_1M_output_tokens=0.6,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
        description="Fast, affordable small model for focused tasks",
    ),
    "gpt-4.1": LlmModelSpec(
        id="gpt-4.1",
        provider=PROVIDERS["openai"],
        model_name="gpt-4.1",
        context_length=1047576,
        max_output_tokens=32768,
        cost_per_1M_input_tokens=2.0,
        cost_per_1M_output_tokens=8.0,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
        description="Flagship GPT model for complex tasks",
    ),
}


class LlmService:
    """Service for managing and loading LLM models."""

    @classmethod
    def get_model_specs(cls) -> list[LlmModelSpec]:
        """Get list of available models."""
        return list(MODELS.values())

    @classmethod
    def get_default_model_spec(cls) -> LlmModelSpec:
        """Get the default model."""
        # import here to avoid circular import
        from app.core.config import settings

        default_model_id = getattr(settings, "DEFAULT_LLM_MODEL", "gpt-4o-mini")

        try:
            spec = cls.get_model_spec(default_model_id)
        except ValueError as e:
            raise ValueError(
                f"Configured default LLM model '{default_model_id}' not found in registry. "
                f"Available models: {cls.get_model_ids()}. Error: {str(e)}"
            )

        return spec

    @classmethod
    def get_user_default_model_spec(
        cls, session: Session, user_id: uuid.UUID
    ) -> LlmModelSpec:
        """Get the user's default model."""
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        if not user.default_llm:
            raise ValueError(f"User with id {user_id} has no default LLM model")
        try:
            return cls.get_model_spec(user.default_llm)
        except ValueError as e:
            raise ValueError(
                f"User's default LLM model {user.default_llm} is invalid: {str(e)}"
            )
        except Exception as e:
            raise ValueError(f"Error getting user's default LLM model: {str(e)}")

    @classmethod
    def get_providers(cls) -> list[str]:
        """Get list of available providers."""
        # import here to avoid circular import
        from app.core.config import settings

        return [
            provider.id
            for provider in PROVIDERS.values()
            if provider.id in settings.ENABLED_PROVIDERS
        ]

    @classmethod
    def get_model_ids(cls) -> list[str]:
        """Get list of available model IDs."""
        return [model_spec.id for model_spec in cls.get_model_specs()]

    @classmethod
    def is_valid_model_id(cls, model_id: str) -> bool:
        """Check if a model ID is valid."""
        return model_id in MODELS

    @classmethod
    def get_model_specs_by_provider(cls, provider: str) -> list[LlmModelSpec]:
        """Get all models for a specific provider."""
        return [spec for spec in MODELS.values() if spec.provider.id == provider]

    @classmethod
    def get_model_spec(cls, model_id: str) -> LlmModelSpec:
        """
        Validate if a model is available and properly configured.

        Returns:
            LlmModelSpec: The validated model specification
        """
        # check if model exists in registry
        if model_id not in MODELS:
            available = ", ".join(cls.get_model_ids())
            raise ValueError(
                f"Model '{model_id}' not found. Available models: {available}"
            )

        # check if provider is enabled
        spec = MODELS[model_id]
        if spec.provider.id not in cls.get_providers():
            raise ValueError(
                f"Provider '{spec.provider.id}' is not enabled. Available providers: {cls.get_providers()}"
            )

        # validate required environment variables
        required_env_vars = spec.provider.required_env_vars
        for env_var in required_env_vars:
            if not os.getenv(env_var):
                raise ValueError(
                    f"{env_var} environment variable required for '{model_id}'"
                )

        return spec

    @classmethod
    def get_model(cls, model_id: str, **kwargs: Any) -> BaseChatModel:
        """
        Get an LLM model by ID.

        Args:
            model_id: The model identifier from the registry
            **kwargs: Additional model parameters (temperature, max_tokens, streaming, etc.)

        Returns:
            An initialized LLM model

        Raises:
            ValueError: If model is invalid or cannot be loaded
            ImportError: If model provider integration package not installed
        """
        try:
            spec = cls.get_model_spec(model_id)

            llm_params = {
                "temperature": kwargs.get("temperature", 0.0),
                "max_tokens": kwargs.get("max_tokens", spec.max_output_tokens),
                "streaming": kwargs.get("streaming", False),
            }
            llm_params.update(kwargs)
            llm: BaseChatModel = init_chat_model(
                model=spec.model_name,
                model_provider=spec.provider.id,
                **llm_params,
            )
            return llm

        except ImportError:
            raise ImportError(f"Provider LangChain package missing: {spec.provider}")

        except Exception as e:
            raise ValueError(f"Failed to load model '{model_id}': {str(e)}")

    @staticmethod
    def record_tool_interaction(
        session: Session,
        user_id: uuid.UUID,
        functionality: Tool,
        input_data: Any,
        output_data: Any,
        metadata: ToolInteractionExtraData | None = None,
    ) -> uuid.UUID:
        """
        Records an interaction with an LLM to the database.

        Args:
            session: SQLModel session
            user_id: ID of the user who initiated the request
            functionality: Service used (Tool enum)
            input_data: The input prompt or data sent to the LLM
            output_data: The output generated by the LLM
            metadata: Any additional information to store
        """
        if metadata is None:
            metadata = ToolInteractionExtraData()

        # Convert input and output to strings if they're not already
        if not isinstance(input_data, str):
            # Try to preserve structure by using JSON
            try:
                input_data = json.dumps(input_data)
            except Exception:
                input_data = str(input_data)

        if not isinstance(output_data, str):
            # Try to preserve structure by using JSON
            try:
                output_data = json.dumps(output_data)
            except Exception:
                output_data = str(output_data)

        # Get user and their default LLM info
        user = session.get(User, user_id)
        if user and user.default_llm:
            try:
                spec = LlmService.get_model_spec(user.default_llm)
            except ValueError as e:
                raise ValueError(
                    f"User's default LLM model {user.default_llm} is invalid: {str(e)}"
                )
            except Exception as e:
                raise ValueError(f"Error getting user's default LLM model: {str(e)}")

            # Add LLM info to metadata
            metadata["llm_model_id"] = spec.id
            metadata["llm_provider"] = spec.provider.id

        # Create and save interaction record
        interaction = ToolInteraction(
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


# class ReplicateLlm:
#     """LLM implementation using Replicate API."""

#     current_dir = Path(__file__).resolve().parent
#     root_dir = current_dir.parent.parent.parent
#     load_dotenv(dotenv_path=os.path.join(root_dir, ".env"), override=True)

#     def __init__(
#         self,
#         model_id: str,
#         temperature: float = 0.0,
#         api_key: Optional[str] = None,
#         **kwargs: Any,
#     ) -> None:
#         """Initialize Replicate LLM.

#         Args:
#             model_id: The model identifier on Replicate
#             temperature: Temperature for generation
#             api_key: Optional API key for Replicate
#             **kwargs: Additional model parameters
#         """
#         self.model_id = model_id
#         self.temperature = temperature
#         self.kwargs = kwargs

#         # set API key if provided
#         if api_key:
#             os.environ["REPLICATE_API_TOKEN"] = api_key

#         # check if we have a modelversion format (owner/model:version)
#         if ":" in model_id:
#             self.owner_model, self.version = model_id.split(":")
#         else:
#             self.owner_model = model_id
#             self.version = None

#     def invoke(self, prompt: Union[str, List[BaseMessage]], **kwargs: Any) -> str:
#         """Generate text using the Replicate model."""
#         # format prompt based on input type
#         if isinstance(prompt, str):
#             input_text = prompt
#             system_prompt = self.kwargs.get("system_prompt", "")
#         elif isinstance(prompt, list):
#             # handle list of messages
#             system_messages = [
#                 msg.content
#                 for msg in prompt
#                 if hasattr(msg, "type") and msg.type == "system"
#             ]
#             user_messages = [
#                 msg.content
#                 for msg in prompt
#                 if hasattr(msg, "content")
#                 and not (hasattr(msg, "type") and msg.type == "system")
#             ]

#             system_prompt = (
#                 system_messages[0]
#                 if system_messages
#                 else self.kwargs.get("system_prompt", "")
#             )
#             input_text = "\n".join(user_messages)
#         else:
#             input_text = str(prompt)
#             system_prompt = self.kwargs.get("system_prompt", "")

#         try:
#             # prepare input parameters
#             input_params = {
#                 "prompt": input_text,
#                 "temperature": kwargs.get("temperature", self.temperature),
#                 "max_tokens": kwargs.get("max_tokens", 4096),
#             }

#             # add system prompt if available
#             if system_prompt:
#                 input_params["system_prompt"] = system_prompt

#             # add any additional parameters
#             for key, value in {**self.kwargs, **kwargs}.items():
#                 if key not in ["system_prompt", "temperature", "max_tokens"]:
#                     input_params[key] = value

#             # use streaming if requested
#             if kwargs.get("streaming", False):
#                 chunks = []
#                 for chunk in replicate.stream(self.model_id, input=input_params):
#                     chunks.append(chunk)
#                 return "".join(chunks)
#             else:
#                 output = replicate.run(self.model_id, input=input_params)

#                 # handle various output formats
#                 if isinstance(output, list):
#                     return output[0] if len(output) == 1 else "".join(output)
#                 return str(output)

#         except Exception as e:
#             raise ValueError(f"Error generating text with Replicate: {str(e)}")

#     def __or__(self, other: Any) -> Any:
#         """Support for pipe operator."""

#         def chain_func(inputs: Any) -> Any:
#             if isinstance(inputs, dict):
#                 prompt_parts = []
#                 for key, value in inputs.items():
#                     prompt_parts.append(f"{key}: {value}")
#                 prompt = "\n".join(prompt_parts)
#             else:
#                 prompt = str(inputs)

#             result = self.invoke(prompt)
#             return type("obj", (object,), {"content": result})()

#         return chain_func
