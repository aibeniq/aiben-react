#!/usr/bin/env python3
"""
Debug script to analyze table processing on the specific PDF file.
"""

import sys
import os
from pathlib import Path

# Add the backend app to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def debug_pdf_table_processing():
    """Debug the table processing on the specific PDF file."""
    print("🔍 Debugging Table Processing on Appendix 6 Fee Schedule.pdf")
    print("=" * 70)

    # Set up environment
    os.environ.setdefault("PROJECT_NAME", "debug")
    os.environ.setdefault("POSTGRES_SERVER", "localhost")
    os.environ.setdefault("POSTGRES_USER", "test")
    os.environ.setdefault("FIRST_SUPERUSER", "debug@example.com")
    os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "test")

    try:
        # Test file path
        test_file = Path(__file__).parent / "test_files" / "Appendix 6 Fee Schedule.pdf"

        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False

        print(f"📄 Found test file: {test_file.name}")
        print(f"📊 File size: {test_file.stat().st_size / 1024:.1f} KB")

        # Read file content
        with open(test_file, "rb") as f:
            file_content = f.read()

        print(f"✅ Successfully read {len(file_content)} bytes from PDF")

        # Step 1: Test basic document extraction
        print("\n📋 Step 1: Testing Basic Document Extraction")
        print("-" * 50)

        from app.services.document_utils import (
            extract_documents_and_images_from_file_unified,
        )

        documents, images = extract_documents_and_images_from_file_unified(
            file_content, test_file.name
        )

        print(f"✅ Extracted {len(documents)} documents")
        print(f"✅ Found {len(images)} images")

        if documents:
            total_text = sum(len(doc.page_content) for doc in documents)
            print(f"📊 Total text length: {total_text} characters")

            # Show first document content sample
            first_doc = documents[0].page_content
            preview = first_doc[:500] + "..." if len(first_doc) > 500 else first_doc
            print(f"📄 First document preview:\n{preview}\n")

        # Step 2: Test table detection
        print("\n🔍 Step 2: Testing Table Detection")
        print("-" * 50)

        from app.services.table_detection import TableDetector

        table_pages = []
        for i, doc in enumerate(documents):
            has_tables = TableDetector.detect_tables_in_text(doc.page_content)
            if has_tables:
                table_pages.append(i)
                analysis = TableDetector.analyze_table_complexity(doc.page_content)
                print(f"📊 Document {i}: Tables detected - {analysis}")
            else:
                print(f"📄 Document {i}: No tables detected")

        print(f"\n🎯 Summary: Found tables on {len(table_pages)} pages: {table_pages}")

        # Step 3: Test vision capability
        print("\n👁️ Step 3: Testing Vision Capability")
        print("-" * 50)

        # Mock LLM for testing
        class MockVisionLLM:
            model_name = "gpt-4-vision-preview"

            def invoke(self, prompt):
                return "Mock vision response - tables detected and processed"

        from app.services.vision_service import VisionService

        mock_llm = MockVisionLLM()
        vision_enabled = VisionService.is_vision_enabled(mock_llm)
        print(f"✅ Vision enabled for mock LLM: {vision_enabled}")

        should_use_vision = TableDetector.should_use_vision_for_tables(
            documents, ".pdf"
        )
        print(f"📊 Should use vision for tables: {should_use_vision}")

        # Step 4: Test full table-aware processing
        print("\n🔧 Step 4: Testing Full Table-Aware Processing")
        print("-" * 50)

        from app.services.document_utils import extract_documents_with_table_processing

        # Test without LLM first
        processed_docs_no_llm, table_data_no_llm = (
            extract_documents_with_table_processing(
                file_content, test_file.name, llm=None
            )
        )

        print(f"📄 Without LLM: {len(processed_docs_no_llm)} processed documents")
        print(f"📊 Without LLM: Table data contains {len(table_data_no_llm)} keys")

        # Test with mock LLM
        processed_docs_llm, table_data_llm = extract_documents_with_table_processing(
            file_content, test_file.name, llm=mock_llm
        )

        print(f"📄 With LLM: {len(processed_docs_llm)} processed documents")
        print(f"📊 With LLM: Table data contains {len(table_data_llm)} keys")

        if table_data_llm.get("tables"):
            print(f"🎉 SUCCESS: Extracted {len(table_data_llm['tables'])} tables!")
            for i, table in enumerate(table_data_llm["tables"]):
                print(f"   Table {i+1}: {table.get('summary', 'No summary')}")
        else:
            print("❌ No tables extracted with vision processing")

        # Step 5: Check for common issues
        print("\n🔍 Step 5: Diagnostic Checks")
        print("-" * 50)

        # Check if PDF has extractable text
        if not documents or all(
            len(doc.page_content.strip()) < 50 for doc in documents
        ):
            print(
                "⚠️ WARNING: PDF may be image-only or have very little extractable text"
            )

        # Check if images were extracted
        if not images:
            print(
                "⚠️ WARNING: No images extracted from PDF - vision processing won't work"
            )
        else:
            print(f"✅ {len(images)} images available for vision processing")

        # Check table detection patterns
        all_text = " ".join(doc.page_content for doc in documents)

        # Look for common table indicators
        indicators = {
            "pipe_tables": all_text.count("|"),
            "dollar_signs": all_text.count("$"),
            "percentages": all_text.count("%"),
            "numbers": len([c for c in all_text if c.isdigit()]),
            "fee_words": all_text.lower().count("fee")
            + all_text.lower().count("cost")
            + all_text.lower().count("rate"),
        }

        print("\n📊 Text Analysis:")
        for key, count in indicators.items():
            print(f"   {key}: {count}")

        return True

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = debug_pdf_table_processing()
    print("\n" + "=" * 70)
    if success:
        print("🎉 Debug completed successfully!")
    else:
        print("💥 Debug failed - check the errors above")
