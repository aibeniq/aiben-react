#!/usr/bin/env python3
"""Test if regular document extraction is interfering"""

import sys
import os

# Add the backend to the path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.table_aware_processing import (
    TableAwareProcessor,
    enhance_document_with_tables,
)


def debug_document_interaction():
    """Debug if there's interference between regular and table-aware processing"""
    print("=== Debug Document Interaction ===")

    pdf_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"✅ PDF found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    # Test 1: Table-aware processing alone
    print(f"\n🔍 Test 1: Table-aware processing only")
    processor = TableAwareProcessor()
    table_docs = processor.create_table_aware_documents(pdf_bytes, "test.pdf")

    print(f"   Created {len(table_docs)} table-aware documents")
    if table_docs:
        first_doc = table_docs[0]
        print(f"   First doc table ID: {first_doc.metadata.get('table_id')}")
        print(f"   First doc headers: {first_doc.metadata.get('headers')}")
        print(f"   Content preview: {repr(first_doc.page_content[:100])}")

    # Test 2: Enhanced processing (both regular + table-aware)
    print(f"\n🔍 Test 2: Enhanced processing (regular + table-aware)")
    enhanced_docs = enhance_document_with_tables(pdf_bytes, "test.pdf")

    print(f"   Created {len(enhanced_docs)} enhanced documents")

    # Find table documents in enhanced results
    table_enhanced_docs = [
        doc
        for doc in enhanced_docs
        if doc.metadata.get("content_type", "").startswith("table_")
    ]

    print(f"   Table documents in enhanced: {len(table_enhanced_docs)}")
    if table_enhanced_docs:
        first_table_doc = table_enhanced_docs[0]
        print(f"   First table doc ID: {first_table_doc.metadata.get('table_id')}")
        print(f"   First table doc headers: {first_table_doc.metadata.get('headers')}")
        print(f"   Content preview: {repr(first_table_doc.page_content[:100])}")


if __name__ == "__main__":
    debug_document_interaction()
