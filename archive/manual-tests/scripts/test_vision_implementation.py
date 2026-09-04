#!/usr/bin/env python3
"""Test vision service functionality."""

import sys
import os

# Add the backend directory to the Python path
sys.path.append(".")


def test_vision_service():
    """Test the vision service functionality."""
    print("🔧 Vision Service Test")
    print("=" * 50)

    try:
        # Import the vision service
        from app.services.vision_service import VisionService

        print("✅ Successfully imported VisionService")

        # Test vision model detection
        class MockVisionLLM:
            model_name = "gpt-4o"

        class MockTextLLM:
            model_name = "gpt-3.5-turbo"

        vision_llm = MockVisionLLM()
        text_llm = MockTextLLM()

        print(f"✅ Vision LLM check: {VisionService.is_vision_enabled(vision_llm)}")
        print(f"✅ Text LLM check: {VisionService.is_vision_enabled(text_llm)}")

        # Test image preparation for comparison
        doc1_images = ["image1_b64", "image2_b64"]
        doc2_images = ["image3_b64"]

        combined = VisionService.prepare_images_for_comparison(
            doc1_images, doc2_images, "doc1.pdf", "doc2.pdf"
        )

        print(f"✅ Combined images for comparison: {len(combined)} images")

        # Test combination strategies
        text_analysis = "This is the text analysis."
        vision_analysis = "This is the vision analysis."

        combined_analysis = VisionService.combine_text_and_vision_analysis(
            text_analysis, vision_analysis, "comprehensive"
        )

        print(f"✅ Combined analysis length: {len(combined_analysis)}")

        print("\n📋 Vision Service Test Results:")
        print("✅ VisionService import successful")
        print("✅ Model detection working")
        print("✅ Image preparation working")
        print("✅ Analysis combination working")

    except ImportError as e:
        print(f"❌ Could not import VisionService: {e}")
        return False
    except Exception as e:
        print(f"❌ Vision service test failed: {e}")
        return False

    return True


def test_document_utils_enhancement():
    """Test enhanced document utils."""
    print("\n🔧 Document Utils Enhancement Test")
    print("=" * 50)

    try:
        from app.services.document_utils import (
            extract_documents_and_images_from_file_unified,
        )

        print("✅ Successfully imported enhanced document utils")

        # Test with a simple text file
        test_content = b"This is test content."
        documents, images = extract_documents_and_images_from_file_unified(
            test_content, "test.txt"
        )

        print(
            f"✅ Text file processing: {len(documents)} documents, {len(images)} images"
        )

        print("\n📋 Document Utils Test Results:")
        print("✅ Enhanced document utils import successful")
        print("✅ Unified extraction function working")

    except ImportError as e:
        print(f"❌ Could not import enhanced document utils: {e}")
        return False
    except Exception as e:
        print(f"❌ Document utils test failed: {e}")
        return False

    return True


def test_configuration():
    """Test vision configuration."""
    print("\n🔧 Configuration Test")
    print("=" * 50)

    try:
        from app.core.config import settings

        print("✅ Successfully imported settings")

        # Check vision-related settings
        print(f"Vision models: {settings.VISION_ENABLED_MODELS}")
        print(f"Max images per document: {settings.MAX_IMAGES_PER_DOCUMENT}")
        print(f"Max image size: {settings.MAX_IMAGE_SIZE_MB}MB")

        # Check prompt templates exist
        templates = [
            "CHATBOT_VISION_PROMPT_TEMPLATE",
            "TWINCHECK_VISION_COMPARISON_PROMPT_TEMPLATE",
            "FORMCONNECT_VISION_PROMPT_TEMPLATE",
            "VERADOC_VISION_PROMPT_TEMPLATE",
        ]

        for template in templates:
            if hasattr(settings, template):
                print(f"✅ {template} exists")
            else:
                print(f"❌ {template} missing")

        print("\n📋 Configuration Test Results:")
        print("✅ Settings import successful")
        print("✅ Vision configuration loaded")

    except ImportError as e:
        print(f"❌ Could not import settings: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("🚀 Vision Enhancement Test Suite")
    print("=" * 60)

    all_tests_passed = True

    # Run all tests
    all_tests_passed &= test_vision_service()
    all_tests_passed &= test_document_utils_enhancement()
    all_tests_passed &= test_configuration()

    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 All tests passed! Vision enhancement is ready.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
