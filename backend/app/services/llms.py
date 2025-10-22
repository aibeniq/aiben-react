import replicate
import os
from io import BytesIO
import base64
from app.models import ModelProvider, LlmModel, User, LlmInteraction
from langchain_openai import ChatOpenAI
from langchain_aws import ChatBedrock
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Optional, Any, Dict
from app.api.deps import SessionDep, CurrentUser
from app.core.config import settings
from sqlmodel import select, Session
from langchain_community.llms import Replicate
from langchain.schema import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import uuid
import traceback
import json
import boto3
from langchain_community.llms import Bedrock
from langchain.chains import LLMChain
from app.services.retry_utils import (
    retry_openai_api,
    retry_aws_api,
    retry_replicate_api,
)
from app.services.global_rate_limiter import (
    global_rate_limiter,
    estimate_tokens,
)
from app.services.openai_queue import openai_request_queue
import logging

logger = logging.getLogger(__name__)


def downsample_image_base64(image_b64: str, max_dimension: int = None) -> str:
    """
    Downsample an image from base64 to ensure maximum dimension is max_dimension pixels.
    Maintains aspect ratio.

    Args:
        image_b64: Base64 encoded image
        max_dimension: Maximum width or height in pixels (uses config default if None)

    Returns:
        Base64 encoded downsampled image
    """
    if max_dimension is None:
        from app.core.config import settings

        max_dimension = getattr(settings, "VISION_IMAGE_MAX_DIMENSION", 512)
    try:
        from PIL import Image
        import io

        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_b64)

        # Open image with PIL
        image = Image.open(io.BytesIO(image_bytes))

        # Check if downsampling is needed
        width, height = image.size
        if width <= max_dimension and height <= max_dimension:
            # No downsampling needed
            return image_b64

        # Calculate new dimensions maintaining aspect ratio
        if width > height:
            new_width = max_dimension
            new_height = int(height * max_dimension / width)
        else:
            new_height = max_dimension
            new_width = int(width * max_dimension / height)

        # Resize image
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Convert back to bytes
        output_buffer = io.BytesIO()
        resized_image.save(output_buffer, format=image.format or "PNG")
        resized_bytes = output_buffer.getvalue()

        # Encode back to base64
        resized_b64 = base64.b64encode(resized_bytes).decode()

        logger.debug(
            f"Downsampled image from {width}x{height} to {new_width}x{new_height}"
        )

        return resized_b64

    except ImportError:
        logger.warning(
            "PIL/Pillow not available for image downsampling, using original image"
        )
        return image_b64
    except Exception as e:
        logger.warning(f"Error downsampling image: {e}, using original image")
        return image_b64


async def execute_openai_request_safely(
    func: callable, formatted_text: str, request_type: str = "llm_invoke", **kwargs
) -> Any:
    """
    Safely execute an OpenAI request using both rate limiting and queue management.

    Args:
        func: The function to execute (LLM invocation)
        formatted_text: The text being sent (for token estimation)
        request_type: Type of request for logging
        **kwargs: Additional arguments to pass to the function

    Returns:
        Result of the function call
    """
    # Estimate tokens needed for this request
    estimated_tokens = estimate_tokens(formatted_text)

    logger.info(
        f"🎯 Queuing OpenAI request ({request_type}) with {estimated_tokens} estimated tokens"
    )

    # Use the queue to manage the request
    result = await openai_request_queue.add_request(
        func, request_type=request_type, estimated_tokens=estimated_tokens, **kwargs
    )

    return result


def create_openai_request_wrapper(formatted_text: str, model_class_name: str):
    """
    Create a wrapper function for OpenAI requests that includes rate limiting.

    Args:
        formatted_text: The text being processed
        model_class_name: Name of the model class

    Returns:
        Function that can be called to execute the OpenAI request safely
    """

    def openai_request_func():
        # Wait for capacity using the global rate limiter
        estimated_tokens = estimate_tokens(formatted_text)

        from app.core.config import settings

        if not global_rate_limiter.wait_for_capacity(
            estimated_tokens, max_wait_time=settings.OPENAI_RATE_LIMIT_MAX_WAIT
        ):
            raise Exception(
                "Global rate limiter: Maximum wait time exceeded for OpenAI request"
            )

        logger.info(
            f"🚀 Proceeding with OpenAI request ({estimated_tokens} estimated tokens)"
        )

        # The actual request will be executed by the calling code
        return True  # Placeholder - actual execution happens in _invoke_langchain_model

    return openai_request_func


