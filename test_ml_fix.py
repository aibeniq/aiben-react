#!/usr/bin/env python3
"""
Test script to verify the HuggingFace shared directory fix.
"""

import os
import sys

# Set environment variables to simulate lean build with runtime ML
os.environ["ENABLE_PYTORCH"] = "false"
os.environ["RUNTIME_INSTALL_PYTORCH"] = "true"

# Add the backend app to Python path
sys.path.insert(0, "/app")


def test_huggingface_fix():
    print("=== Testing HuggingFace Shared Directory Fix ===")

    # Test environment variables
    print(f"ENABLE_PYTORCH: {os.environ.get('ENABLE_PYTORCH')}")
    print(f"RUNTIME_INSTALL_PYTORCH: {os.environ.get('RUNTIME_INSTALL_PYTORCH')}")

    try:
        from app.core.ml_imports import get_langchain_huggingface

        print("✅ Successfully imported get_langchain_huggingface")

        print("\n=== Testing HuggingFace Embeddings Installation ===")
        HuggingFaceEmbeddings = get_langchain_huggingface()

        if HuggingFaceEmbeddings:
            print("✅ HuggingFaceEmbeddings class obtained successfully")

            # Try to create embeddings instance
            try:
                print("Creating HuggingFaceEmbeddings instance...")
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                print("✅ HuggingFaceEmbeddings instance created successfully!")

                # Test embedding a simple text
                print("Testing text embedding...")
                test_text = "This is a test sentence for embeddings."
                embedding = embeddings.embed_query(test_text)
                print(f"✅ Embedding successful! Vector dimension: {len(embedding)}")
                print(f"✅ First 5 values: {embedding[:5]}")

                return True

            except Exception as e:
                print(f"❌ Error creating or using embeddings: {e}")
                return False
        else:
            print("❌ Failed to get HuggingFaceEmbeddings class")
            return False

    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


if __name__ == "__main__":
    success = test_huggingface_fix()
    if success:
        print("\n🎉 HuggingFace shared directory fix is working!")
    else:
        print("\n❌ Fix still needs work")
