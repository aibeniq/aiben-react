#!/usr/bin/env python3
"""Debug document content for table-aware processing"""

import sys
import os

# Add the backend to the path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.table_aware_processing import TableAwareProcessor


def debug_document_content():
    """Debug the actual content of created documents"""
    print("=== Document Content Debug ===")

    # Test with the actual PDF
    pdf_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"✅ PDF found: {pdf_path}")

    # Create table processor
    processor = TableAwareProcessor()

    # Extract documents
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    documents = processor.create_table_aware_documents(pdf_bytes, "pdf")

    print(f"📊 Created {len(documents)} documents")

    # Show first few documents
    print(f"\n📋 First 10 document samples:")
    for i, doc in enumerate(documents[:10]):
        content_type = doc.metadata.get("content_type", "unknown")
        table_id = doc.metadata.get("table_id", "N/A")

        print(f"\n   Document {i+1}:")
        print(f"   Type: {content_type}")
        print(f"   Table ID: {table_id}")
        print(f"   Content length: {len(doc.page_content)} chars")
        print(f"   Content preview: {repr(doc.page_content[:200])}")

    # Look for specific content
    print(f"\n🔍 Searching for key terms:")

    smart_found = False
    all_inclusive_found = False
    us_found = False

    for i, doc in enumerate(documents):
        content = doc.page_content

        if "Smart" in content and not smart_found:
            print(f"\n   ✅ Found 'Smart' in document {i+1}:")
            print(f"   Type: {doc.metadata.get('content_type', 'unknown')}")
            print(f"   Content: {repr(content[:300])}")
            smart_found = True

        if "All-inclusive" in content and not all_inclusive_found:
            print(f"\n   ✅ Found 'All-inclusive' in document {i+1}:")
            print(f"   Type: {doc.metadata.get('content_type', 'unknown')}")
            print(f"   Content: {repr(content[:300])}")
            all_inclusive_found = True

        if "United States" in content and not us_found:
            print(f"\n   ✅ Found 'United States' in document {i+1}:")
            print(f"   Type: {doc.metadata.get('content_type', 'unknown')}")
            print(f"   Content: {repr(content[:300])}")
            us_found = True

        if smart_found and all_inclusive_found and us_found:
            break

    return len(documents) > 0


if __name__ == "__main__":
    success = debug_document_content()
    if success:
        print("\n✅ Document content debug complete")
    else:
        print("\n❌ Document content debug failed")
