#!/usr/bin/env python3
"""
Test the new page image generation logic for table processing.
"""

import sys
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

sys.path.append("backend")


def test_new_table_processing():
    """Test the new table processing logic with page image generation"""

    logger.info("🔄 TESTING NEW TABLE PROCESSING LOGIC")
    logger.info("=" * 60)

    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return

    # Load file
    with open(file_path, "rb") as f:
        file_content = f.read()

    logger.info(f"📄 File loaded: {len(file_content)} bytes")

    # Mock LLM with vision capability
    class MockVisionLLM:
        def __init__(self):
            self.model_name = "gpt-4o"
            self.model = "gpt-4o"

    mock_llm = MockVisionLLM()

    # Mock settings temporarily
    class MockSettings:
        VISION_ENABLED_MODELS = ["gpt-4o", "gpt-4-vision", "claude-3"]

    # Test the new table processing function
    try:
        # Import and patch settings
        import backend.app.core.config as config_module

        original_settings = getattr(config_module, "settings", None)
        config_module.settings = MockSettings()

        from backend.app.services.document_utils import (
            extract_documents_with_table_processing,
        )

        logger.info(
            "🔄 Calling extract_documents_with_table_processing with new logic..."
        )

        processed_docs, table_data = extract_documents_with_table_processing(
            file_content, "Appendix 6 Fee Schedule.pdf", mock_llm
        )

        logger.info(f"📊 RESULTS:")
        logger.info(f"   Processed documents: {len(processed_docs)}")
        logger.info(f"   Table data keys: {list(table_data.keys())}")
        logger.info(f"   Tables extracted: {len(table_data.get('tables', []))}")

        if table_data.get("tables"):
            logger.info("🎉 SUCCESS: Vision processing was triggered!")
            logger.info("✅ Table enhancement is now working correctly")
        else:
            logger.warning(
                "⚠️ Vision processing was not triggered - check the logs above"
            )

        # Restore settings
        if original_settings:
            config_module.settings = original_settings

    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("💡 This is likely why table processing fails in your backend")
        logger.error("💡 Install with: pip install pdf2image PyMuPDF")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_new_table_processing()

    print("\n" + "=" * 60)
    print("📝 SUMMARY:")
    print("✅ If SUCCESS: Table processing now works correctly")
    print("❌ If failed: Check for missing pdf2image dependency")
    print("=" * 60)
