#!/usr/bin/env python3
"""Test table processing step by step"""

import sys
import os

# Add the backend to the path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import pdfplumber
from io import BytesIO
from app.services.table_aware_processing import TableAwareProcessor


def test_step_by_step():
    """Test table processing step by step"""
    print("=== Step-by-Step Table Processing Test ===")

    pdf_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"✅ PDF found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Step 1: Test direct pdfplumber extraction
    print(f"\n📋 Step 1: Direct pdfplumber extraction")
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        raw_table = tables[0]

        print(f"   Raw table headers: {raw_table[0]}")
        print(f"   Raw table first row: {raw_table[1]}")

    # Step 2: Test our table extractor method
    print(f"\n📋 Step 2: Our extract_tables_from_pdf_bytes method")
    processor = TableAwareProcessor()
    extracted_tables = processor.extract_tables_from_pdf_bytes(pdf_bytes, "test.pdf")

    if extracted_tables:
        first_table = extracted_tables[0]
        print(f"   Extracted headers: {first_table.get('headers', 'N/A')}")
        print(f"   Table ID: {first_table.get('table_id', 'N/A')}")
        print(f"   Metadata: {first_table.get('metadata', 'N/A')}")
    else:
        print(f"   ❌ No tables extracted")

    # Step 3: Test document creation
    print(f"\n📋 Step 3: Document creation")
    documents = processor.create_table_aware_documents(pdf_bytes, "pdf")

    print(f"   Created {len(documents)} documents")
    if documents:
        first_doc = documents[0]
        print(
            f"   First document type: {first_doc.metadata.get('content_type', 'N/A')}"
        )
        print(f"   First document preview: {repr(first_doc.page_content[:200])}")


if __name__ == "__main__":
    test_step_by_step()
