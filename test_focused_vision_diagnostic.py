#!/usr/bin/env python3
"""
Focused test script to identify why vision processing isn't triggered.
This test avoids loading full settings and focuses on the core issue.
"""

import sys
import os
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))


def test_vision_processing_issue():
    """Test what's preventing vision processing from being triggered"""

    print("🔍 DIAGNOSING VISION PROCESSING ISSUE")
    print("=" * 60)

    # Import after path setup
    from backend.app.services.document_utils import (
        extract_documents_and_images_from_file_unified,
    )
    from backend.app.services.table_detection import TableDetector

    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"📄 Testing file: {file_path}")

    # Load file content
    with open(file_path, "rb") as f:
        file_content = f.read()

    print(f"📄 File loaded: {len(file_content)} bytes")

    # Step 1: Extract documents and images
    print(f"\n🔍 STEP 1: Extract documents and images")
    try:
        documents, images = extract_documents_and_images_from_file_unified(
            file_content, "Appendix 6 Fee Schedule.pdf"
        )
        print(f"✅ Documents extracted: {len(documents)}")
        print(f"✅ Images extracted: {len(images)}")

        if not images:
            print("❌ PROBLEM FOUND: No images extracted!")
            print("   This is likely the reason vision processing is skipped")
            return

    except Exception as e:
        print(f"❌ Error extracting documents/images: {e}")
        return

    # Step 2: Test table detection
    print(f"\n🔍 STEP 2: Test table detection")
    try:
        table_pages = TableDetector.identify_table_pages(documents)
        print(f"✅ Table pages detected: {len(table_pages)} pages: {table_pages}")

        if not table_pages:
            print("❌ PROBLEM FOUND: No table pages detected!")
            return

    except Exception as e:
        print(f"❌ Error in table detection: {e}")
        return

    # Step 3: Check vision recommendation
    print(f"\n🔍 STEP 3: Check vision recommendation")
    try:
        should_use_vision = TableDetector.should_use_vision_for_tables(
            documents, ".pdf"
        )
        print(f"✅ Should use vision: {should_use_vision}")

        if not should_use_vision:
            print("❌ PROBLEM FOUND: Vision not recommended for these tables!")
            return

    except Exception as e:
        print(f"❌ Error checking vision recommendation: {e}")
        return

    # Step 4: Mock vision capability check
    print(f"\n🔍 STEP 4: Mock vision capability check")

    # Create a mock vision-enabled LLM
    class MockVisionLLM:
        def __init__(self):
            self.model_name = "gpt-4-vision-preview"
            self.model = "gpt-4-vision-preview"

    mock_llm = MockVisionLLM()

    # Mock the settings for vision check
    class MockSettings:
        VISION_ENABLED_MODELS = ["gpt-4o", "gpt-4-vision", "claude-3"]

    # Patch settings temporarily
    import backend.app.core.config as config_module

    original_settings = getattr(config_module, "settings", None)
    config_module.settings = MockSettings()

    try:
        from backend.app.services.vision_service import VisionService

        vision_enabled = VisionService.is_vision_enabled(mock_llm)
        print(f"✅ Mock vision check: {vision_enabled}")

        # Now test the complete condition
        all_conditions_met = table_pages and images and vision_enabled
        print(f"\n📊 FINAL DIAGNOSIS:")
        print(f"   Table pages: {len(table_pages)} ({'✅' if table_pages else '❌'})")
        print(f"   Images: {len(images)} ({'✅' if images else '❌'})")
        print(
            f"   Vision enabled: {vision_enabled} ({'✅' if vision_enabled else '❌'})"
        )
        print(
            f"   All conditions met: {all_conditions_met} ({'✅' if all_conditions_met else '❌'})"
        )

        if all_conditions_met:
            print(f"\n✅ CONCLUSION: Vision processing SHOULD be triggered!")
            print(
                f"   The issue may be in the actual LLM configuration in your backend"
            )
        else:
            print(
                f"\n❌ CONCLUSION: Vision processing correctly skipped due to missing conditions"
            )

    except Exception as e:
        print(f"❌ Error in vision capability check: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Restore original settings
        if original_settings:
            config_module.settings = original_settings


def test_image_extraction():
    """Specifically test image extraction from PDF"""

    print(f"\n🖼️ TESTING IMAGE EXTRACTION")
    print("=" * 40)

    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "rb") as f:
        file_content = f.read()

    # Try to extract images using the document_utils function
    try:
        from backend.app.services.document_utils import extract_images_from_pdf_bytes

        images = extract_images_from_pdf_bytes(file_content)
        print(f"📄 PDF images extracted: {len(images)}")

        if images:
            print(f"✅ Images successfully extracted from PDF")
            for i, img in enumerate(images[:3]):  # Show first 3
                print(f"   Image {i+1}: {len(img)} bytes (base64)")
        else:
            print(f"❌ No images extracted from PDF")
            print(f"   This is likely why vision processing is not triggered")

    except ImportError as e:
        print(f"❌ Missing dependency for PDF image extraction: {e}")
        print(f"   This explains why no images are available for vision processing")
    except Exception as e:
        print(f"❌ Error extracting PDF images: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🔍 FOCUSED VISION PROCESSING DIAGNOSTIC")
    print("=" * 60)

    test_vision_processing_issue()
    test_image_extraction()

    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC COMPLETE")
    print("Check the output above to identify the root cause")
    print("=" * 60)
