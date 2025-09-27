#!/usr/bin/env python3
"""
Debug script to understand why table-aware processing isn't working for the actual PDF file.
This will help us identify where the process is failing.
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append("backend")


def debug_pdf_processing():
    """Debug the PDF processing pipeline to identify issues."""

    print("🔍 Debugging PDF Table Processing")
    print("=" * 50)

    # Check if the PDF file exists
    pdf_path = Path("test_files/Appendix 6 Fee Schedule.pdf")

    if not pdf_path.exists():
        print(f"❌ PDF file not found at: {pdf_path}")
        print("Creating a mock PDF content for testing...")

        # Create mock PDF-like content that should trigger table processing
        mock_pdf_content = """APPENDIX 6 - FEE SCHEDULE

Service Type | Smart | All-Inclusive
US Equities | 0.08% of total trade value BUT minimum per trade 0.2 EUR/USD | 0.5% of the volume of each transaction  
US Stock options | 0.65 USD per contract | 3 USD per contract + 10 USD per order
Exchange-traded futures and options | 1.5 USD/EUR per contract | 1.5 USD/EUR per contract
"""
        pdf_bytes = mock_pdf_content.encode("utf-8")
        filename = "Mock_Appendix_6_Fee_Schedule.pdf"
    else:
        print(f"✅ PDF file found at: {pdf_path}")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        filename = pdf_path.name

    print(f"📄 Processing file: {filename}")
    print(f"📊 File size: {len(pdf_bytes)} bytes")

    try:
        print("\n1. Testing Regular PDF Processing")
        print("-" * 40)

        from app.services.document_utils import extract_documents_from_file_unified

        regular_docs = extract_documents_from_file_unified(pdf_bytes, filename)
        print(f"📊 Regular processing created: {len(regular_docs)} documents")

        if regular_docs:
            content_preview = regular_docs[0].page_content[:500]
            print(f"📝 Content preview:\n{content_preview}...")

            # Check if this content shows the problematic pattern
            if "0.08%" in content_preview and "Smart" not in content_preview:
                print("❌ CONFIRMED: Regular processing loses column header context!")

        print("\n2. Testing Table-Aware Processing")
        print("-" * 40)

        # Test the table-aware processing step by step
        try:
            from app.services.table_aware_processing import (
                enhance_document_with_tables,
                get_table_processor,
            )

            print("✅ Table-aware modules imported successfully")

            # Get the processor
            processor = get_table_processor()
            print(f"✅ Table processor created with settings:")
            print(f"   - preserve_headers: {processor.preserve_headers}")
            print(f"   - max_table_rows: {processor.max_table_rows}")
            print(f"   - enable_json_format: {processor.enable_json_format}")
            print(
                f"   - enable_structured_format: {processor.enable_structured_format}"
            )
            print(f"   - enable_row_documents: {processor.enable_row_documents}")

            # Test the enhancement function
            enhanced_docs = enhance_document_with_tables(pdf_bytes, filename)
            print(f"📊 Table-aware processing created: {len(enhanced_docs)} documents")

            # Analyze document types
            doc_types = {}
            table_docs = 0
            for doc in enhanced_docs:
                content_type = doc.metadata.get("content_type", "unknown")
                doc_types[content_type] = doc_types.get(content_type, 0) + 1

                if "table" in content_type:
                    table_docs += 1

            print(f"📋 Document types created:")
            for doc_type, count in doc_types.items():
                print(f"   • {doc_type}: {count}")

            print(f"📊 Table-specific documents: {table_docs}")

            if table_docs == 0:
                print("❌ NO TABLE DOCUMENTS CREATED - This is the problem!")
                print("   The PDF table extraction is not working properly.")

                print("\n3. Testing PDF Table Extraction Directly")
                print("-" * 45)

                # Test pdfplumber directly
                try:
                    import pdfplumber
                    from io import BytesIO

                    print("✅ pdfplumber is available")

                    if filename.endswith(".pdf") and not filename.startswith("Mock_"):
                        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                            print(f"📄 PDF has {len(pdf.pages)} pages")

                            for page_num, page in enumerate(pdf.pages):
                                tables = page.extract_tables()
                                print(
                                    f"   Page {page_num + 1}: {len(tables)} tables found"
                                )

                                if tables:
                                    for i, table in enumerate(tables):
                                        print(f"     Table {i + 1}: {len(table)} rows")
                                        if table:
                                            print(f"     Sample row: {table[0]}")
                                else:
                                    # Try extracting text to see the structure
                                    text = page.extract_text()
                                    if text:
                                        lines = text.split("\n")[:10]
                                        print(f"     Text sample (first 10 lines):")
                                        for line in lines:
                                            print(f"       {line}")
                    else:
                        print("⚠️  Using mock content, cannot test pdfplumber directly")

                except ImportError:
                    print("❌ pdfplumber not available")

                print("\n4. Testing Text-Based Table Detection")
                print("-" * 40)

                # Test the fallback text processing
                if regular_docs:
                    text = regular_docs[0].page_content
                    processor = get_table_processor()
                    text_tables = processor._extract_tables_from_text(text, filename)

                    print(
                        f"📊 Text-based table extraction found: {len(text_tables)} tables"
                    )

                    if text_tables:
                        for i, table in enumerate(text_tables):
                            headers = table.get("headers", [])
                            rows = table.get("rows", [])
                            print(
                                f"   Table {i + 1}: {len(headers)} headers, {len(rows)} rows"
                            )
                            print(f"   Headers: {headers}")
                    else:
                        print("❌ Text-based extraction also failed to find tables")

                        # Show what the text looks like
                        print("\n📝 Raw text analysis:")
                        lines = text.split("\n")
                        for i, line in enumerate(lines[:20]):
                            if line.strip():
                                separators = (
                                    line.count("|")
                                    + line.count("\t")
                                    + line.count("  ")
                                )
                                print(
                                    f"   Line {i+1}: {separators} separators - '{line.strip()}'"
                                )

            else:
                print("✅ Table documents were created successfully!")

                # Show sample table document
                for doc in enhanced_docs:
                    if "table" in doc.metadata.get("content_type", ""):
                        print(
                            f"\n📋 Sample table document ({doc.metadata.get('content_type')}):"
                        )
                        print(doc.page_content[:300] + "...")
                        break

        except Exception as e:
            print(f"❌ Error in table-aware processing: {e}")
            import traceback

            traceback.print_exc()

        print("\n3. Testing Full Pipeline")
        print("-" * 25)

        from app.services.document_utils import extract_documents_from_file_table_aware

        pipeline_docs = extract_documents_from_file_table_aware(pdf_bytes, filename)
        print(f"📊 Full pipeline created: {len(pipeline_docs)} documents")

        # Check if we get table-specific documents
        table_pipeline_docs = [
            doc
            for doc in pipeline_docs
            if "table" in doc.metadata.get("content_type", "")
        ]

        if table_pipeline_docs:
            print("✅ Pipeline successfully created table documents!")
        else:
            print(
                "❌ Pipeline did NOT create table documents - falling back to regular processing"
            )

        print("\n4. Search Simulation")
        print("-" * 20)

        # Simulate searching for US equities
        us_equity_docs = []
        for doc in pipeline_docs:
            if "us equities" in doc.page_content.lower():
                us_equity_docs.append(doc)

        print(f"🔍 Found {len(us_equity_docs)} documents mentioning 'US equities'")

        for i, doc in enumerate(us_equity_docs[:2]):
            content_type = doc.metadata.get("content_type", "unknown")
            print(f"\n📄 Document {i+1} ({content_type}):")
            print(doc.page_content[:200] + "...")

            # Check if Smart/All-Inclusive context is preserved
            content_lower = doc.page_content.lower()
            has_smart = "smart" in content_lower
            has_all_inclusive = "all-inclusive" or "all inclusive" in content_lower

            print(f"   Contains 'Smart': {has_smart}")
            print(f"   Contains 'All-Inclusive': {has_all_inclusive}")

            if has_smart and has_all_inclusive:
                print("   ✅ Both plan types mentioned - context preserved!")
            elif has_smart or has_all_inclusive:
                print("   ⚠️  Only one plan type mentioned - partial context")
            else:
                print("   ❌ No plan types mentioned - context lost!")

        return True

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = debug_pdf_processing()

    if success:
        print(f"\n🔍 Debug complete. Check the output above to identify the issue.")
    else:
        print(f"\n💥 Debug failed.")
