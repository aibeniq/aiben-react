"""
Simple test to verify the generate-outline-json endpoint
"""

import sys
import os

sys.path.append(".")

from app.models import GenerateOutlineRequest


# Test the model
def test_model():
    request = GenerateOutlineRequest(
        description="Test outline for AI in healthcare",
        report_type="general",
        knowledge_base_id="test-kb-id",
    )

    print(f"Request created successfully: {request}")
    print(f"Knowledge base ID: {request.knowledge_base_id}")


if __name__ == "__main__":
    test_model()
    print("✅ Model test passed!")
