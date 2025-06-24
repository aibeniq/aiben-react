"""
Wrapper functions for external API calls with retry logic.
These functions provide a convenient way to wrap existing API calls with tenacity retry decorators.
"""

from typing import Any, Callable, TypeVar
from app.services.retry_utils import (
    retry_openai_api,
    retry_aws_api,
    retry_replicate_api,
)

# Type variables for generic wrapper functions
F = TypeVar("F", bound=Callable[..., Any])


def with_openai_retries(func: F) -> F:
    """
    Wrapper function that adds OpenAI retry logic to any function.

    Usage:
        @with_openai_retries
        def my_openai_function():
            return openai_client.chat.completions.create(...)

    Args:
        func: Function to wrap with retry logic

    Returns:
        Function decorated with OpenAI retry logic
    """
    return retry_openai_api(min_wait=1, max_wait=60, max_attempts=6)(func)


def with_aws_retries(func: F) -> F:
    """
    Wrapper function that adds AWS retry logic to any function.

    Usage:
        @with_aws_retries
        def my_aws_function():
            return bedrock_client.invoke_model(...)

    Args:
        func: Function to wrap with retry logic

    Returns:
        Function decorated with AWS retry logic
    """
    return retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)(func)


def with_replicate_retries(func: F) -> F:
    """
    Wrapper function that adds Replicate retry logic to any function.

    Usage:
        @with_replicate_retries
        def my_replicate_function():
            return replicate.run(model_id, input=...)

    Args:
        func: Function to wrap with retry logic

    Returns:
        Function decorated with Replicate retry logic
    """
    return retry_replicate_api(min_wait=1, max_wait=60, max_attempts=6)(func)


class OpenAIClientWrapper:
    """
    Wrapper class that adds retry logic to OpenAI client methods.

    Usage:
        client = OpenAIClientWrapper()
        response = client.chat.completions.create(...)
    """

    def __init__(self):
        from openai import OpenAI

        self._client = OpenAI(
            max_retries=0,  # Disable OpenAI's internal retries
            timeout=30,  # Set reasonable timeout
        )

    @property
    def chat(self):
        """Access to chat completions with retry logic."""
        return ChatWrapper(self._client.chat)

    @property
    def completions(self):
        """Access to completions with retry logic."""
        return CompletionsWrapper(self._client.completions)


class ChatWrapper:
    def __init__(self, chat_instance):
        self._chat = chat_instance
        self.completions = ChatCompletionsWrapper(self._chat.completions)


class ChatCompletionsWrapper:
    def __init__(self, completions_instance):
        self._completions = completions_instance

    @with_openai_retries
    def create(self, **kwargs):
        """Create chat completion with retry logic."""
        return self._completions.create(**kwargs)


class CompletionsWrapper:
    def __init__(self, completions_instance):
        self._completions = completions_instance

    @with_openai_retries
    def create(self, **kwargs):
        """Create completion with retry logic."""
        return self._completions.create(**kwargs)


# Example AWS Bedrock wrapper
class BedrockWrapper:
    """
    Wrapper class that adds retry logic to AWS Bedrock client.

    Usage:
        bedrock = BedrockWrapper()
        response = bedrock.invoke_model(modelId="...", body="...")
    """

    def __init__(self, region_name=None):
        import boto3

        self._client = boto3.client(
            "bedrock-runtime", region_name=region_name or "eu-north-1"
        )

    @with_aws_retries
    def invoke_model(self, **kwargs):
        """Invoke model with retry logic."""
        return self._client.invoke_model(**kwargs)


# Example Replicate wrapper
class ReplicateWrapper:
    """
    Wrapper class that adds retry logic to Replicate API calls.

    Usage:
        wrapper = ReplicateWrapper()
        result = wrapper.run(model_id, input={...})
    """

    @with_replicate_retries
    def run(self, model_id, input=None):
        """Run prediction with retry logic."""
        import replicate

        return replicate.run(model_id, input=input)
