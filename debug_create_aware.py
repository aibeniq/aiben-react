#!/usr/bin/env python3
"""Check what happens in create_table_aware_documents"""

import sys
import os

# Add the backend to the path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.table_aware_processing import TableAwareProcessor


def debug_create_table_aware():
    """Debug create_table_aware_documents method"""
    print("=== Debug create_table_aware_documents ===")

    pdf_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"✅ PDF found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Create processor
    processor = TableAwareProcessor()

    # Override the methods with debugging
    original_pdf_extract = processor.extract_tables_from_pdf_bytes
    original_text_extract = processor._extract_tables_from_text

    def debug_pdf_extract(*args, **kwargs):
        print(f"   📊 Called extract_tables_from_pdf_bytes")
        result = original_pdf_extract(*args, **kwargs)
        print(f"   📊 PDF extraction returned {len(result)} tables")
        if result:
            print(f"      First table ID: {result[0]['table_id']}")
            print(f"      First table headers: {result[0]['headers']}")
        return result

    def debug_text_extract(*args, **kwargs):
        print(f"   📝 Called _extract_tables_from_text")
        result = original_text_extract(*args, **kwargs)
        print(f"   📝 Text extraction returned {len(result)} tables")
        if result:
            print(f"      First table ID: {result[0]['table_id']}")
            print(f"      First table headers: {result[0]['headers']}")
        return result

    processor.extract_tables_from_pdf_bytes = debug_pdf_extract
    processor._extract_tables_from_text = debug_text_extract

    # Now call create_table_aware_documents
    print(f"\n🔍 Calling create_table_aware_documents...")
    documents = processor.create_table_aware_documents(pdf_bytes, "test.pdf")

    print(f"\n📊 Final result: {len(documents)} documents created")
    if documents:
        first_doc = documents[0]
        print(
            f"   First document content type: {first_doc.metadata.get('content_type')}"
        )
        print(f"   First document table ID: {first_doc.metadata.get('table_id')}")
        print(f"   First document headers: {first_doc.metadata.get('headers')}")


if __name__ == "__main__":
    debug_create_table_aware()
