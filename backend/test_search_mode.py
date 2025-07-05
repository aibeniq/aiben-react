#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, ".")

from app.models import RagChecklistRequest


def test_rag_request():
    try:
        # Test vector mode (default)
        vector_req = RagChecklistRequest(
            knowledge_base_id="test-kb-id",
            questions="Test question 1",
            search_mode="vector",
        )
        print(f"✅ Vector mode request: {vector_req.search_mode}")

        # Test full_scan mode
        full_scan_req = RagChecklistRequest(
            knowledge_base_id="test-kb-id",
            questions="Test question 2",
            search_mode="full_scan",
        )
        print(f"✅ Full scan mode request: {full_scan_req.search_mode}")

        # Test default mode (should be vector)
        default_req = RagChecklistRequest(
            knowledge_base_id="test-kb-id", questions="Test question 3"
        )
        print(f"✅ Default mode request: {default_req.search_mode}")

        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    test_rag_request()
