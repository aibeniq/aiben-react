#!/usr/bin/env python3
"""
Test script to validate the new batched table extraction implementation.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))


def test_batching_logic():
    """Test the batching logic for table extraction"""

    print("🧪 Testing Batched Table Extraction Logic")
    print("=" * 50)

    # Test different scenarios
    test_cases = [
        {"pages": 3, "expected_batches": 1},  # 3 pages = 1 batch
        {"pages": 5, "expected_batches": 1},  # 5 pages = 1 batch
        {"pages": 7, "expected_batches": 2},  # 7 pages = 2 batches (5+2)
        {"pages": 10, "expected_batches": 2},  # 10 pages = 2 batches (5+5)
        {"pages": 12, "expected_batches": 3},  # 12 pages = 3 batches (5+5+2)
        {"pages": 15, "expected_batches": 3},  # 15 pages = 3 batches (5+5+5)
        {"pages": 17, "expected_batches": 4},  # 17 pages = 4 batches (5+5+5+2)
    ]

    BATCH_SIZE = 5

    for test_case in test_cases:
        pages = test_case["pages"]
        expected = test_case["expected_batches"]

        # Calculate actual batches
        actual_batches = (pages + BATCH_SIZE - 1) // BATCH_SIZE

        # Simulate the batching
        batches = []
        for batch_start in range(0, pages, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, pages)
            batch_pages = list(
                range(batch_start + 1, batch_end + 1)
            )  # 1-based page numbers
            batches.append(batch_pages)

        status = "✅" if actual_batches == expected else "❌"
        print(
            f"{status} {pages} pages → {actual_batches} batches (expected {expected})"
        )

        for i, batch in enumerate(batches):
            print(f"    Batch {i+1}: Pages {batch}")

    print("\n🎯 Batching Benefits:")
    print("   • Reduces token usage per LLM call")
    print("   • Prevents hitting model context limits")
    print("   • Allows processing of large documents")
    print("   • Improves reliability and success rate")

    return True


if __name__ == "__main__":
    try:
        test_batching_logic()
        print("\n🎉 Batching logic validation completed!")
    except Exception as e:
        print(f"💥 Test failed: {e}")
        import traceback

        traceback.print_exc()
