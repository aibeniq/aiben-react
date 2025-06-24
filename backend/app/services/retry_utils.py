"""
Retry utilities with exponential backoff for API calls.
Implements Tenacity decorators for handling rate limits and transient errors.

Example Usage:

1. OpenAI API calls:

    @retry_openai_api(min_wait=5, max_wait=120, max_attempts=5)
    def completion_with_backoff(**kwargs):
        return client.completions.create(**kwargs)

    # Use it:
    completion_with_backoff(model="gpt-4o-mini", prompt="Once upon a time,")

2. AWS API calls:

    @retry_aws_api(min_wait=2, max_wait=60, max_attempts=8)
    def get_bedrock_response(bedrock_client, model_id, prompt):
        return bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps({"prompt": prompt, "temperature": 0.0})
        )

3. Replicate API calls:

    @retry_replicate_api(min_wait=3, max_wait=90, max_attempts=6)
    def replicate_prediction(**kwargs):
        return replicate.run(model_id, input=kwargs)

4. Universal wrapper:

    @with_retries('openai')
    def my_openai_function():
        return openai_client.chat.completions.create(...)

    @with_retries('aws')
    def my_aws_function():
        return bedrock_client.invoke_model(...)
"""

import logging
import functools
import re
import time
from typing import Any, Callable, TypeVar

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    retry_if_exception_type,
    retry_if_exception,
    RetryCallState,
    before_sleep_log,
    after_log,
    wait_fixed,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# For OpenAI rate limiting and transient errors
import openai
from openai import (
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
)

# For AWS rate limiting and transient errors
import botocore.exceptions
from botocore.exceptions import ClientError, ConnectionError, EndpointConnectionError

# For Replicate rate limiting
import replicate
from replicate.exceptions import ReplicateError

# Generic function type for retry decorators
F = TypeVar("F", bound=Callable[..., Any])

# Specific exceptions that should trigger retries
OPENAI_RETRY_EXCEPTIONS = (
    RateLimitError,
    APITimeoutError,
    APIConnectionError,
    InternalServerError,
)
AWS_RETRY_EXCEPTIONS = (ClientError, ConnectionError, EndpointConnectionError)
REPLICATE_RETRY_EXCEPTIONS = (ReplicateError, ConnectionError, TimeoutError)


def extract_openai_wait_time(exception: Exception) -> float:
    """
    Extract the suggested wait time from OpenAI rate limit error messages.

    Example error message: 'Please try again in 39.466s'
    """
    try:
        error_message = str(exception)
        # Look for patterns like "try again in X.Xs" or "try again in Xms"

        # Pattern for seconds: "try again in 39.466s"
        seconds_match = re.search(r"try again in (\d+\.?\d*)s", error_message)
        if seconds_match:
            return float(seconds_match.group(1))

        # Pattern for milliseconds: "try again in 608ms"
        ms_match = re.search(r"try again in (\d+)ms", error_message)
        if ms_match:
            return float(ms_match.group(1)) / 1000.0

        # If no pattern found, return 0 to use default backoff
        return 0.0

    except Exception as e:
        logger.warning(f"Failed to extract wait time from error message: {e}")
        return 0.0


class OpenAIWaitStrategy:
    """
    Custom wait strategy that respects OpenAI's suggested wait times.
    Falls back to exponential backoff if no suggestion is provided.
    """

    def __init__(self, min_wait: int = 5, max_wait: int = 120, multiplier: int = 1):
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.multiplier = multiplier
        self.exponential_backoff = wait_random_exponential(
            multiplier=multiplier, min=min_wait, max=max_wait
        )

    def __call__(self, retry_state: RetryCallState) -> float:
        """Calculate wait time based on OpenAI suggestion or exponential backoff."""
        if retry_state.outcome and retry_state.outcome.failed:
            exception = retry_state.outcome.exception()

            # Check if this is an OpenAI RateLimitError with suggested wait time
            if isinstance(exception, RateLimitError):
                suggested_wait = extract_openai_wait_time(exception)
                if suggested_wait > 0:
                    # Add a small buffer (10%) to the suggested wait time
                    buffered_wait = suggested_wait * 1.1
                    logger.info(
                        f"🕒 OpenAI suggested wait time: {suggested_wait:.3f}s, "
                        f"using buffered time: {buffered_wait:.3f}s"
                    )
                    return buffered_wait

        # Fall back to exponential backoff for other errors or when no suggestion
        fallback_wait = self.exponential_backoff(retry_state)
        logger.info(f"🔄 Using exponential backoff: {fallback_wait:.3f}s")
        return fallback_wait