class ReplicateWrapper:
    """Wrapper for Replicate API to make it compatible with our interface"""

    def __init__(self, model_id: str, temperature: float = 0.0, **kwargs):
        self.model_id = model_id
        self.temperature = temperature
        self.kwargs = kwargs

        # Check if we have a modelversion format (owner/model:version)
        if ":" in model_id:
            self.owner_model, self.version = model_id.split(":")
        else:
            self.owner_model = model_id
            self.version = None

    # Add this method to make it work with the | operator
    def __or__(self, other):
        # If used with pipe operator, just return the result of invoke directly
        print("ReplicateWrapper: __or__ method called")

        def chain_func(inputs):
            print(f"ReplicateWrapper chain function called with inputs: {inputs}")
            # Format prompt from inputs
            if isinstance(inputs, dict):
                # Extract all values and join them with newlines
                prompt_parts = []
                for key, value in inputs.items():
                    prompt_parts.append(f"{key}: {value}")
                prompt = "\n".join(prompt_parts)
            else:
                prompt = str(inputs)

            # Call invoke with the formatted prompt
            result = self.invoke(prompt)
            # Return an object with content attribute to mimic LangChain format
            return type("obj", (object,), {"content": result})

        return chain_func

    @retry_replicate_api(min_wait=1, max_wait=60, max_attempts=6)
    def invoke(self, prompt):
        """Run the model with the provided prompt"""
        if isinstance(prompt, str):
            input_text = prompt
            system_prompt = self.kwargs.get("system_prompt", "")
        elif hasattr(prompt, "content"):
            input_text = prompt.content
            system_prompt = self.kwargs.get("system_prompt", "")
        else:
            # Handle list of messages by identifying system and user messages
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

        try:
            # Prepare input with proper structure for Replicate models
            input_params = {
                "prompt": input_text,
                "temperature": self.temperature,
            }

            # Add system prompt if available
            if system_prompt:
                input_params["system_prompt"] = system_prompt

            # Add any additional parameters from kwargs that should be passed to the model
            for key, value in self.kwargs.items():
                if key not in ["system_prompt"]:  # Skip already handled keys
                    input_params[key] = value

            print(f"Running Replicate model: {self.model_id}")
            print(f"Input parameters: {input_params}")

            # Use Replicate's stream function for better compatibility
            if self.kwargs.get("streaming", False):
                # For streaming, we'll gather chunks and join them
                chunks = []
                for chunk in replicate.stream(
                    self.model_id if self.version else self.owner_model,
                    input=input_params,
                ):
                    chunks.append(chunk)
                return "".join(chunks)
            else:
                # For non-streaming use case
                output = replicate.run(
                    self.model_id if self.version else self.owner_model,
                    input=input_params,
                )

                # Handle various output formats
                if isinstance(output, list):
                    return output[0] if len(output) == 1 else "".join(output)
                return output
        except Exception as e:
            print(f"Error running Replicate model: {e}")
            raise


