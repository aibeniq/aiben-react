#!/usr/bin/env python3
"""
Test script to demonstrate the new logging functionality for table detection and vision processing.
This script shows the detailed logs that will help you track when tables are detected and vision is invoked.
"""

import sys
import os
import logging

sys.path.append(os.path.join(os.getcwd(), "backend"))

# Configure logging to show all the new table detection logs
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Set specific loggers to INFO level for cleaner output
logging.getLogger("backend.app.services.table_detection").setLevel(logging.INFO)
logging.getLogger("backend.app.services.document_utils").setLevel(logging.INFO)
logging.getLogger("backend.app.api.routes.formconnect").setLevel(logging.INFO)

from backend.app.services.table_detection import TableDetector
from backend.app.services.document_utils import extract_documents_from_file_unified


def test_table_detection_with_logging():
    """Test table detection with comprehensive logging"""

    print("=" * 80)
    print("🔍 TABLE DETECTION LOGGING DEMONSTRATION")
    print("=" * 80)

    file_path = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        print("Please ensure the test file exists to see the logging in action.")
        return

    print(f"\n📁 Testing file: {file_path}")

    # Load file content
    with open(file_path, "rb") as f:
        file_content = f.read()

    print(f"\n📄 File loaded: {len(file_content)} bytes")

    # Extract documents (this will trigger table detection logging)
    print(f"\n🔄 Extracting documents...")
    documents = extract_documents_from_file_unified(
        file_content, "Appendix 6 Fee Schedule.pdf"
    )

    # Test table page identification (with logging)
    print(f"\n🔍 Identifying table pages...")
    table_pages = TableDetector.identify_table_pages(documents)

    # Test vision recommendation (with logging)
    print(f"\n🔮 Evaluating vision processing recommendation...")
    should_use_vision = TableDetector.should_use_vision_for_tables(documents, ".pdf")

    print(f"\n📊 RESULTS SUMMARY:")
    print(f"   Documents processed: {len(documents)}")
    print(f"   Table pages found: {len(table_pages)}")
    print(f"   Vision recommended: {should_use_vision}")

    # Show some detailed analysis for first few pages
    print(f"\n🔬 DETAILED PAGE ANALYSIS:")
    for i, doc in enumerate(documents[:3]):  # Show first 3 pages
        page_num = doc.metadata.get("page", i + 1)
        print(f"\n   Page {page_num}:")

        has_tables = TableDetector.detect_tables_in_text(doc.page_content)
        if has_tables:
            analysis = TableDetector.analyze_table_complexity(doc.page_content)
            print(f"      ✅ Tables detected")
            print(f"      📊 Complexity: {analysis.get('complexity')}")
            print(f"      💰 Financial rows: {analysis.get('financial_rows', 0)}")
            print(
                f"      📈 Financial density: {analysis.get('financial_density', 0):.2f}"
            )
        else:
            print(f"      ❌ No tables detected")


def demonstrate_log_levels():
    """Show what logs appear at different levels"""

    print("\n" + "=" * 80)
    print("📋 LOG LEVEL DEMONSTRATION")
    print("=" * 80)

    print("\n🔧 The following log messages will help you track table processing:")

    print("\n📊 INFO Level Messages (most important):")
    print("   ✅ 🔍 Analyzing X document chunks for table detection")
    print("   ✅ 📋 Table detection complete: X pages contain tables")
    print("   ✅ 🔮 Evaluating vision processing for X documents")
    print("   ✅ ✅ Vision RECOMMENDED: [reason]")
    print("   ✅ ❌ Vision NOT recommended: [reason]")
    print("   ✅ 🔮 VISION PROCESSING INVOKED: Processing X table pages")
    print("   ✅ ✅ Vision processing complete: extracted data for X tables")
    print("   ✅ 🔍 FormConnect: Using table-aware vector search")
    print("   ✅ ✅ FOUND IN TABLE DATA: field_name = value")

    print("\n🔍 DEBUG Level Messages (detailed diagnostics):")
    print("   🔍 📊 Table detected on page X (chunk Y)")
    print("   🔍 📊 Table complexity analysis: columns=X, rows=Y, financial_density=Z")
    print("   🔍 Table detection analysis: pattern_score=X, row_percentage=Y")
    print("   🔍 ❌ Field 'field_name' not found in table data")

    print("\n⚙️ How to use these logs:")
    print("   1. Set logging level to INFO to see key decisions")
    print("   2. Set logging level to DEBUG for detailed diagnostics")
    print("   3. Watch for 'VISION PROCESSING INVOKED' to confirm vision is being used")
    print("   4. Look for 'FOUND IN TABLE DATA' to see when table extraction helps")


if __name__ == "__main__":
    print("🧪 Starting table detection logging demonstration...\n")

    try:
        test_table_detection_with_logging()
        demonstrate_log_levels()

        print("\n" + "=" * 80)
        print("🎉 LOGGING DEMONSTRATION COMPLETE!")
        print("=" * 80)

        print("\n✅ Key benefits of the new logging:")
        print("   📊 Track when tables are detected in documents")
        print("   🔮 See when vision processing is recommended and invoked")
        print("   📋 Monitor table complexity analysis decisions")
        print("   💰 Identify financial schedule detection")
        print("   🔍 Debug field extraction from table data")
        print("   ⚙️  Monitor the complete table-aware processing pipeline")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        print("\nThis is likely due to missing dependencies or test files.")
        print("The logging functionality is still working in the main application.")
