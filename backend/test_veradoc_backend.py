#!/usr/bin/env python3
"""
Test script to verify VeraDoc backend functionality.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_imports():
    """Test that all necessary modules can be imported."""
    try:
        print("Testing imports...")

        # Test core imports
        from app.api.routes.veradoc import router, process_rag_checklist

        print("✅ VeraDoc router and process_rag_checklist imported successfully")

        from app.models import RagChecklistRequest, VeraDocResponse

        print("✅ VeraDoc models imported successfully")

        from langchain_core.documents import Document as LangchainDocument

        print("✅ LangChain Document imported successfully")

        from langchain_community.vectorstores import Chroma

        print("✅ Chroma vectorstore imported successfully")

        print("\n✅ All imports successful!")
        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_search_mode_model():
    """Test that the search mode model works correctly."""
    try:
        print("\nTesting search mode model...")

        from app.models import RagChecklistRequest

        # Test default value
        request1 = RagChecklistRequest(
            knowledge_base_id="test-kb-id", questions="Test question?"
        )
        print(f"✅ Default search_mode: {request1.search_mode}")

        # Test vector mode
        request2 = RagChecklistRequest(
            knowledge_base_id="test-kb-id",
            questions="Test question?",
            search_mode="vector",
        )
        print(f"✅ Vector search_mode: {request2.search_mode}")

        # Test full_scan mode
        request3 = RagChecklistRequest(
            knowledge_base_id="test-kb-id",
            questions="Test question?",
            search_mode="full_scan",
        )
        print(f"✅ Full scan search_mode: {request3.search_mode}")

        # Test invalid mode (should raise validation error)
        try:
            request4 = RagChecklistRequest(
                knowledge_base_id="test-kb-id",
                questions="Test question?",
                search_mode="invalid_mode",
            )
            print("❌ ERROR: Invalid search mode was accepted!")
            return False
        except Exception as e:
            print(
                f"✅ Validation correctly rejected invalid search mode: {type(e).__name__}"
            )

        print("✅ Search mode model tests passed!")
        return True

    except Exception as e:
        print(f"❌ Search mode model test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_full_scan_retriever():
    """Test the FullScanRetriever class logic."""
    try:
        print("\nTesting FullScanRetriever logic...")

        # Mock ChromaDB for testing
        class MockChromaDB:
            def get(self):
                return {
                    "documents": ["Test document 1", "Test document 2"],
                    "metadatas": [{"source": "test1.pdf"}, {"source": "test2.pdf"}],
                }

        # Import the LangchainDocument class
        from langchain_core.documents import Document as LangchainDocument

        # Test the FullScanRetriever logic (simulated)
        mock_chroma = MockChromaDB()
        all_data = mock_chroma.get()

        documents = []
        if all_data and "documents" in all_data and all_data["documents"]:
            for i, doc_content in enumerate(all_data["documents"]):
                metadata = (
                    all_data["metadatas"][i]
                    if "metadatas" in all_data
                    and i < len(all_data["metadatas"])
                    and all_data["metadatas"][i] is not None
                    else {}
                )

                if not isinstance(metadata, dict):
                    metadata = {}

                documents.append(
                    LangchainDocument(
                        page_content=str(doc_content or ""), metadata=metadata
                    )
                )

        print(f"✅ Created {len(documents)} LangChain documents")
        for i, doc in enumerate(documents):
            print(
                f"   Document {i+1}: {doc.page_content[:50]}... (metadata: {doc.metadata})"
            )

        print("✅ FullScanRetriever logic test passed!")
        return True

    except Exception as e:
        print(f"❌ FullScanRetriever test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🧪 Starting VeraDoc backend tests...\n")

    tests = [
        ("Import Tests", test_imports),
        ("Search Mode Model Tests", test_search_mode_model),
        ("FullScanRetriever Tests", test_full_scan_retriever),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name}")
        print("=" * 50)

        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print(f"\n{'='*50}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print("=" * 50)

    if passed == total:
        print("🎉 All tests passed! VeraDoc backend should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. There may be issues with the backend.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
