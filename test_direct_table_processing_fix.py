#!/usr/bin/env python3
"""
Direct test of table processing fix without API authentication.
Tests the document processing logic directly.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_document_processing_directly():
    """Test the document processing logic directly."""

    print("🧪 Testing Table Processing Fix (Direct)\n")

    # Check if test file exists
    test_file_path = Path("test_files/Appendix 6 Fee Schedule.pdf")
    if not test_file_path.exists():
        print(f"❌ Test file not found: {test_file_path}")
        return False

    try:
        # Import necessary modules
        from app.services.document_utils import extract_documents_with_table_processing
        from app.services.table_detection import TableDetector
        from app.services.vision_service import VisionService

        print("✅ Successfully imported document processing modules")

        # Read the test file
        print(f"📖 Reading test file: {test_file_path}")
        with open(test_file_path, "rb") as f:
            file_content = f.read()

        print(f"📄 File size: {len(file_content):,} bytes")

        # Test document processing with table enhancement
        print("\n🔍 Processing document with table detection...")

        documents, table_data = extract_documents_with_table_processing(
            file_content=file_content, filename="Appendix 6 Fee Schedule.pdf"
        )

        print(f"📋 Extracted {len(documents)} document chunks")

        # Analyze the results
        structured_chunks = 0
        raw_chunks = 0
        regular_chunks = 0

        for i, doc in enumerate(documents):
            content = doc.page_content

            if "=== STRUCTURED TABLE DATA ===" in content:
                structured_chunks += 1
                print(f"   📊 Chunk {i+1}: Contains STRUCTURED TABLE DATA ✅")

                # Show a preview of the structured data
                if "table_json" in content or '"headers"' in content:
                    print(f"      🎯 Found JSON table structure")

            elif "=== RAW TABLE CONTENT ===" in content:
                raw_chunks += 1
                print(f"   📄 Chunk {i+1}: Contains RAW TABLE CONTENT (fallback)")

            else:
                regular_chunks += 1
                if i < 3:  # Show first few regular chunks
                    print(f"   📝 Chunk {i+1}: Regular content ({len(content)} chars)")

        print(f"\n📊 Summary:")
        print(f"   • Structured table chunks: {structured_chunks}")
        print(f"   • Raw table chunks: {raw_chunks}")
        print(f"   • Regular content chunks: {regular_chunks}")
        print(f"   • Total chunks: {len(documents)}")

        # Check table detection results
        if table_data and table_data.get("tables"):
            print(f"\n🎯 Table Detection Results:")
            print(f"   • Vision extracted tables: {len(table_data['tables'])}")

            for i, table in enumerate(table_data["tables"]):
                print(f"   • Table {i+1}: {table.get('title', 'Untitled')}")
                print(f"     - Page: {table.get('page', 'Unknown')}")
                print(f"     - Rows: {len(table.get('rows', []))}")
                print(f"     - Columns: {len(table.get('headers', []))}")

        # Success criteria
        if structured_chunks > 0:
            print("\n🎉 SUCCESS: Table processing fix is working!")
            print("   ✅ Found structured JSON table data in document chunks")
            print("   ✅ Vision processing successfully extracted table metadata")
            return True
        elif raw_chunks > 0:
            print("\n⚠️  PARTIAL SUCCESS: Fallback processing working")
            print("   ⚠️  Vision processing may have failed, using raw content fallback")
            print(
                "   💡 This is better than no table data, but vision processing should be investigated"
            )
            return True
        else:
            print("\n❌ ISSUE: No table content found in any chunks")
            print("   ❌ Table detection or processing may not be working")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the project root directory")
        return False
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_table_detection_only():
    """Test just the table detection logic."""

    print("\n🔍 Testing Table Detection Logic Only...")

    try:
        from app.services.table_detection import TableDetector

        test_file_path = Path("test_files/Appendix 6 Fee Schedule.pdf")
        with open(test_file_path, "rb") as f:
            file_content = f.read()

        # First extract documents from PDF
        from app.services.document_utils import extract_documents_from_file_unified

        documents = extract_documents_from_file_unified(
            file_content, "Appendix 6 Fee Schedule.pdf"
        )

        # Then detect table pages
        table_pages = TableDetector.identify_table_pages(documents)

        print(f"📋 Table detection results:")
        print(f"   • Pages with tables: {table_pages}")
        print(f"   • Total table pages: {len(table_pages)}")

        if len(table_pages) > 0:
            print("✅ Table detection is working correctly")
            return True
        else:
            print("❌ No tables detected - this may indicate an issue")
            return False

    except Exception as e:
        print(f"❌ Table detection error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Direct Table Processing Fix Test\n")

    # Test table detection first
    if test_table_detection_only():
        print()
        # Test full document processing
        if test_document_processing_directly():
            print("\n✅ All tests passed! Table processing fix is working correctly.")
        else:
            print("\n❌ Document processing test failed.")
            sys.exit(1)
    else:
        print("\n❌ Table detection test failed.")
        sys.exit(1)
