#!/usr/bin/env python3
"""
Test script for the embedding chunking functionality.
"""
import sys
import os

# Add the backend app to the path
sys.path.append("backend")

from langchain.schema.document import Document
from backend.app.api.routes.knowledgebases import (
    estimate_tokens_for_embedding,
    chunk_documents_for_embedding,
)


def test_token_estimation():
    """Test the token estimation function."""
    print("Testing token estimation...")

    # Test with a simple text
    test_text = "This is a simple test text to estimate tokens."
    tokens = estimate_tokens_for_embedding(test_text)
    print(f"Text: '{test_text}' -> {tokens} tokens")

    # Test with a larger text
    large_text = "This is a larger test text. " * 1000  # Repeat to make it larger
    tokens = estimate_tokens_for_embedding(large_text)
    print(f"Large text ({len(large_text)} chars) -> {tokens:,} tokens")


def test_document_chunking():
    """Test the document chunking functionality."""
    print("\nTesting document chunking...")

    # Create test documents
    docs = []

    # Small documents
    for i in range(5):
        content = f"This is document {i}. " * 100  # About 300-400 tokens each
        docs.append(Document(page_content=content, metadata={"source": f"doc_{i}"}))

    # One large document (simulate the problematic case)
    large_content = (
        "This is a very large document that exceeds token limits. " * 5000
    )  # About 280k+ tokens
    docs.append(Document(page_content=large_content, metadata={"source": "large_doc"}))

    print(f"Created {len(docs)} test documents")

    # Test chunking with a small limit for testing
    chunks = chunk_documents_for_embedding(docs, max_tokens_per_chunk=10000)

    print(f"Result: {len(chunks)} chunks created")

    for i, chunk in enumerate(chunks):
        total_tokens = sum(
            estimate_tokens_for_embedding(doc.page_content) for doc in chunk
        )
        print(f"  Chunk {i+1}: {len(chunk)} documents, ~{total_tokens:,} tokens")


if __name__ == "__main__":
    print("Testing embedding chunking functionality...")
    test_token_estimation()
    test_document_chunking()
    print("\nTest completed!")
