#!/usr/bin/env python3
"""
Direct test of table processing with actual PDF - bypassing settings issues.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append("backend")


def test_pdf_table_extraction_direct():
    """Test PDF table extraction directly without settings dependencies."""

    print("🔧 Direct PDF Table Extraction Test")
    print("=" * 45)

    # Check if PDF exists
    pdf_path = Path("test_files/Appendix 6 Fee Schedule.pdf")

    if not pdf_path.exists():
        print(f"❌ PDF not found at: {pdf_path}")
        return False

    print(f"✅ PDF found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    print(f"📊 File size: {len(pdf_bytes)} bytes")

    try:
        print("\n1. Testing pdfplumber extraction")
        print("-" * 35)

        try:
            import pdfplumber
            from io import BytesIO

            print("✅ pdfplumber available")

            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                print(f"📄 PDF has {len(pdf.pages)} pages")

                tables_found = 0
                for page_num, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    print(f"   Page {page_num + 1}: {len(tables)} tables")
                    tables_found += len(tables)

                    if tables:
                        for i, table in enumerate(tables):
                            print(
                                f"     Table {i+1}: {len(table)} rows, {len(table[0]) if table else 0} columns"
                            )
                            if table and len(table) > 0:
                                print(f"       Headers: {table[0]}")
                                if len(table) > 1:
                                    print(f"       Sample row: {table[1]}")

                    # Also show raw text to understand structure
                    if page_num == 0:  # First page
                        text = page.extract_text()
                        if text:
                            print(f"   Page 1 text preview:")
                            lines = text.split("\n")[:15]
                            for line in lines:
                                if line.strip():
                                    separators = line.count("|") + line.count("\t")
                                    print(f"     {separators} seps: {line.strip()}")

                print(f"\n📊 Total tables found: {tables_found}")

                if tables_found == 0:
                    print("❌ No tables detected by pdfplumber")
                    print(
                        "   This suggests the PDF doesn't have clear table boundaries"
                    )
                    print("   Will need to rely on text-based detection")
                else:
                    print(
                        "✅ Tables detected - should work with table-aware processing"
                    )

        except ImportError:
            print("❌ pdfplumber not available")
            return False

        print("\n2. Testing table-aware processor directly")
        print("-" * 42)

        from app.services.table_aware_processing import TableAwareProcessor

        # Create processor with explicit settings to avoid config issues
        processor = TableAwareProcessor(
            preserve_headers=True,
            max_table_rows=1000,
            max_row_documents=50,
            enable_json_format=True,
            enable_structured_format=True,
            enable_row_documents=True,
        )

        print("✅ Table processor created")

        # Test PDF table extraction
        pdf_tables = processor.extract_tables_from_pdf_bytes(
            pdf_bytes, "Appendix 6 Fee Schedule.pdf"
        )

        print(f"📊 PDF table extraction found: {len(pdf_tables)} tables")

        if pdf_tables:
            for i, table in enumerate(pdf_tables):
                headers = table.get("headers", [])
                rows = table.get("rows", [])
                print(f"   Table {i+1}: {len(headers)} headers, {len(rows)} rows")
                print(f"     Headers: {headers}")

                # Check if we have the expected fee schedule structure
                if any("smart" in str(h).lower() for h in headers):
                    print("     ✅ Contains 'Smart' column!")
                if any("inclusive" in str(h).lower() for h in headers):
                    print("     ✅ Contains 'All-Inclusive' column!")

                # Check for equities data in rows (rows are dict objects in our processed format)
                has_equities = False
                for row in rows:
                    if isinstance(row, dict):
                        for value in row.values():
                            if "equities" in str(value).lower():
                                has_equities = True
                                break
                if has_equities:
                    print("     ✅ Contains US Equities data!")
        else:
            print("❌ No tables extracted from PDF")

        # Test creating table-aware documents
        print("\n3. Testing document creation")
        print("-" * 30)

        table_docs = processor.create_table_aware_documents(
            pdf_bytes, "Appendix 6 Fee Schedule.pdf"
        )

        print(f"📊 Created {len(table_docs)} documents")

        # Analyze what was created
        doc_types = {}
        for doc in table_docs:
            content_type = doc.metadata.get("content_type", "unknown")
            doc_types[content_type] = doc_types.get(content_type, 0) + 1

        print(f"📋 Document types:")
        for doc_type, count in doc_types.items():
            print(f"   • {doc_type}: {count}")

        # Look for US equities
        us_equity_docs = [
            doc for doc in table_docs if "us equities" in doc.page_content.lower()
        ]
        print(f"\n🔍 US equity documents: {len(us_equity_docs)}")

        # Check for context preservation
        context_docs = []
        for doc in us_equity_docs:
            content = doc.page_content.lower()
            if "smart" in content and (
                "all-inclusive" in content or "all inclusive" in content
            ):
                context_docs.append(doc)

        print(f"✅ Documents with both plan contexts: {len(context_docs)}")

        if context_docs:
            print("\n💪 SUCCESS! Sample preserved context:")
            sample = context_docs[0]
            print("-" * 50)
            print(sample.page_content[:300] + "...")
            print("-" * 50)
            return True
        else:
            print("\n❌ Context not preserved")

            # Show what we do have
            if us_equity_docs:
                print("Sample US equity document:")
                print(us_equity_docs[0].page_content[:200] + "...")

        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_table_extraction_direct()

    if success:
        print(f"\n🎉 PDF table processing is working!")
        print("The issue should be resolved for new knowledge bases.")
    else:
        print(f"\n💥 PDF table processing needs more work.")
