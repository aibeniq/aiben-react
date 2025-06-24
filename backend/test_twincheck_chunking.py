"""
Test script for TwinCheck chunking functionality.
This script tests the token estimation and chunking logic.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.routes.twincheck import estimate_tokens, chunk_diff_text


def test_token_estimation():
    """Test token estimation functionality."""
    print("Testing token estimation...")

    test_text = "This is a simple test text with some words."
    tokens = estimate_tokens(test_text)
    print(f"Text: '{test_text}'")
    print(f"Estimated tokens: {tokens}")
    print(f"Characters: {len(test_text)}")
    print(f"Ratio: {len(test_text) / tokens:.2f} chars per token")
    print()


def test_chunking():
    """Test chunking functionality."""
    print("Testing chunking functionality...")

    # Create a large diff text
    large_diff = []
    for i in range(1000):
        large_diff.append(f"- This is line {i} from document 1")
        large_diff.append(f"+ This is line {i} from document 2")

    diff_text = "\n".join(large_diff)

    print(f"Total diff lines: {len(large_diff)}")
    print(f"Total characters: {len(diff_text)}")
    print(f"Estimated tokens: {estimate_tokens(diff_text)}")

    # Test chunking with different limits
    for limit in [10000, 50000, 100000]:
        chunks = chunk_diff_text(diff_text, max_tokens=limit)
        print(f"\nWith {limit} token limit:")
        print(f"  Generated {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            chunk_tokens = estimate_tokens(chunk)
            print(f"  Chunk {i+1}: {chunk_tokens} tokens, {len(chunk.split())} lines")


def test_small_text():
    """Test with small text that shouldn't be chunked."""
    print("\nTesting small text...")

    small_diff = "- Small text\n+ Different small text"
    chunks = chunk_diff_text(small_diff)
    print(f"Small diff tokens: {estimate_tokens(small_diff)}")
    print(f"Number of chunks: {len(chunks)}")
    print("Should be 1 chunk (no chunking needed)")


if __name__ == "__main__":
    print("TwinCheck Chunking Test")
    print("=" * 40)

    test_token_estimation()
    test_chunking()
    test_small_text()

    print("\nTest completed!")
