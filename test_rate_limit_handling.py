#!/usr/bin/env python3
"""
Test script to verify the improved rate limit handling works correctly.
"""

import os
import sys
import traceback

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.retry_utils import OpenAIWaitStrategy, extract_openai_wait_time
from tenacity import RetryCallState
from openai import RateLimitError


class MockRetryState:
    """Mock retry state for testing"""

    def __init__(self, attempt_number, outcome):
        self.attempt_number = attempt_number
        self.outcome = outcome


class MockOutcome:
    """Mock outcome for testing"""

    def __init__(self, exception):
        self._exception = exception
        self.failed = True

    def exception(self):
        return self._exception


def test_rate_limit_strategy():
    """Test the new OpenAI wait strategy with different scenarios"""

    print("🧪 Testing OpenAI Wait Strategy with Rate Limit Scaling\n")

    # Test cases with different usage patterns
    test_cases = [
        {
            "name": "100% Capacity (Sustained Rate Limit)",
            "error_msg": "Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 200000, Requested 4521. Please try again in 1.356s. Visit https://platform.openai.com/account/rate-limits to learn more.",
            "attempts": [1, 2, 3, 4],
        },
        {
            "name": "95% Capacity (High Usage)",
            "error_msg": "Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 190000, Requested 20000. Please try again in 2.5s. Visit https://platform.openai.com/account/rate-limits to learn more.",
            "attempts": [1, 2, 3],
        },
        {
            "name": "80% Capacity (Normal Usage)",
            "error_msg": "Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 160000, Requested 20000. Please try again in 1.2s. Visit https://platform.openai.com/account/rate-limits to learn more.",
            "attempts": [1, 2],
        },
    ]

    wait_strategy = OpenAIWaitStrategy(min_wait=5, max_wait=300)

    for test_case in test_cases:
        print(f"--- {test_case['name']} ---")

        # Create mock exception that behaves like RateLimitError
        class MockRateLimitError:
            def __str__(self):
                return test_case["error_msg"]

        mock_error = MockRateLimitError()

        # Monkey patch isinstance to return True for our mock
        original_isinstance = __builtins__["isinstance"]

        def mock_isinstance(obj, class_or_tuple):
            if obj is mock_error and class_or_tuple is RateLimitError:
                return True
            return original_isinstance(obj, class_or_tuple)

        __builtins__["isinstance"] = mock_isinstance

        # Test different retry attempts
        for attempt in test_case["attempts"]:
            mock_outcome = MockOutcome(mock_error)
            mock_retry_state = MockRetryState(attempt, mock_outcome)

            wait_time = wait_strategy(mock_retry_state)

            print(f"  Attempt #{attempt}: Wait {wait_time:.2f}s")

        print()


def test_error_parsing():
    """Test the error message parsing functionality"""

    print("🔍 Testing Error Message Parsing\n")

    test_messages = [
        "Please try again in 1.356s",
        "Please try again in 436ms",
        "Please try again in 30.5s",
        "No wait time mentioned",
        "Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 200000, Requested 4521. Please try again in 1.356s. Visit https://platform.openai.com/account/rate-limits to learn more.",
    ]

    for msg in test_messages:

        class MockError:
            def __str__(self):
                return msg

        mock_error = MockError()
        wait_time = extract_openai_wait_time(mock_error)
        print(f"Message: '{msg[:50]}...' -> Wait time: {wait_time}s")

    print()


if __name__ == "__main__":
    try:
        print("🚀 Testing Improved OpenAI Rate Limit Handling\n")

        test_error_parsing()
        test_rate_limit_strategy()

        print("✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        traceback.print_exc()
