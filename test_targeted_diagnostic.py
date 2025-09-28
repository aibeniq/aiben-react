#!/usr/bin/env python3
"""
Targeted diagnostic for table processing issue.
This bypasses settings issues and focuses on the core problem.
"""

import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

sys.path.append("backend")


def diagnose_table_processing():
    """Run targeted diagnostic on table processing"""

    logger.info("🔍 TARGETED TABLE PROCESSING DIAGNOSTIC")
    logger.info("=" * 60)

    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        logger.error(f"❌ File not found: {file_path}")
        return

    # Load file
    with open(file_path, "rb") as f:
        file_content = f.read()

    logger.info(f"📄 File loaded: {len(file_content)} bytes")

    # Import functions
    try:
        from backend.app.services.document_utils import (
            extract_documents_and_images_from_file_unified,
        )
        from backend.app.services.table_detection import TableDetector

        # Step 1: Extract documents and images
        logger.info("\n🔍 STEP 1: Document and Image Extraction")
        documents, images = extract_documents_and_images_from_file_unified(
            file_content, "Appendix 6 Fee Schedule.pdf"
        )
        logger.info(f"✅ Documents: {len(documents)}")
        logger.info(f"✅ Images: {len(images)}")

        # Step 2: Table detection
        logger.info("\n🔍 STEP 2: Table Detection")
        table_pages = TableDetector.identify_table_pages(documents)
        logger.info(f"✅ Table pages: {len(table_pages)} - {table_pages}")

        # Step 3: Vision recommendation
        logger.info("\n🔍 STEP 3: Vision Recommendation")
        should_use_vision = TableDetector.should_use_vision_for_tables(
            documents, ".pdf"
        )
        logger.info(f"✅ Should use vision: {should_use_vision}")

        # Step 4: The three conditions check
        logger.info("\n🔍 STEP 4: Three Conditions Analysis")
        logger.info(
            f"   Condition 1 (table_pages): {bool(table_pages)} - {len(table_pages)} pages"
        )
        logger.info(f"   Condition 2 (images): {bool(images)} - {len(images)} images")

        # Mock vision check (since we can't load settings)
        mock_vision_enabled = True  # Since you confirmed vision works
        logger.info(
            f"   Condition 3 (vision_enabled): {mock_vision_enabled} - (confirmed working)"
        )

        all_conditions_met = table_pages and images and mock_vision_enabled
        logger.info(f"   ALL CONDITIONS MET: {all_conditions_met}")

        # Step 5: Detailed image analysis
        if not images:
            logger.error("❌ PROBLEM IDENTIFIED: No images extracted!")
            logger.error("   This is why table enhancement is skipped")
            logger.error(
                "   Even though vision works for regular images, table processing needs PDF page images"
            )

            # Check if we have PDF processing dependencies
            try:
                import fitz  # PyMuPDF

                logger.info("✅ PyMuPDF (fitz) is available")
            except ImportError:
                logger.error("❌ PyMuPDF (fitz) not available - this is the problem!")

            try:
                from pdf2image import convert_from_bytes

                logger.info("✅ pdf2image is available")
            except ImportError:
                logger.error("❌ pdf2image not available - this could be the problem!")

        else:
            logger.info(f"✅ Images successfully extracted: {len(images)} images")
            logger.info("   The issue is likely NOT image extraction")

        # Step 6: Show what would happen
        logger.info(f"\n🎯 CONCLUSION:")
        if all_conditions_met:
            logger.info("✅ All conditions are met - table enhancement SHOULD work")
            logger.info(
                "   The issue may be in the actual backend environment or LLM configuration"
            )
        else:
            failed_conditions = []
            if not table_pages:
                failed_conditions.append("no table pages")
            if not images:
                failed_conditions.append("no images extracted")
            if not mock_vision_enabled:
                failed_conditions.append("vision disabled")

            logger.error(
                f"❌ Table enhancement skipped due to: {', '.join(failed_conditions)}"
            )

            # Specific recommendations
            if not images:
                logger.info("💡 SOLUTION: Install missing PDF processing dependencies:")
                logger.info("   pip install PyMuPDF pdf2image")

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    diagnose_table_processing()
