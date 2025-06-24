"""
Test examples for retry functionality with OpenAI and AWS APIs.
These examples demonstrate how to use the retry decorators.
"""

import os
from app.services.retry_utils import (
    retry_openai_api,
    retry_aws_api,
    retry_replicate_api,
    with_retries,
)


# Example 1: OpenAI API with retry (like the example you provided)
@retry_openai_api(min_wait=1, max_wait=60, max_attempts=6)
def completion_with_backoff(**kwargs):
    """Example OpenAI completion with exponential backoff."""
    from openai import OpenAI

    client = OpenAI()
    return client.completions.create(**kwargs)


# Example 2: AWS Bedrock API with retry (like the example you provided)
@retry_aws_api(min_wait=1, max_wait=30, max_attempts=10)
def get_bedrock_response(model_id, prompt):
    """Example AWS Bedrock call with exponential backoff."""
    import boto3
    import json

    bedrock_client = boto3.client(
        "bedrock-runtime", region_name=os.environ.get("AWS_REGION", "eu-north-1")
    )

    response = bedrock_client.invoke_model(
        modelId=model_id,
        body=json.dumps({"prompt": prompt, "temperature": 0.0, "max_tokens": 100}),
    )

    return response


# Example 3: Replicate API with retry
@retry_replicate_api(min_wait=1, max_wait=60, max_attempts=6)
def replicate_prediction_with_backoff(model_id, **input_params):
    """Example Replicate prediction with exponential backoff."""
    import replicate

    return replicate.run(model_id, input=input_params)


# Example 4: Using the universal decorator
@with_retries("openai", min_wait=2, max_wait=120, max_attempts=5)
def universal_openai_example(**kwargs):
    """Example using universal retry decorator for OpenAI."""
    from openai import OpenAI

    client = OpenAI()
    return client.chat.completions.create(**kwargs)


@with_retries("aws", min_wait=1, max_wait=20, max_attempts=8)
def universal_aws_example(model_id, prompt):
    """Example using universal retry decorator for AWS."""
    import boto3
    import json

    bedrock_client = boto3.client(
        "bedrock-runtime", region_name=os.environ.get("AWS_REGION", "eu-north-1")
    )

    response = bedrock_client.invoke_model(
        modelId=model_id,
        body=json.dumps({"prompt": prompt, "temperature": 0.0, "max_tokens": 100}),
    )

    return response


@with_retries("replicate")
def universal_replicate_example(model_id, **input_params):
    """Example using universal retry decorator for Replicate."""
    import replicate

    return replicate.run(model_id, input=input_params)


# Example 5: Manual retry pattern for custom error handling
def manual_retry_example():
    """Example of how to manually implement retry with custom logic."""
    from tenacity import retry, stop_after_attempt, wait_exponential

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def my_custom_api_call():
        # Your custom API call here
        pass

    return my_custom_api_call()


# Test functions to validate retry behavior
def test_openai_retry():
    """Test function to verify OpenAI retry behavior."""
    try:
        result = completion_with_backoff(
            model="gpt-4o-mini", prompt="Say hello", max_tokens=10
        )
        print("OpenAI retry test successful:", result)
        return True
    except Exception as e:
        print("OpenAI retry test failed:", str(e))
        return False


def test_aws_retry():
    """Test function to verify AWS retry behavior."""
    try:
        result = get_bedrock_response(
            "anthropic.claude-instant-v1", "Say hello in French"
        )
        print("AWS retry test successful:", result)
        return True
    except Exception as e:
        print("AWS retry test failed:", str(e))
        return False


def test_replicate_retry():
    """Test function to verify Replicate retry behavior."""
    try:
        result = replicate_prediction_with_backoff(
            "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
            prompt="Say hello",
        )
        print("Replicate retry test successful:", result)
        return True
    except Exception as e:
        print("Replicate retry test failed:", str(e))
        return False


if __name__ == "__main__":
    """Run basic tests to verify retry functionality."""
    print("Testing retry functionality...")

    # Note: These tests will only work if you have proper API keys set up
    print("1. Testing OpenAI retry...")
    test_openai_retry()

    print("2. Testing AWS retry...")
    test_aws_retry()

    print("3. Testing Replicate retry...")
    test_replicate_retry()

    print("Retry testing complete.")