def log_before_sleep(retry_state: RetryCallState) -> None:
    """Custom logging function before sleep (exponential backoff)"""
    attempt_number = retry_state.attempt_number
    sleep_time = retry_state.next_action.sleep if retry_state.next_action else 0
    function_name = retry_state.fn.__name__

    if retry_state.outcome and retry_state.outcome.failed:
        exception = retry_state.outcome.exception()

        # Enhanced logging for OpenAI rate limits
        if isinstance(exception, RateLimitError):
            suggested_wait = extract_openai_wait_time(exception)
            if suggested_wait > 0:
                logger.warning(
                    f"⏰ OPENAI RATE LIMIT: OpenAI suggested {suggested_wait:.3f}s, "
                    f"waiting {sleep_time:.3f}s before retry #{attempt_number + 1} "
                    f"for function '{function_name}'"
                )
            else:
                logger.warning(
                    f"⏰ TENACITY BACKOFF: Sleeping for {sleep_time:.2f} seconds before retry #{attempt_number + 1} "
                    f"for function '{function_name}'. Last error: {type(exception).__name__}: {str(exception)}"
                )
        else:
            logger.warning(
                f"⏰ TENACITY BACKOFF: Sleeping for {sleep_time:.2f} seconds before retry #{attempt_number + 1} "
                f"for function '{function_name}'. Last error: {type(exception).__name__}: {str(exception)}"
            )


def log_after_attempt(retry_state: RetryCallState) -> None:
    """Custom logging function after each attempt"""
    attempt_number = retry_state.attempt_number
    function_name = retry_state.fn.__name__

    if retry_state.outcome:
        if retry_state.outcome.failed:
            exception = retry_state.outcome.exception()
            logger.info(
                f"❌ TENACITY: Attempt #{attempt_number} failed for '{function_name}': "
                f"{type(exception).__name__}: {str(exception)}"
            )
        else:
            logger.info(
                f"✅ TENACITY: Attempt #{attempt_number} succeeded for '{function_name}' after {attempt_number} attempts"
            )


def is_retryable_openai_error(exception: Exception) -> bool:
    """Check if OpenAI exception is retryable."""
    if isinstance(
        exception,
        (RateLimitError, APITimeoutError, APIConnectionError, InternalServerError),
    ):
        return True

    # Don't retry context length exceeded errors - they won't work without reducing input
    if isinstance(exception, Exception):
        error_message = str(exception).lower()
        if (
            "context length" in error_message
            or "maximum context length" in error_message
        ):
            logger.error(f"🚫 Context length exceeded - will not retry: {exception}")
            return False

    # Check for specific status codes that are retryable
    if hasattr(exception, "status_code"):
        # 429: Rate limit, 500-503: Server errors, 524: Timeout
        # But NOT 400: Bad Request (which includes context length errors)
        return exception.status_code in [429, 500, 502, 503, 524]
    return False


def is_retryable_aws_error(exception: Exception) -> bool:
    """Check if AWS exception is retryable."""
    if isinstance(exception, (ConnectionError, EndpointConnectionError)):
        return True

    if isinstance(exception, ClientError):
        error_code = exception.response.get("Error", {}).get("Code", "")
        # Throttling, service unavailable, and internal errors are retryable
        retryable_codes = [
            "Throttling",
            "ThrottledException",
            "ProvisionedThroughputExceededException",
            "ServiceUnavailable",
            "InternalError",
            "InternalFailure",
            "ServiceException",
        ]
        return error_code in retryable_codes

    return False


def is_retryable_replicate_error(exception: Exception) -> bool:
    """Check if Replicate exception is retryable."""
    if isinstance(exception, ReplicateError):
        # Check if it's a rate limit or server error
        error_message = str(exception).lower()
        return any(
            keyword in error_message
            for keyword in [
                "rate limit",
                "throttle",
                "too many requests",
                "server error",
                "internal error",
                "timeout",
            ]
        )
    return False


