#!/usr/bin/env python3
"""
Test script to verify runtime ML installation works correctly.
"""

import os
import sys

# Set environment variables to simulate lean build with runtime ML
os.environ["ENABLE_PYTORCH"] = "false"
os.environ["RUNTIME_INSTALL_PYTORCH"] = "true"

# Add the backend app to Python path
sys.path.insert(0, "/app")


def test_runtime_ml():
    print("=== Testing Runtime ML Installation ===")

    # Test the configuration functions
    from app.core.ml_imports import is_pytorch_enabled, is_runtime_install_enabled

    print(f"ENABLE_PYTORCH: {os.environ.get('ENABLE_PYTORCH')}")
    print(f"RUNTIME_INSTALL_PYTORCH: {os.environ.get('RUNTIME_INSTALL_PYTORCH')}")
    print(f"is_pytorch_enabled(): {is_pytorch_enabled()}")
    print(f"is_runtime_install_enabled(): {is_runtime_install_enabled()}")

    # Test PyTorch installation
    print("\n=== Testing PyTorch Installation ===")
    from app.core.ml_imports import ensure_pytorch

    pytorch_available = ensure_pytorch()
    print(f"PyTorch available after ensure_pytorch(): {pytorch_available}")

    if pytorch_available:
        try:
            import torch

            print(f"PyTorch version: {torch.__version__}")
            print("✅ PyTorch runtime installation successful!")
        except ImportError:
            print("❌ PyTorch import failed after installation")
    else:
        print("❌ PyTorch not available")

    # Test HuggingFace embeddings
    print("\n=== Testing HuggingFace Embeddings ===")
    from app.core.ml_imports import get_langchain_huggingface

    HuggingFaceEmbeddings = get_langchain_huggingface()
    if HuggingFaceEmbeddings:
        print("✅ HuggingFace embeddings available!")

        # Try to create an embeddings instance
        try:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            print("✅ HuggingFace embeddings model loaded successfully!")

            # Test embedding a simple text
            test_text = "This is a test sentence."
            embedding = embeddings.embed_query(test_text)
            print(f"✅ Test embedding successful! Dimension: {len(embedding)}")

        except Exception as e:
            print(f"❌ Error creating embeddings: {e}")
    else:
        print("❌ HuggingFace embeddings not available")


if __name__ == "__main__":
    test_runtime_ml()
