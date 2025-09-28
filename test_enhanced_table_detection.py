#!/usr/bin/env python3
"""
Test script to validate the enhanced table detection for financial schedules.
This demonstrates that the fix for "Appendix 6 Fee Schedule.pdf" is working.
"""

import sys
import os

sys.path.append(os.path.join(os.getcwd(), "backend"))

from backend.app.services.table_detection import TableDetector
from backend.app.services.document_utils import extract_documents_from_file_unified


def test_enhanced_table_detection():
    """Test enhanced table detection on the Fee Schedule PDF"""

    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False

    print(f"🔍 Testing enhanced table detection on: {file_path}")

    # Load file content
    with open(file_path, "rb") as f:
        file_content = f.read()

    # Extract documents
    documents = extract_documents_from_file_unified(
        file_content, "Appendix 6 Fee Schedule.pdf"
    )
    print(f"📄 Loaded {len(documents)} document chunks")

    # Test table detection
    table_pages = TableDetector.identify_table_pages(documents)
    print(f"📊 Table pages detected: {len(table_pages)} pages - {table_pages}")

    # Test vision recommendation
    should_use_vision = TableDetector.should_use_vision_for_tables(documents, ".pdf")
    print(f"🔮 Should use vision processing: {should_use_vision}")

    # Analyze financial content
    financial_pages = 0
    complex_pages = 0

    for i, doc in enumerate(documents):
        page_num = doc.metadata.get("page", i + 1)
        has_tables = TableDetector.detect_tables_in_text(doc.page_content)

        if has_tables:
            analysis = TableDetector.analyze_table_complexity(doc.page_content)
            financial_density = analysis.get("financial_density", 0)
            complexity = analysis.get("complexity", "simple")

            if financial_density > 0:
                financial_pages += 1
            if complexity in ["medium", "complex"]:
                complex_pages += 1

    print(f"💰 Pages with financial content: {financial_pages}")
    print(f"⚙️  Pages with medium/complex tables: {complex_pages}")

    # Validation checks
    success = True

    if len(table_pages) < 5:  # Should detect tables on most pages
        print("❌ FAIL: Too few table pages detected")
        success = False
    else:
        print("✅ PASS: Table detection working")

    if not should_use_vision:
        print("❌ FAIL: Vision processing not recommended")
        success = False
    else:
        print("✅ PASS: Vision processing recommended")

    if financial_pages < 5:  # Should detect financial content on most pages
        print("❌ FAIL: Too few pages with financial content detected")
        success = False
    else:
        print("✅ PASS: Financial schedule detection working")

    return success


def test_original_vs_enhanced():
    """Compare original vs enhanced detection patterns"""

    # Sample financial schedule text from the PDF
    sample_text = """
    Transaction fees                                 0.12%
    Custody fee                                      USD 600 per annum
    Settlement fees                                  free of charge
    Administrative fee                               USD 50 per transaction
    Monthly account fee                              0.25%
    Wire transfer fee                               USD 25 each
    """

    print("\n🔬 Testing detection patterns on sample financial text:")
    print(sample_text.strip())

    # Test basic table detection
    has_tables = TableDetector.detect_tables_in_text(sample_text)
    print(f"📊 Basic table detection: {has_tables}")

    # Test complexity analysis
    if has_tables:
        analysis = TableDetector.analyze_table_complexity(sample_text)
        print(f"📈 Analysis results:")
        print(f"   Complexity: {analysis.get('complexity')}")
        print(f"   Financial rows: {analysis.get('financial_rows', 0)}")
        print(f"   Financial density: {analysis.get('financial_density', 0):.2f}")
        print(f"   Regular rows: {analysis.get('estimated_rows', 0)}")
        print(f"   Estimated columns: {analysis.get('estimated_columns', 0)}")

    return has_tables


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ENHANCED TABLE DETECTION TEST SUITE")
    print("=" * 60)

    # Test 1: Sample text patterns
    test1_pass = test_original_vs_enhanced()

    print("\n" + "=" * 60)

    # Test 2: Full PDF processing
    test2_pass = test_enhanced_table_detection()

    print("\n" + "=" * 60)

    if test1_pass and test2_pass:
        print("🎉 ALL TESTS PASSED! Enhanced table detection is working correctly.")
        print("✅ The Fee Schedule PDF issue has been resolved!")
    else:
        print("❌ Some tests failed. Check the output above for details.")

    print("=" * 60)