class BedrockWrapper:
    """Wrapper for AWS Bedrock API to make it compatible with our interface"""

    def __init__(self, model_id: str, temperature: float = 0.0, **kwargs):
        self.model_id = model_id
        self.temperature = temperature
        self.kwargs = kwargs

        # Initialize AWS Bedrock client using environment variables by default
        self.client = self._initialize_client()

        # Create the appropriate LangChain instance based on model type
        if "anthropic.claude" in self.model_id:
            # For Claude models, use ChatBedrock

            self.bedrock = ChatBedrock(
                model_id=self.model_id,
                client=self.client,
                model_kwargs={"temperature": self.temperature},
                provider="anthropic",
                **{k: v for k, v in kwargs.items() if k not in ["system_prompt"]},
            )
        else:
            # For other models like Amazon Titan, use standard Bedrock
            self.bedrock = Bedrock(
                model_id=self.model_id,
                client=self.client,
                model_kwargs={"temperature": self.temperature},
                provider="amazon" if "amazon" in self.model_id else None,
                **{k: v for k, v in kwargs.items() if k not in ["system_prompt"]},
            )

    def _initialize_client(self):
        """Initialize the Bedrock client using the AWS SDK"""
        # Use AWS credentials from environment variables by default
        return boto3.client(
            "bedrock-runtime",  # Changed from 'bedrock' to 'bedrock-runtime'
            region_name=os.environ.get("AWS_REGION", "eu-north-1"),
        )

    # Add this method to make it work with the | operator
    def __or__(self, other):
        # If used with pipe operator, just return the result of invoke directly
        print("BedrockWrapper: __or__ method called")

        def chain_func(inputs):
            print(f"BedrockWrapper chain function called with inputs: {inputs}")
            # Format prompt from inputs
            if isinstance(inputs, dict):
                # Extract all values and join them with newlines
                prompt_parts = []
                for key, value in inputs.items():
                    prompt_parts.append(f"{key}: {value}")
                prompt = "\n".join(prompt_parts)
            else:
                prompt = str(inputs)

            # Call invoke with the formatted prompt
            result = self.invoke(prompt)
            # Return an object with content attribute to mimic LangChain format
            return type("obj", (object,), {"content": result})

        return chain_func

    @retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)
    def invoke(self, prompt):
        """Run the model with the provided prompt"""
        system_prompt = self.kwargs.get("system_prompt", "")

        # Handle differently based on model type
        if "anthropic.claude" in self.model_id:
            # For Claude models using ChatBedrock
            # Prepare messages for chat models
            messages = []

            # Add system message if provided
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))

            # Handle different input types
            if isinstance(prompt, str):
                messages.append(HumanMessage(content=prompt))
            elif hasattr(prompt, "content"):
                messages.append(HumanMessage(content=prompt.content))
            elif isinstance(prompt, list):
                # If prompt is already a list of messages, use it directly
                # This assumes the messages are already properly formatted
                messages = prompt

            try:
                # Use the ChatBedrock instance to invoke the model
                response = self.bedrock.invoke(messages)
                # Return the text content if available, otherwise the whole response
                return response.content if hasattr(response, "content") else response
            except Exception as e:
                print(f"Error calling AWS Bedrock Chat: {e}")
                print("Exception details:", str(e))
                raise
        else:
            # For non-Claude models (like Amazon Titan)
            # Format the text prompt appropriately
            if isinstance(prompt, str):
                input_text = prompt
            elif hasattr(prompt, "content"):
                input_text = prompt.content
            else:
                # Handle list of messages by extracting text content
                user_messages = [
                    msg.content for msg in prompt if hasattr(msg, "content")
                ]
                input_text = "\n".join(user_messages)

            # Add system prompt if available
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{input_text}"
            else:
                full_prompt = input_text

            try:
                # For standard Bedrock models
                response = self.bedrock.invoke(full_prompt)
                return response
            except Exception as e:
                print(f"Error calling AWS Bedrock: {e}")
                print("Exception details:", str(e))
                raise


