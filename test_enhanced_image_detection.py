#!/usr/bin/env python3
"""
Test script to verify the enhanced image-heavy table processing logic.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.table_detection import TableDetector
from langchain.schema import Document


def test_apa_sample_detection():
    """Test detection of APA sample table content."""

    # Simulate the content that appears in your APA table example
    apa_content = """Sample tables https://apastyle.apa.org/style-grammar-guidelines/tables-figures/sample-...
2 of 79/28/2025, 6:05 PM"""

    documents = [
        Document(page_content=apa_content, metadata={"page": 1}),
        Document(page_content=apa_content, metadata={"page": 2}),
        Document(page_content=apa_content, metadata={"page": 3}),
    ]

    print("🧪 Testing APA Sample Table Detection")
    print(f"📄 Sample content length: {len(apa_content)} characters")
    print(f"📝 Content: {apa_content[:100]}...")
    print()

    # Test the should_use_vision_for_tables method
    should_use_vision = TableDetector.should_use_vision_for_tables(documents, ".pdf")

    print(f"🔮 Vision processing recommended: {should_use_vision}")

    if should_use_vision:
        print("✅ SUCCESS: Vision processing will be used for APA sample tables")
    else:
        print(
            "❌ FAILURE: Vision processing will NOT be used - needs more aggressive detection"
        )

    return should_use_vision


def test_minimal_text_detection():
    """Test detection of truly minimal text content."""

    minimal_content = "Table 1"

    documents = [
        Document(page_content=minimal_content, metadata={"page": 1}),
    ]

    print(f"\n🧪 Testing Minimal Text Detection")
    print(f"📄 Content length: {len(minimal_content)} characters")
    print(f"📝 Content: '{minimal_content}'")
    print()

    should_use_vision = TableDetector.should_use_vision_for_tables(documents, ".pdf")

    print(f"🔮 Vision processing recommended: {should_use_vision}")

    if should_use_vision:
        print("✅ SUCCESS: Vision processing will be used for minimal text")
    else:
        print("❌ FAILURE: Vision processing will NOT be used for minimal text")

    return should_use_vision


if __name__ == "__main__":
    print("🚀 Enhanced Table Processing Detection Test")
    print("=" * 50)

    # Test APA sample detection (this should trigger vision processing)
    apa_result = test_apa_sample_detection()

    # Test minimal text detection
    minimal_result = test_minimal_text_detection()

    print("\n📊 Test Results Summary:")
    print(f"APA Sample Tables: {'✅ PASS' if apa_result else '❌ FAIL'}")
    print(f"Minimal Text: {'✅ PASS' if minimal_result else '❌ FAIL'}")

    if apa_result and minimal_result:
        print(
            "\n🎉 All tests passed! Enhanced detection should work for image-heavy content."
        )
    else:
        print(
            "\n⚠️  Some tests failed. The detection logic may need further adjustment."
        )
