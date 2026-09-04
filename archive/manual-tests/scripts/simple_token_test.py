#!/usr/bin/env python3
"""
Simple test script for the embedding chunking functionality.
"""
import tiktoken


def estimate_tokens_for_embedding(text: str) -> int:
    """
    Estimate tokens in text for embedding models using cl100k_base encoding.
    This is the same encoding used by OpenAI's text-embedding models.
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback to rough estimation if tiktoken fails
        return len(text) // 4


def test_token_estimation():
    """Test the token estimation function."""
    print("Testing token estimation...")

    # Test with a simple text
    test_text = "This is a simple test text to estimate tokens."
    tokens = estimate_tokens_for_embedding(test_text)
    print(f"Text: '{test_text}' -> {tokens} tokens")

    # Test with a text that would exceed 300k tokens (simulate the original error)
    large_text = (
        "This is a test sentence that will be repeated many times to simulate a large document upload. "
        * 25000
    )  # About 500k+ tokens
    tokens = estimate_tokens_for_embedding(large_text)
    print(f"Large text ({len(large_text)} chars) -> {tokens:,} tokens")

    if tokens > 300000:
        print(f"⚠️  This text exceeds OpenAI's 300k token limit!")
        chunks_needed = (tokens // 250000) + 1
        print(f"Would need {chunks_needed} chunks to process safely")
    else:
        print("✅ Text is within token limits")


if __name__ == "__main__":
    print("Testing embedding token estimation...")
    test_token_estimation()
    print("\nTest completed!")