def retry_openai_api(
    min_wait: int = 5,  # Increased minimum wait to avoid overwhelming API
    max_wait: int = 180,  # Increased to handle longer OpenAI suggested waits
    max_attempts: int = 5,  # Reduced max attempts to prevent runaway retries
) -> Callable[[F], F]:
    """
    Decorator for OpenAI API calls with intelligent wait strategy that respects OpenAI's suggested wait times.
    Enhanced to handle context length errors appropriately.

    Args:
        min_wait: Minimum wait time in seconds (default: 5)
        max_wait: Maximum wait time in seconds (default: 180)
        max_attempts: Maximum number of retry attempts (default: 5)

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: F) -> F:
        @retry(
            wait=OpenAIWaitStrategy(min_wait=min_wait, max_wait=max_wait),
            stop=stop_after_attempt(max_attempts),
            retry=retry_if_exception(is_retryable_openai_error),
            before_sleep=log_before_sleep,
            after=log_after_attempt,
            reraise=True,
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"🚀 TENACITY: Calling OpenAI API function: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"✅ TENACITY: OpenAI API call successful: {func.__name__}")
                return result
            except Exception as e:
                # Enhanced error logging with more details
                error_type = type(e).__name__
                error_message = str(e)

                # Safely extract error details for logging
                if hasattr(e, "response") and e.response:
                    try:
                        response_json = (
                            e.response.json() if hasattr(e.response, "json") else {}
                        )
                        if "error" in response_json:
                            error_details = response_json["error"]
                            logger.error(
                                f"💥 TENACITY: OpenAI API call failed: {func.__name__} - "
                                f"{error_type}: {error_details.get('message', error_message)}"
                            )
                        else:
                            logger.error(
                                f"💥 TENACITY: OpenAI API call failed: {func.__name__} - "
                                f"{error_type}: {error_message}"
                            )
                    except Exception:
                        # Fallback for error parsing issues
                        logger.error(
                            f"💥 TENACITY: OpenAI API call failed: {func.__name__} - "
                            f"{error_type}: {error_message}"
                        )
                else:
                    logger.error(
                        f"💥 TENACITY: OpenAI API call failed: {func.__name__} - "
                        f"{error_type}: {error_message}"
                    )
                raise

        return wrapper

    return decorator


def retry_aws_api(
    min_wait: int = 2, max_wait: int = 60, max_attempts: int = 8
) -> Callable[[F], F]:
    """
    Decorator for AWS API calls with exponential backoff and enhanced logging.

    Args:
        min_wait: Minimum wait time in seconds (default: 2)
        max_wait: Maximum wait time in seconds (default: 60)
        max_attempts: Maximum number of retry attempts (default: 8)

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: F) -> F:
        @retry(
            wait=wait_random_exponential(multiplier=1, min=min_wait, max=max_wait),
            stop=stop_after_attempt(max_attempts),
            retry=retry_if_exception_type(AWS_RETRY_EXCEPTIONS),
            before_sleep=log_before_sleep,
            after=log_after_attempt,
            reraise=True,
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"🚀 TENACITY: Calling AWS API function: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"✅ TENACITY: AWS API call successful: {func.__name__}")
                return result
            except Exception as e:
                logger.error(
                    f"💥 TENACITY: AWS API call failed: {func.__name__} - {type(e).__name__}: {str(e)}"
                )
                raise

        return wrapper

    return decorator


def retry_replicate_api(
    min_wait: int = 3, max_wait: int = 90, max_attempts: int = 6
) -> Callable[[F], F]:
    """
    Decorator for Replicate API calls with exponential backoff and enhanced logging.

    Args:
        min_wait: Minimum wait time in seconds (default: 3)
        max_wait: Maximum wait time in seconds (default: 90)
        max_attempts: Maximum number of retry attempts (default: 6)

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: F) -> F:
        @retry(
            wait=wait_random_exponential(min=min_wait, max=max_wait),
            stop=stop_after_attempt(max_attempts),
            retry=retry_if_exception_type(REPLICATE_RETRY_EXCEPTIONS),
            before_sleep=log_before_sleep,
            after=log_after_attempt,
            reraise=True,
        )
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"🚀 TENACITY: Calling Replicate API function: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(
                    f"✅ TENACITY: Replicate API call successful: {func.__name__}"
                )
                return result
            except Exception as e:
                logger.error(
                    f"💥 TENACITY: Replicate API call failed: {func.__name__} - {type(e).__name__}: {str(e)}"
                )
                raise

        return wrapper

    return decorator


def with_retries(
    provider: str, min_wait: int = 2, max_wait: int = 60, max_attempts: int = 5
) -> Callable[[F], F]:
    """
    Universal retry decorator that chooses the appropriate retry strategy based on provider.
    Enhanced with better logging and conservative retry settings.

    Args:
        provider: API provider ('openai', 'aws', 'replicate')
        min_wait: Minimum wait time in seconds (default: 2)
        max_wait: Maximum wait time in seconds (default: 60)
        max_attempts: Maximum number of retry attempts (default: 5)

    Returns:
        Decorated function with provider-specific retry logic
    """
    provider = provider.lower()

    if provider == "openai":
        return retry_openai_api(
            min_wait=min_wait, max_wait=max_wait, max_attempts=max_attempts
        )
    elif provider == "aws":
        return retry_aws_api(
            min_wait=min_wait, max_wait=max_wait, max_attempts=max_attempts
        )
    elif provider == "replicate":
        return retry_replicate_api(
            min_wait=min_wait, max_wait=max_wait, max_attempts=max_attempts
        )
    else:
        # Default generic retry for unknown providers with enhanced logging
        def decorator(func: F) -> F:
            @retry(
                wait=wait_random_exponential(min=min_wait, max=max_wait),
                stop=stop_after_attempt(max_attempts),
                before_sleep=log_before_sleep,
                after=log_after_attempt,
                reraise=True,
            )
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(
                    f"🚀 TENACITY: Calling {provider.upper()} API function: {func.__name__}"
                )
                try:
                    result = func(*args, **kwargs)
                    logger.info(
                        f"✅ TENACITY: {provider.upper()} API call successful: {func.__name__}"
                    )
                    return result
                except Exception as e:
                    logger.error(
                        f"💥 TENACITY: {provider.upper()} API call failed: {func.__name__} - {type(e).__name__}: {str(e)}"
                    )
                    raise

            return wrapper

        return decorator


# Legacy function removal - these are no longer needed with the new implementation
# Removed the old helper functions that were causing KeyError issues
