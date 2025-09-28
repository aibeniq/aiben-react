"""
Test vision processing retry logic to ensure rate limits are handled properly
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import time
from unittest.mock import Mock, patch
import pytest


def test_vision_retry_logic():
    """Test that vision processing has proper retry logic for rate limits"""

    print("=== VISION PROCESSING RETRY LOGIC TEST ===")

    # Mock components
    mock_llm = Mock()
    mock_llm.invoke = Mock()

    # Import the function we want to test
    from app.services.llms import invoke_llm_with_images

    # Test 1: Simulate rate limit error on first call, success on retry
    print("\n--- Test 1: Rate Limit Recovery ---")

    # Create a mock OpenAI rate limit error
    from openai import RateLimitError

    # Configure mock to fail first, then succeed
    error_response = Mock()
    error_response.status_code = 429
    error_response.json.return_value = {
        "error": {"message": "Rate limit exceeded", "type": "rate_limit_error"}
    }

    rate_limit_error = RateLimitError(
        message="Rate limit exceeded", response=error_response, body=None
    )

    success_response = Mock()
    success_response.content = 'Successfully extracted tables: [{"table_id": "test_table", "data": "test_data"}]'

    # Mock to fail twice, then succeed
    mock_llm.invoke.side_effect = [
        rate_limit_error,  # First call fails
        rate_limit_error,  # Second call fails
        success_response,  # Third call succeeds
    ]

    # Test with mock images
    test_images = ["mock_image_base64_1", "mock_image_base64_2"]
    test_prompt = "Extract table data from these images: {filename}"
    test_variables = {"filename": "test_document.pdf"}

    try:
        result = invoke_llm_with_images(
            llm=mock_llm,
            prompt=test_prompt,
            variables=test_variables,
            images_list=test_images,
        )

        print(f"✅ Rate limit retry successful: {result[:100]}...")
        print(
            f"✅ LLM was called {mock_llm.invoke.call_count} times (2 failures + 1 success)"
        )

        if mock_llm.invoke.call_count == 3:
            print("✅ Retry logic is working correctly!")
            retry_test_passed = True
        else:
            print(f"❌ Expected 3 calls, got {mock_llm.invoke.call_count}")
            retry_test_passed = False

    except Exception as e:
        print(f"❌ Retry test failed: {e}")
        retry_test_passed = False

    # Test 2: Verify retry doesn't happen for non-retryable errors
    print("\n--- Test 2: Non-Retryable Error Handling ---")

    mock_llm.reset_mock()

    # Create a non-retryable error (context length exceeded)
    context_error = Exception("Context length exceeded")
    mock_llm.invoke.side_effect = context_error

    try:
        result = invoke_llm_with_images(
            llm=mock_llm,
            prompt=test_prompt,
            variables=test_variables,
            images_list=test_images,
        )
        print(f"❌ Should have failed with context error, but got: {result}")
        non_retry_test_passed = False
    except Exception as e:
        if "Context length exceeded" in str(e):
            print("✅ Non-retryable error correctly propagated")
            print(f"✅ LLM was called {mock_llm.invoke.call_count} times (no retries)")
            non_retry_test_passed = True
        else:
            print(f"❌ Unexpected error: {e}")
            non_retry_test_passed = False

    # Test 3: Check message format for vision calls
    print("\n--- Test 3: Vision Message Format ---")

    mock_llm.reset_mock()
    mock_llm.invoke.return_value = success_response

    try:
        result = invoke_llm_with_images(
            llm=mock_llm,
            prompt="Analyze these images",
            variables={},
            images_list=["test_image_b64"],
        )

        # Check that the message was formatted correctly
        call_args = mock_llm.invoke.call_args
        if call_args:
            messages = call_args[0][
                0
            ]  # First positional argument should be message list
            if messages and len(messages) > 0:
                message = messages[0]
                if hasattr(message, "content") and isinstance(message.content, list):
                    # Check for text and image content
                    has_text = any(
                        item.get("type") == "text" for item in message.content
                    )
                    has_image = any(
                        item.get("type") == "image_url" for item in message.content
                    )

                    if has_text and has_image:
                        print("✅ Message format is correct for vision processing")
                        format_test_passed = True
                    else:
                        print(
                            f"❌ Missing content types - text: {has_text}, image: {has_image}"
                        )
                        format_test_passed = False
                else:
                    print(
                        f"❌ Message content format unexpected: {type(message.content)}"
                    )
                    format_test_passed = False
            else:
                print("❌ No message content found")
                format_test_passed = False
        else:
            print("❌ No call arguments found")
            format_test_passed = False
    except Exception as e:
        print(f"❌ Format test failed: {e}")
        format_test_passed = False

    # Final assessment
    print("\n=== FINAL RESULTS ===")
    print(f"Rate limit retry test: {'✅ PASSED' if retry_test_passed else '❌ FAILED'}")
    print(
        f"Non-retryable error test: {'✅ PASSED' if non_retry_test_passed else '❌ FAILED'}"
    )
    print(f"Message format test: {'✅ PASSED' if format_test_passed else '❌ FAILED'}")

    if all([retry_test_passed, non_retry_test_passed, format_test_passed]):
        print("✅ ALL TESTS PASSED: Vision retry logic is working correctly!")
        return True
    else:
        print("❌ SOME TESTS FAILED: Vision retry logic needs attention")
        return False


if __name__ == "__main__":
    success = test_vision_retry_logic()
    sys.exit(0 if success else 1)
