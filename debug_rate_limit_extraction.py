#!/usr/bin/env python3
"""
Debug script to test OpenAI rate limit error message parsing.
"""

import re
from openai import RateLimitError


def extract_openai_wait_time(exception):
    """
    Extract the suggested wait time from OpenAI rate limit error messages.
    """
    try:
        error_message = str(exception)
        print(f"Full error message: {error_message}")

        # Look for patterns like "try again in X.Xs" or "try again in Xms"

        # Pattern for seconds: "try again in 39.466s"
        seconds_match = re.search(r"try again in (\d+\.?\d*)s", error_message)
        if seconds_match:
            print(f"Found seconds match: {seconds_match.group(1)}")
            return float(seconds_match.group(1))

        # Pattern for milliseconds: "try again in 608ms"
        ms_match = re.search(r"try again in (\d+)ms", error_message)
        if ms_match:
            print(f"Found ms match: {ms_match.group(1)}")
            return float(ms_match.group(1)) / 1000.0

        print("No pattern found in error message")
        return 0.0

    except Exception as e:
        print(f"Failed to extract wait time from error message: {e}")
        return 0.0


# Test with various error message formats
test_messages = [
    "Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 189522, Requested 20045. Please try again in 2.87s. Visit https://platform.openai.com/account/rate-limits to learn more.",
    "Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 181224, Requested 20231. Please try again in 436ms. Visit https://platform.openai.com/account/rate-limits to learn more.",
    "Error code: 429 - {'error': {'message': 'Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 189522, Requested 20045. Please try again in 2.87s. Visit https://platform.openai.com/account/rate-limits to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}",
]

print("Testing error message parsing:")
for i, msg in enumerate(test_messages):
    print(f"\n--- Test {i+1} ---")

    # Create a mock exception with this message
    class MockException:
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return self.message

    mock_error = MockException(msg)
    wait_time = extract_openai_wait_time(mock_error)
    print(f"Extracted wait time: {wait_time} seconds")

# Test with actual RateLimitError structure
print("\n\n--- Testing with RateLimitError structure ---")
try:
    # This will fail but let's see the structure
    raise RateLimitError(
        message="Rate limit reached for gpt-4o-mini in organization org-Uc4Dd425U2fzq58c9zw4okdC on tokens per min (TPM): Limit 200000, Used 189522, Requested 20045. Please try again in 2.87s. Visit https://platform.openai.com/account/rate-limits to learn more.",
        response=None,
        body=None,
    )
except RateLimitError as e:
    print(f"RateLimitError str(): {str(e)}")
    print(f"RateLimitError message: {getattr(e, 'message', 'No message attr')}")
    wait_time = extract_openai_wait_time(e)
    print(f"Extracted wait time from RateLimitError: {wait_time} seconds")
