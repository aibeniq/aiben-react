#!/usr/bin/env python3
"""Detailed debugging of table processing corruption"""

import sys
import os

# Add the backend to the path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.table_aware_processing import TableAwareProcessor


def debug_table_corruption():
    """Debug where table data gets corrupted"""
    print("=== Table Corruption Debug ===")

    pdf_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"✅ PDF found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Create processor with debugging
    processor = TableAwareProcessor()

    # Test each step in isolation
    print(f"\n🔍 Step 1: PDF table extraction")
    tables = processor.extract_tables_from_pdf_bytes(pdf_bytes, "test.pdf")

    if tables:
        table = tables[0]
        print(f"   ✅ Extracted table:")
        print(f"   Table ID: {table['table_id']}")
        print(f"   Headers: {table['headers']}")
        print(f"   Structured text preview: {table['structured_text'][:200]}")

        # Test document creation from this specific table
        print(f"\n🔍 Step 2: Document creation from extracted table")

        # Mock the document creation process
        from langchain_core.documents import Document

        # Structured document
        doc_structured = Document(
            page_content=table["structured_text"],
            metadata={
                **table["metadata"],
                "content_type": "table_structured",
                "table_id": table["table_id"],
                "headers": table["headers"],
            },
        )

        print(f"   ✅ Created structured document:")
        print(f"   Content preview: {repr(doc_structured.page_content[:200])}")
        print(f"   Metadata: {doc_structured.metadata}")

        # Compare the headers
        print(f"\n🔍 Header comparison:")
        print(f"   Original headers: {table['headers']}")
        print(
            f"   Document metadata headers: {doc_structured.metadata.get('headers', 'N/A')}"
        )

    else:
        print(f"   ❌ No tables extracted")


if __name__ == "__main__":
    debug_table_corruption()
