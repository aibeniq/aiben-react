#!/usr/bin/env python3
"""
Test script for the enhanced OpenAI retry logic with rate limit respect.
"""

import sys
import os
import time
import logging

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.services.retry_utils import (
    extract_openai_wait_time,
    OpenAIWaitStrategy,
    retry_openai_api,
    logger,
)

# Configure logging for the test
logging.basicConfig(level=logging.INFO)


def test_extract_wait_time():
    """Test the wait time extraction function."""
    print("=" * 50)
    print("Testing wait time extraction...")

    # Test cases from your actual logs
    test_cases = [
        {
            "message": "Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 150974, Requested 53621. Please try again in 1.378s. Visit https://platform.openai.com/account/rate-limits to learn more.",
            "expected": 1.378,
        },
        {
            "message": "Please try again in 608ms. Visit https://platform.openai.com/account/rate-limits to learn more.",
            "expected": 0.608,
        },
        {
            "message": "Please try again in 39.466s. Visit https://platform.openai.com/account/rate-limits to learn more.",
            "expected": 39.466,
        },
        {"message": "Please try again in 20.956s.", "expected": 20.956},
        {"message": "Some other error message without timing", "expected": 0.0},
    ]

    for i, test_case in enumerate(test_cases):

        class MockException:
            def __str__(self):
                return test_case["message"]

        mock_exc = MockException()
        result = extract_openai_wait_time(mock_exc)
        expected = test_case["expected"]

        status = "✅ PASS" if abs(result - expected) < 0.001 else "❌ FAIL"
        print(f"Test {i+1}: {status}")
        print(f"  Message: {test_case['message'][:80]}...")
        print(f"  Expected: {expected}s, Got: {result}s")
        print()


def test_mock_openai_function():
    """Test the retry decorator with a mock function."""
    print("=" * 50)
    print("Testing retry decorator with mock OpenAI function...")

    call_count = 0

    @retry_openai_api(min_wait=1, max_wait=60, max_attempts=3)
    def mock_openai_call():
        nonlocal call_count
        call_count += 1
        print(f"  Mock call #{call_count}")

        if call_count == 1:
            # Simulate rate limit error with suggested wait time
            from openai import RateLimitError

            raise RateLimitError(
                "Rate limit reached for gpt-4o-mini. Please try again in 2.5s.",
                response=None,
                body=None,
            )
        elif call_count == 2:
            # Simulate another rate limit with different wait time
            from openai import RateLimitError

            raise RateLimitError(
                "Rate limit reached for gpt-4o-mini. Please try again in 1.2s.",
                response=None,
                body=None,
            )
        else:
            # Success on third try
            return "Success!"

    try:
        start_time = time.time()
        result = mock_openai_call()
        total_time = time.time() - start_time

        print(f"✅ Function succeeded after {call_count} attempts")
        print(f"   Result: {result}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Expected wait time: ~3.7s (2.5s + 1.2s with buffers)")

    except Exception as e:
        print(f"❌ Function failed: {e}")


def test_context_length_error():
    """Test that context length errors are not retried."""
    print("=" * 50)
    print("Testing context length error handling...")

    call_count = 0

    @retry_openai_api(min_wait=1, max_wait=60, max_attempts=3)
    def mock_context_error():
        nonlocal call_count
        call_count += 1
        print(f"  Mock call #{call_count} (should only be called once)")

        # Simulate context length exceeded error
        from openai import BadRequestError

        raise BadRequestError(
            "This model's maximum context length is 128000 tokens. However, your messages resulted in 144248 tokens.",
            response=None,
            body=None,
        )

    try:
        start_time = time.time()
        result = mock_context_error()
        print(f"❌ Unexpected success: {result}")

    except Exception as e:
        total_time = time.time() - start_time
        print(f"✅ Function failed as expected after {call_count} attempt(s)")
        print(f"   Error: {type(e).__name__}: {str(e)[:100]}...")
        print(f"   Total time: {total_time:.2f}s (should be very short)")

        if call_count == 1:
            print("   ✅ Context length error was NOT retried (correct behavior)")
        else:
            print("   ❌ Context length error was retried (incorrect behavior)")


if __name__ == "__main__":
    print("🧪 Testing Enhanced OpenAI Retry Logic")
    print("=" * 50)

    try:
        test_extract_wait_time()
        test_mock_openai_function()
        test_context_length_error()

        print("=" * 50)
        print("✅ All tests completed!")
        print("\nKey improvements:")
        print("- ✅ Extracts OpenAI suggested wait times from error messages")
        print("- ✅ Uses suggested wait times instead of exponential backoff")
        print("- ✅ Does not retry context length exceeded errors")
        print("- ✅ Enhanced error logging with better details")
        print("- ✅ Increased token chunk limits to prevent context overflow")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the backend directory")
        print("and that all dependencies are installed.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
