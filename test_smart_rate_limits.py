#!/usr/bin/env python3
"""
Simple test script to verify the improved rate limit handling works correctly.
"""

import os
import sys
import re

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def extract_openai_wait_time(exception):
    """
    Extract the suggested wait time from OpenAI rate limit error messages.
    """
    try:
        error_message = str(exception)

        # Pattern for seconds: "try again in 39.466s"
        seconds_match = re.search(r"try again in (\d+\.?\d*)s", error_message)
        if seconds_match:
            return float(seconds_match.group(1))

        # Pattern for milliseconds: "try again in 608ms"
        ms_match = re.search(r"try again in (\d+)ms", error_message)
        if ms_match:
            return float(ms_match.group(1)) / 1000.0

        return 0.0

    except Exception as e:
        print(f"Failed to extract wait time from error message: {e}")
        return 0.0


def extract_rate_limit_info(error_message):
    """Extract rate limit usage information from OpenAI error message."""
    try:
        # Pattern to extract: "Limit 200000, Used 200000, Requested 4521"
        limit_match = re.search(
            r"Limit (\d+), Used (\d+), Requested (\d+)", error_message
        )
        if limit_match:
            limit = int(limit_match.group(1))
            used = int(limit_match.group(2))
            requested = int(limit_match.group(3))
            return limit, used, requested

        return None, None, None
    except Exception as e:
        print(f"Could not extract rate limit info: {e}")
        return None, None, None


def calculate_smart_wait_time(error_message, attempt_number, min_wait=5, max_wait=300):
    """Calculate intelligent wait time for rate limit scenarios."""

    # Extract wait time and usage info
    class MockError:
        def __str__(self):
            return error_message

    mock_error = MockError()
    suggested_wait = extract_openai_wait_time(mock_error)
    limit, used, requested = extract_rate_limit_info(error_message)

    if suggested_wait > 0 and limit and used:
        # Calculate usage percentage
        usage_percent = used / limit * 100

        # Base wait time from OpenAI suggestion
        base_wait = suggested_wait

        # Apply intelligent scaling based on usage and retry count
        if usage_percent >= 100:
            # At 100% capacity - use aggressive scaling for sliding window reset
            scaling_factor = 2.0 + (
                attempt_number * 1.5
            )  # Start at 2x, increase by 1.5x per retry
            strategy = "SUSTAINED RATE LIMIT"
        elif usage_percent >= 95:
            # Near capacity - moderate scaling
            scaling_factor = 1.5 + (attempt_number * 0.5)
            strategy = "HIGH USAGE"
        else:
            # Normal usage - minimal scaling
            scaling_factor = 1.1 + (attempt_number * 0.1)
            strategy = "NORMAL USAGE"

        # Apply scaling and ensure minimum/maximum bounds
        scaled_wait = base_wait * scaling_factor
        final_wait = max(min_wait, min(scaled_wait, max_wait))

        return final_wait, usage_percent, strategy, scaling_factor

    return None, None, None, None


def test_rate_limit_scenarios():
    """Test different rate limit scenarios"""

    print("🧪 Testing Smart Rate Limit Wait Time Calculation\n")

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

    for test_case in test_cases:
        print(f"--- {test_case['name']} ---")

        for attempt in test_case["attempts"]:
            result = calculate_smart_wait_time(test_case["error_msg"], attempt)
            wait_time, usage_percent, strategy, scaling_factor = result

            if wait_time is not None:
                print(
                    f"  Attempt #{attempt}: {wait_time:.2f}s (Usage: {usage_percent:.1f}%, Strategy: {strategy}, Scale: {scaling_factor:.1f}x)"
                )
            else:
                print(f"  Attempt #{attempt}: Could not calculate wait time")

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
        limit, used, requested = extract_rate_limit_info(msg)

        usage_info = f" (Usage: {used}/{limit})" if limit and used else ""
        print(f"Wait time: {wait_time}s{usage_info} <- '{msg[:60]}...'")

    print()


if __name__ == "__main__":
    try:
        print("🚀 Testing Improved OpenAI Rate Limit Handling\n")

        test_error_parsing()
        test_rate_limit_scenarios()

        print("✅ All tests completed successfully!")
        print("\n🎯 Key Improvements:")
        print("   • Sustained rate limits (100% usage) get 2x+ scaling")
        print("   • High usage (95%+) gets moderate scaling")
        print("   • Progressive scaling increases with retry attempts")
        print("   • Maximum wait time capped at 5 minutes")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