def create_llm(
    provider: ModelProvider,
    model_id: str,
    temperature: float = 0.0,
    api_key: Optional[str] = None,
    additional_params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Factory function to create the appropriate LLM based on provider.
    """
    params = additional_params or {}

    if provider == ModelProvider.AWS:
        print(f"Creating AWS Bedrock LLM wrapper for model: {model_id}")

        # Check if AWS credentials are configured
        if not os.environ.get("AWS_ACCESS_KEY_ID") or not os.environ.get(
            "AWS_SECRET_ACCESS_KEY"
        ):
            print("WARNING: AWS credentials not found in environment variables")

        # Create BedrockWrapper instance
        wrapper = BedrockWrapper(model_id=model_id, temperature=temperature, **params)
        print("AWS Bedrock LLM wrapper created successfully.")
        return wrapper

    elif provider == ModelProvider.OPENAI:
        # If API key is provided, use it; otherwise, rely on environment variable
        # Disable OpenAI's built-in retries to avoid conflicts with Tenacity
        if api_key:
            return ChatOpenAI(
                model=model_id,
                temperature=temperature,
                openai_api_key=api_key,
                max_retries=0,  # Disable OpenAI's internal retries
                request_timeout=settings.OPENAI_TIMEOUT,  # Use configurable timeout (10 minutes)
                **params,
            )
        else:
            return ChatOpenAI(
                model=model_id,
                temperature=temperature,
                max_retries=0,  # Disable OpenAI's internal retries
                request_timeout=settings.OPENAI_TIMEOUT,  # Use configurable timeout (10 minutes)
                **params,
            )

    elif provider == ModelProvider.OLLAMA:
        # Configure Ollama
        base_url = params.get("OLLAMA_BASE_URL", "http://ollama:11434")
        return ChatOllama(
            model=model_id, temperature=temperature, base_url=base_url, **params
        )

    elif provider == ModelProvider.REPLICATE:
        # Configure Replicate
        if api_key:
            print("API key provided with length:", len(api_key))
            os.environ["REPLICATE_API_TOKEN"] = api_key

        print(f"Creating Replicate LLM wrapper for model: {model_id}")
        print(
            f"REPLICATE_API_TOKEN set: {'Yes' if 'REPLICATE_API_TOKEN' in os.environ else 'No'}"
        )
        print(f"Token length: {len(os.environ.get('REPLICATE_API_TOKEN', ''))}")

        print("Now creating Replicate LLM wrapper...")
        wrapper = ReplicateWrapper(model_id=model_id, temperature=temperature, **params)
        print("Replicate LLM wrapper created successfully.")
        # Create a Replicate wrapper
        return wrapper

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_default_llm(session: SessionDep, current_user) -> Any:
    """
    Get the user's default LLM instance, or fall back to a system default
    that's enabled in the configuration.
    """
    # Try to get the user's configured default LLM
    user = session.get(User, current_user.id)
    if user and user.default_llm:
        model = session.get(LlmModel, user.default_llm)
        if model:
            return create_llm(
                provider=model.provider, model_id=model.model_id, temperature=0.0
            )

    # Get enabled providers from config
    enabled_providers = settings.llm_providers

    # Get all system default models
    system_defaults = session.exec(
        select(LlmModel).where(LlmModel.owner_id.is_(None))
    ).all()

    # First try: Find the first system model with an enabled provider
    for model in system_defaults:
        if model.provider.value.lower() in enabled_providers:
            print(f"Using system default LLM: {model.name} ({model.provider.value})")
            return create_llm(
                provider=model.provider,
                model_id=model.model_id,
                temperature=0.0,
            )

    # If no enabled system models found, raise a helpful error
    enabled_str = ", ".join(enabled_providers)
    raise ValueError(
        f"No default LLM available for enabled providers ({enabled_str}). "
        f"Please check your configuration or add system default models."
    )


def invoke_llm(llm, prompt, variables=None):
    """
    Unified function to invoke either a ReplicateWrapper or LangChain LLM.
    - llm: The LLM instance.
    - prompt: Either a string (for Replicate) or a LangChain ChatPromptTemplate.
    - variables: dict of variables for the prompt (for LangChain).
    Returns the response content as a string.
    """
    # ReplicateWrapper: expects a formatted string prompt (already has retry logic)
    if hasattr(llm, "__class__") and "ReplicateWrapper" in llm.__class__.__name__:
        if variables:
            prompt_text = prompt.format(**variables)
        else:
            prompt_text = prompt
        # Route through rate limiter for consistency
        from app.services.universal_llm_wrapper import execute_llm_request_safely_sync

        return execute_llm_request_safely_sync(llm, prompt_text, model_name="replicate")

    # BedrockWrapper: already has retry logic
    elif hasattr(llm, "__class__") and "BedrockWrapper" in llm.__class__.__name__:
        if variables:
            prompt_text = (
                prompt.format(**variables) if isinstance(prompt, str) else prompt
            )
        else:
            prompt_text = prompt
        # Route through rate limiter for consistency
        from app.services.universal_llm_wrapper import execute_llm_request_safely_sync

        return execute_llm_request_safely_sync(llm, prompt_text, model_name="bedrock")

    else:
        # LangChain models: add retry logic based on model type
        if variables is None:
            variables = {}

        # Determine if this is an OpenAI model and add appropriate retry logic
        model_class_name = llm.__class__.__name__

        def _invoke_langchain_model():
            # Prepare the text content for token estimation
            if hasattr(prompt, "from_template"):
                formatted_text = (
                    prompt.template.format(**variables)
                    if variables
                    else prompt.template
                )
            elif hasattr(prompt, "format_prompt"):
                # For ChatPromptTemplate, get the text content
                formatted_text = (
                    str(prompt.format_prompt(**variables)) if variables else str(prompt)
                )
            elif isinstance(prompt, str):
                formatted_text = prompt.format(**variables) if variables else prompt
            else:
                formatted_text = str(prompt)

            # For OpenAI models, apply global rate limiting
            if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
                # Estimate tokens needed for this request
                estimated_tokens = estimate_tokens(formatted_text)

                # Wait for capacity if needed
                from app.core.config import settings

                if not global_rate_limiter.wait_for_capacity(
                    estimated_tokens, max_wait_time=settings.OPENAI_RATE_LIMIT_MAX_WAIT
                ):
                    raise Exception(
                        "Global rate limiter: Maximum wait time exceeded for OpenAI request"
                    )

                logger.info(
                    f"🚀 Proceeding with OpenAI request ({estimated_tokens} estimated tokens)"
                )

            # Execute the actual LLM invocation
            if hasattr(prompt, "from_template"):
                # If prompt is a template, build the chain
                section_prompt = prompt.from_template(prompt.template)
                chain = section_prompt | llm
                result = chain.invoke(variables)
            elif hasattr(prompt, "format_prompt"):
                # If prompt is already a ChatPromptTemplate
                chain = prompt | llm
                result = chain.invoke(variables)
            elif isinstance(prompt, str):
                # Create a proper chat message from the string
                formatted_text = prompt.format(**variables)
                try:
                    from langchain_core.messages import HumanMessage
                except ImportError:
                    from langchain.schema import HumanMessage
                # Route through rate limiter
                from app.services.universal_llm_wrapper import (
                    execute_llm_request_safely_sync,
                )

                result = execute_llm_request_safely_sync(
                    llm,
                    [HumanMessage(content=formatted_text)],
                    model_name=getattr(llm, "model_name", "gpt-4o"),
                )
            else:
                # If prompt is a plain string, just pass as-is
                result = llm(prompt)

            # For OpenAI models, record actual token usage if available
            if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
                try:
                    if hasattr(result, "usage_metadata") and result.usage_metadata:
                        actual_tokens = result.usage_metadata.get(
                            "total_tokens", estimated_tokens
                        )
                        global_rate_limiter.record_actual_usage(
                            actual_tokens, estimated_tokens
                        )
                        logger.debug(f"📊 Recorded actual token usage: {actual_tokens}")
                    elif (
                        hasattr(result, "response_metadata")
                        and result.response_metadata
                    ):
                        # Try alternative metadata location
                        usage = result.response_metadata.get("token_usage", {})
                        actual_tokens = usage.get("total_tokens", estimated_tokens)
                        global_rate_limiter.record_actual_usage(
                            actual_tokens, estimated_tokens
                        )
                        logger.debug(f"📊 Recorded actual token usage: {actual_tokens}")
                except Exception as e:
                    logger.debug(f"Could not extract actual token usage: {e}")

            # Extract content from message object if needed
            if hasattr(result, "content"):
                return result.content
            return result

        # Apply appropriate retry logic based on model type
        if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
            # Apply aggressive OpenAI retry logic with exponential backoff
            return retry_openai_api(min_wait=10, max_wait=300, max_attempts=7)(
                _invoke_langchain_model
            )()
        elif "ChatBedrock" in model_class_name or "Bedrock" in model_class_name:
            # Apply AWS retry logic
            return retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)(
                _invoke_langchain_model
            )()
        else:
            # For other models (like Ollama), no retry logic needed
            return _invoke_langchain_model()


async def invoke_llm_async(llm, prompt, variables=None):
    """
    Async version of invoke_llm that doesn't block the event loop.
    Unified function to invoke either a ReplicateWrapper or LangChain LLM.
    - llm: The LLM instance.
    - prompt: Either a string (for Replicate) or a LangChain ChatPromptTemplate.
    - variables: dict of variables for the prompt (for LangChain).
    Returns the response content as a string.
    """
    # ReplicateWrapper: expects a formatted string prompt
    if hasattr(llm, "__class__") and "ReplicateWrapper" in llm.__class__.__name__:
        if variables:
            prompt_text = prompt.format(**variables)
        else:
            prompt_text = prompt
        # Route through rate limiter for consistency
        from app.services.universal_llm_wrapper import execute_llm_request_safely

        result = await execute_llm_request_safely(
            llm, prompt_text, model_name="replicate"
        )
        return result

    # BedrockWrapper: already has retry logic
    elif hasattr(llm, "__class__") and "BedrockWrapper" in llm.__class__.__name__:
        if variables:
            prompt_text = (
                prompt.format(**variables) if isinstance(prompt, str) else prompt
            )
        else:
            prompt_text = prompt
        # Route through rate limiter for consistency
        from app.services.universal_llm_wrapper import execute_llm_request_safely

        result = await execute_llm_request_safely(
            llm, prompt_text, model_name="bedrock"
        )
        return result

    else:
        # LangChain models: add retry logic based on model type
        if variables is None:
            variables = {}

        # Determine if this is an OpenAI model and add appropriate retry logic
        model_class_name = llm.__class__.__name__

        async def _invoke_langchain_model_async():
            # Prepare the text content for token estimation
            if hasattr(prompt, "from_template"):
                formatted_text = (
                    prompt.template.format(**variables)
                    if variables
                    else prompt.template
                )
            elif hasattr(prompt, "format_prompt"):
                # For ChatPromptTemplate, get the text content
                formatted_text = (
                    str(prompt.format_prompt(**variables)) if variables else str(prompt)
                )
            elif isinstance(prompt, str):
                formatted_text = prompt.format(**variables) if variables else prompt
            else:
                formatted_text = str(prompt)

            # For OpenAI models, apply global rate limiting
            if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
                # Estimate tokens needed for this request
                estimated_tokens = estimate_tokens(formatted_text)

                # Wait for capacity if needed
                from app.core.config import settings

                if not global_rate_limiter.wait_for_capacity(
                    estimated_tokens, max_wait_time=settings.OPENAI_RATE_LIMIT_MAX_WAIT
                ):
                    raise Exception(
                        "Global rate limiter: Maximum wait time exceeded for OpenAI request"
                    )

                logger.info(
                    f"🚀 Proceeding with OpenAI request ({estimated_tokens} estimated tokens)"
                )

            # Execute the actual LLM invocation
            if hasattr(prompt, "from_template"):
                # If prompt is a template, build the chain
                section_prompt = prompt.from_template(prompt.template)
                chain = section_prompt | llm
                result = await chain.ainvoke(variables)
            elif hasattr(prompt, "format_prompt"):
                # If prompt is already a ChatPromptTemplate
                chain = prompt | llm
                result = await chain.ainvoke(variables)
            elif isinstance(prompt, str):
                # Create a proper chat message from the string
                formatted_text = prompt.format(**variables)
                try:
                    from langchain_core.messages import HumanMessage
                except ImportError:
                    from langchain.schema import HumanMessage
                # Route through rate limiter
                from app.services.universal_llm_wrapper import (
                    execute_llm_request_safely,
                )

                result = await execute_llm_request_safely(
                    llm,
                    [HumanMessage(content=formatted_text)],
                    model_name=getattr(llm, "model_name", "gpt-4o"),
                )
            else:
                # If prompt is a plain string, just pass as-is
                # For async, we need to run in executor
                import asyncio

                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: llm(prompt)
                )

            # For OpenAI models, record actual token usage if available
            if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
                try:
                    if hasattr(result, "usage_metadata") and result.usage_metadata:
                        actual_tokens = result.usage_metadata.get(
                            "total_tokens", estimated_tokens
                        )
                        global_rate_limiter.record_actual_usage(
                            actual_tokens, estimated_tokens
                        )
                        logger.debug(f"📊 Recorded actual token usage: {actual_tokens}")
                    elif (
                        hasattr(result, "response_metadata")
                        and result.response_metadata
                    ):
                        # Try alternative metadata location
                        usage = result.response_metadata.get("token_usage", {})
                        actual_tokens = usage.get("total_tokens", estimated_tokens)
                        global_rate_limiter.record_actual_usage(
                            actual_tokens, estimated_tokens
                        )
                        logger.debug(f"📊 Recorded actual token usage: {actual_tokens}")
                except Exception as e:
                    logger.debug(f"Could not extract actual token usage: {e}")

            # Extract content from message object if needed
            if hasattr(result, "content"):
                return result.content
            return result

        # Apply appropriate retry logic based on model type
        if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
            # Apply aggressive OpenAI retry logic with exponential backoff
            return await retry_openai_api(min_wait=10, max_wait=300, max_attempts=7)(
                _invoke_langchain_model_async
            )()
        elif "ChatBedrock" in model_class_name or "Bedrock" in model_class_name:
            # Apply AWS retry logic
            return await retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)(
                _invoke_langchain_model_async
            )()
        else:
            # For other models (like Ollama), no retry logic needed
            return await _invoke_langchain_model_async()


def invoke_llm_with_image(
    llm, prompt, variables=None, image_file=None, image_base64=None, image_type="png"
):
    """
    Unified function to invoke an LLM with an image (for multimodal models).
    """
    # First, prepare the text content properly
    if variables is None:
        variables = {}

    # Validate base64 image if provided
    if image_base64:
        logger.debug(
            f"Starting base64 validation for single image in invoke_llm_with_image (length: {len(image_base64)})"
        )
        try:
            base64.b64decode(image_base64, validate=True)
        except Exception as e:
            logger.warning(
                f"BASE64 VALIDATION ERROR: Invalid base64 image data in invoke_llm_with_image. "
                f"Error: {str(e)}. Image processing will be skipped. "
                f"Image data length: {len(image_base64) if image_base64 else 0} characters."
            )
            image_base64 = None

    # Format the text content based on prompt type and variables
    if isinstance(prompt, str):
        text_content = prompt.format(**variables) if variables else prompt
    else:
        text_content = str(prompt)

    # For Replicate models, use their API directly
    if hasattr(llm, "__class__") and "ReplicateWrapper" in llm.__class__.__name__:
        print("Using ReplicateWrapper for multimodal LLM invocation")

        # For Replicate, we can't easily use images, so warn and fall back
        print(
            "WARNING: Replicate models may not support image processing in the same way"
        )
        print("Using Replicate model for image extraction - text-only fallback")

        # Fall back to text-only prompt without the image
        prompt_text = f"""Here is a template of the fields that I want you to extract: {variables.get('template', {})}
        
        NOTE: This was supposed to be an image file with handwritten content, but I'm using a text-only model.
        If you cannot process images, please respond with 'Cannot process image content'."""

        try:
            # Route through rate limiter
            from app.services.universal_llm_wrapper import (
                execute_llm_request_safely_sync,
            )

            response_text = execute_llm_request_safely_sync(
                llm, prompt_text, model_name="replicate"
            )
            return response_text
        except Exception as e:
            print(f"Error with Replicate image extraction: {e}")
            return f"Error processing image with Replicate: {str(e)}"

    # For LangChain models that support images
    else:
        print("Using LangChain-based LLM for multimodal invocation")

        def _invoke_multimodal_langchain():
            print("Using LangChain model for image extraction")

            # If we were given a template string, use it directly
            if isinstance(prompt, str) and prompt:
                # Create a prompt template from the string
                prompt_template = ChatPromptTemplate.from_template(prompt)
                # Format it with variables
                formatted_prompt = prompt_template.format_prompt(**variables)
                # Get messages
                messages = formatted_prompt.to_messages()
            else:
                # Create a basic message about the image
                messages = [HumanMessage(content=text_content)]

            # Add the image to the first message's content
            if messages and isinstance(messages[0].content, str):
                # Convert to multimodal format
                content_parts = [
                    {"type": "text", "text": messages[0].content},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_type};base64,{image_base64}"
                        },
                    },
                ]

                messages[0].content = content_parts

            print("Messages defined, proceeding to invoke LLM with image...")

            # Call the LLM with image capability through rate limiter
            from app.services.universal_llm_wrapper import (
                execute_llm_request_safely_sync,
            )

            response = execute_llm_request_safely_sync(
                llm,
                messages,
                images=[image_base64] if image_base64 else None,
                model_name=getattr(llm, "model_name", "gpt-4o"),
            )

            print("Raw response from LangChain:", response)

            # Extract content from the response object
            if hasattr(response, "content"):
                return response.content

            # Otherwise return the string representation
            return str(response)

        try:
            # Apply appropriate retry logic based on model type
            model_class_name = llm.__class__.__name__

            if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
                # Apply aggressive OpenAI retry logic with exponential backoff
                return retry_openai_api(min_wait=10, max_wait=300, max_attempts=7)(
                    _invoke_multimodal_langchain
                )()
            elif "ChatBedrock" in model_class_name or "Bedrock" in model_class_name:
                # Apply AWS retry logic
                return retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)(
                    _invoke_multimodal_langchain
                )()
            else:
                # For other models, no retry logic needed
                return _invoke_multimodal_langchain()

            # Extract content from the response object
            if hasattr(response, "content"):
                return response.content

            # Otherwise return the string representation
            return str(response)

        except Exception as e:
            print(f"Error using LangChain for image: {str(e)}")
            print(traceback.format_exc())
            return f"Error processing image: {str(e)}"


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
    print(f"[DEBUG] record_llm_interaction called with functionality: {functionality}")
    print(f"[DEBUG] user_id: {user_id}")
    # print(f"[DEBUG] metadata: {metadata}")
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

    user = session.get(User, user_id)
    if user and user.default_llm:
        model = session.get(LlmModel, user.default_llm)
        if model:
            llm_model_id = model.model_id
            llm_provider = model.provider.value

            # Add LLM info to metadata
            if llm_model_id:
                metadata["llm_model_id"] = llm_model_id
            if llm_provider:
                metadata["llm_provider"] = llm_provider

    # Create and save interaction record
    interaction = LlmInteraction(
        user_id=user_id,
        functionality=functionality,
        input_data=input_data,
        output_data=output_data,
        extra_data=metadata,
    )

    print(f"[DEBUG] Created interaction object with id: {interaction.id}")
    session.add(interaction)
    session.commit()
    print(f"[DEBUG] Interaction saved successfully with id: {interaction.id}")
    return interaction.id


def invoke_llm_with_images(llm, prompt, variables=None, images_list=None):
    """
    Enhanced function to invoke an LLM with multiple images (for multimodal models).

    Args:
        llm: The LLM instance to use
        prompt: The prompt template string
        variables: Dictionary of variables to substitute in the prompt
        images_list: List of base64-encoded images

    Returns:
        The LLM response content
    """
    from langchain_core.messages import HumanMessage
    from langchain.prompts import ChatPromptTemplate
    import traceback

    # First, prepare the text content properly
    if variables is None:
        variables = {}

    if images_list is None:
        images_list = []

    # Validate base64 images and filter out invalid ones
    if images_list:
        logger.debug(
            f"Starting base64 validation for {len(images_list)} images in invoke_llm_with_images"
        )

    valid_images = []
    invalid_count = 0
    for i, image_b64 in enumerate(images_list):
        try:
            base64.b64decode(image_b64, validate=True)
            valid_images.append(image_b64)
        except Exception as e:
            invalid_count += 1
            logger.warning(
                f"BASE64 VALIDATION ERROR: Invalid base64 image at index {i} in invoke_llm_with_images. "
                f"Error: {str(e)}. This image will be skipped. "
                f"Image data length: {len(image_b64) if image_b64 else 0} characters."
            )

    if invalid_count > 0:
        logger.info(
            f"BASE64 VALIDATION SUMMARY: Filtered out {invalid_count} invalid images. "
            f"Processing {len(valid_images)} valid images out of {len(images_list)} total."
        )

    images_list = valid_images

    # Downsample images to reduce token usage and processing time
    if images_list:
        logger.debug(f"Starting image downsampling for {len(images_list)} images")
        downsampled_images = []
        for i, image_b64 in enumerate(images_list):
            try:
                downsampled = downsample_image_base64(image_b64)
                downsampled_images.append(downsampled)
                # Log if image was actually downsampled (size difference indicates change)
                if (
                    len(downsampled) < len(image_b64) * 0.9
                ):  # 10% size reduction threshold
                    logger.debug(
                        f"Image {i} was downsampled (size reduced from {len(image_b64)} to {len(downsampled)} chars)"
                    )
            except Exception as e:
                logger.warning(f"Failed to downsample image {i}: {e}, using original")
                downsampled_images.append(image_b64)

        images_list = downsampled_images
        logger.debug(
            f"Completed image downsampling, processing {len(images_list)} images"
        )

    # Format the text content based on prompt type and variables
    if isinstance(prompt, str):
        text_content = prompt.format(**variables) if variables else prompt
    else:
        text_content = str(prompt)

    # For Replicate models, use fallback to text-only
    if hasattr(llm, "__class__") and "ReplicateWrapper" in llm.__class__.__name__:
        print("Using ReplicateWrapper for multimodal LLM invocation")
        print("WARNING: Replicate models may not support multiple image processing")

        # Fall back to text-only prompt
        try:
            # Route through rate limiter
            from app.services.universal_llm_wrapper import (
                execute_llm_request_safely_sync,
            )

            response_text = execute_llm_request_safely_sync(
                llm, text_content, model_name="replicate"
            )
            return response_text
        except Exception as e:
            print(f"Error with Replicate image extraction: {e}")
            return f"Error processing images with Replicate: {str(e)}"

    # For LangChain models that support images
    else:
        print(
            f"Using LangChain-based LLM for multimodal invocation with {len(images_list)} images"
        )

        def _invoke_multimodal_langchain_multiple():
            # Create the message content with text and multiple images
            content_parts = [{"type": "text", "text": text_content}]

            # Add each image to the content
            for i, image_b64 in enumerate(images_list):
                content_parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    }
                )

            # Create the message
            try:
                from langchain_core.messages import HumanMessage
            except ImportError:
                from langchain.schema import HumanMessage

            message = HumanMessage(content=content_parts)

            print(
                f"Invoking LLM with {len(content_parts)} content parts (1 text + {len(images_list)} images)"
            )

            # Call the LLM with image capability through rate limiter
            from app.services.universal_llm_wrapper import (
                execute_llm_request_safely_sync,
            )

            response = execute_llm_request_safely_sync(
                llm,
                [message],
                images=images_list,
                model_name=getattr(llm, "model_name", "gpt-4o"),
            )

            print("Successfully received response from multimodal LLM")

            # Extract content from the response object
            if hasattr(response, "content"):
                return response.content

            # Otherwise return the string representation
            return str(response)

        try:
            # Apply appropriate retry logic based on model type
            model_class_name = llm.__class__.__name__

            if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
                # Apply aggressive OpenAI retry logic with exponential backoff
                return retry_openai_api(min_wait=10, max_wait=300, max_attempts=7)(
                    _invoke_multimodal_langchain_multiple
                )()
            elif "ChatBedrock" in model_class_name or "Bedrock" in model_class_name:
                # Apply AWS retry logic
                return retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)(
                    _invoke_multimodal_langchain_multiple
                )()
            else:
                # For other models, no retry logic needed
                return _invoke_multimodal_langchain_multiple()

        except Exception as e:
            print(f"Error using LangChain for multiple images: {str(e)}")
            print(traceback.format_exc())
            return f"Error processing multiple images: {str(e)}"
