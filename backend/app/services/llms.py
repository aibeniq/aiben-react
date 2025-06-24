import replicate
import os
from io import BytesIO
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
                request_timeout=30,  # Set reasonable timeout
                **params,
            )
        else:
            return ChatOpenAI(
                model=model_id,
                temperature=temperature,
                max_retries=0,  # Disable OpenAI's internal retries
                request_timeout=30,  # Set reasonable timeout
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
        return llm.invoke(prompt_text)

    # BedrockWrapper: already has retry logic
    elif hasattr(llm, "__class__") and "BedrockWrapper" in llm.__class__.__name__:
        if variables:
            prompt_text = (
                prompt.format(**variables) if isinstance(prompt, str) else prompt
            )
        else:
            prompt_text = prompt
        return llm.invoke(prompt_text)

    else:
        # LangChain models: add retry logic based on model type
        if variables is None:
            variables = {}

        # Determine if this is an OpenAI model and add appropriate retry logic
        model_class_name = llm.__class__.__name__

        def _invoke_langchain_model():
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
                result = llm.invoke([HumanMessage(content=formatted_text)])
            else:
                # If prompt is a plain string, just pass as-is
                result = llm(prompt)

            # Extract content from message object if needed
            if hasattr(result, "content"):
                return result.content
            return result

        # Apply appropriate retry logic based on model type
        if "ChatOpenAI" in model_class_name or "OpenAI" in model_class_name:
            # Apply OpenAI retry logic
            return retry_openai_api(min_wait=1, max_wait=60, max_attempts=6)(
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


def invoke_llm_with_image(
    llm, prompt, variables=None, image_file=None, image_base64=None, image_type="png"
):
    """
    Unified function to invoke an LLM with an image (for multimodal models).
    """
    # First, prepare the text content properly
    if variables is None:
        variables = {}

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
            response_text = llm.invoke(prompt_text)
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

            # Call the LLM with image capability using the newer invoke() method
            response = llm.invoke(messages)

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
                # Apply OpenAI retry logic
                return retry_openai_api(min_wait=1, max_wait=60, max_attempts=6)(
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

    session.add(interaction)
    session.commit()
    return interaction.id
