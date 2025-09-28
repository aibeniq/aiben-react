#!/usr/bin/env python3
"""
Comprehensive test script for table detection and vision processing with enhanced logging.
This will test the complete pipeline on Appendix 6 Fee Schedule.pdf and show detailed logs.
"""

import sys
import os
import logging
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.app.services.table_detection import TableDetector
from backend.app.services.document_utils import extract_documents_with_table_processing
from backend.app.services.vision_service import VisionService
from backend.app.core.config import Settings


# Mock LLM classes for testing
class MockVisionLLM:
    """Mock LLM that should support vision"""

    def __init__(self, model_name):
        self.model_name = model_name
        self.model = model_name


class MockNonVisionLLM:
    """Mock LLM that should NOT support vision"""

    def __init__(self, model_name):
        self.model_name = model_name
        self.model = model_name


def test_vision_detection():
    """Test vision capability detection with different LLM types"""

    print("\n" + "=" * 70)
    print("🔮 TESTING VISION CAPABILITY DETECTION")
    print("=" * 70)

    test_cases = [
        ("GPT-4 Vision", MockVisionLLM("gpt-4-vision-preview")),
        ("GPT-4o", MockVisionLLM("gpt-4o")),
        ("Claude-3", MockVisionLLM("claude-3-sonnet-20240229")),
        ("GPT-3.5 (no vision)", MockNonVisionLLM("gpt-3.5-turbo")),
        ("None", None),
    ]

    for name, llm in test_cases:
        print(f"\n🤖 Testing: {name}")
        vision_enabled = VisionService.is_vision_enabled(llm)
        print(
            f"   Result: {'✅ Vision Enabled' if vision_enabled else '❌ Vision Disabled'}"
        )


def test_table_processing_pipeline():
    """Test the complete table processing pipeline"""

    print("\n" + "=" * 70)
    print("📊 TESTING COMPLETE TABLE PROCESSING PIPELINE")
    print("=" * 70)

    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False

    print(f"📄 Testing file: {file_path}")

    # Load file content
    with open(file_path, "rb") as f:
        file_content = f.read()

    print(f"📄 Loaded file: {len(file_content)} bytes")

    # Test with different LLM types
    test_llms = [
        ("GPT-4 Vision (should work)", MockVisionLLM("gpt-4-vision-preview")),
        ("GPT-3.5 (should fail vision)", MockNonVisionLLM("gpt-3.5-turbo")),
        ("None (should fail)", None),
    ]

    for llm_name, llm in test_llms:
        print(f"\n🤖 Testing with: {llm_name}")
        print("-" * 50)

        try:
            # Call the enhanced table processing function
            processed_documents, table_data = extract_documents_with_table_processing(
                file_content, "Appendix 6 Fee Schedule.pdf", llm
            )

            print(f"✅ Processing complete:")
            print(f"   📄 Processed documents: {len(processed_documents)}")
            print(f"   📊 Table data: {len(table_data.get('tables', []))} tables")

            if table_data.get("tables"):
                print(f"   🔮 Vision processing was SUCCESSFUL!")
            else:
                print(
                    f"   📄 Vision processing was NOT used (expected for non-vision models)"
                )

        except Exception as e:
            print(f"❌ Error during processing: {str(e)}")
            import traceback

            traceback.print_exc()


def test_basic_table_detection():
    """Test basic table detection without vision processing"""

    print("\n" + "=" * 70)
    print("🔍 TESTING BASIC TABLE DETECTION")
    print("=" * 70)

    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False

    # Load file and extract documents
    with open(file_path, "rb") as f:
        file_content = f.read()

    from backend.app.services.document_utils import extract_documents_from_file_unified

    documents = extract_documents_from_file_unified(
        file_content, "Appendix 6 Fee Schedule.pdf"
    )

    print(f"📄 Loaded {len(documents)} document chunks")

    # Test table detection
    table_pages = TableDetector.identify_table_pages(documents)
    print(f"📊 Table pages detected: {len(table_pages)} pages: {table_pages}")

    # Test vision recommendation
    should_use_vision = TableDetector.should_use_vision_for_tables(documents, ".pdf")
    print(f"🔮 Should use vision: {should_use_vision}")

    # Analyze first few pages
    for i, doc in enumerate(documents[:3]):
        page_num = doc.metadata.get("page", i + 1)
        has_tables = TableDetector.detect_tables_in_text(doc.page_content)

        if has_tables:
            analysis = TableDetector.analyze_table_complexity(doc.page_content)
            print(f"📄 Page {page_num}:")
            print(f"   Tables: {has_tables}")
            print(f"   Complexity: {analysis.get('complexity')}")
            print(f"   Financial rows: {analysis.get('financial_rows', 0)}")
            print(f"   Financial density: {analysis.get('financial_density', 0):.2f}")


if __name__ == "__main__":
    print("🧪 COMPREHENSIVE TABLE PROCESSING TEST SUITE")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        # Test 1: Basic table detection
        test_basic_table_detection()

        # Test 2: Vision capability detection
        test_vision_detection()

        # Test 3: Complete pipeline
        test_table_processing_pipeline()

        print("\n" + "=" * 70)
        print("🎉 TEST SUITE COMPLETED")
        print("Check the logs above to see why vision processing may not be triggered")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback

        traceback.print_exc()
