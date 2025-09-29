#!/usr/bin/env python3
"""Direct test of vision service to see debug output"""

import sys
import os

# Setup path like the backend would
sys.path.append("/app")

# Now try to import and test the vision service directly
try:
    from app.services.vision_service import VisionService
    from app.services.llms import initialize_llm_client
    from app.core.config import settings
    import base64

    def test_vision_service():
        print("=== Direct Vision Service Test ===")

        # Initialize LLM client (same as backend does)
        llm = initialize_llm_client("gpt-4o-mini")
        print(f"✅ LLM initialized: {type(llm)}")

        # Test a simple case
        print("\n🔧 Testing safe_vision_analysis with empty images...")

        # Test with empty images first
        result = VisionService.safe_vision_analysis(
            llm=llm,
            prompt_template="Test prompt",
            variables={"test": "value"},
            images=[],
        )

        print(f"📝 Result with empty images: {result}")

        # Now test with dummy image data
        print("\n🔧 Testing with dummy image data...")
        dummy_images = [
            {
                "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                "metadata": {"test": "dummy"},
            }
        ]

        result2 = VisionService.safe_vision_analysis(
            llm=llm,
            prompt_template="Describe what you see in the image: {test}",
            variables={"test": "test_value"},
            images=dummy_images,
        )

        print(f"📝 Result with dummy image: {result2}")

        return True

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    return False

if __name__ == "__main__":
    success = test_vision_service()
    sys.exit(0 if success else 1)
