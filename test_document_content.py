#!/usr/bin/env python3
"""Test document content for table-aware processing"""

import sys
import os

# Add the backend to the path
backend_path = os.path.abspath("backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.services.table_aware_processing import TableAwareProcessor


def test_document_content():
    """Test the actual content of created documents"""
    print("=== Document Content Analysis ===")

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

    # Analyze document content
    us_equity_docs = []
    smart_docs = []
    all_inclusive_docs = []

    for doc in documents:
        content = doc.page_content.lower()

        # Look for US equity-related content
        if any(
            term in content for term in ["united states", "us equities", "usd", "usa"]
        ):
            us_equity_docs.append(doc)

        # Look for plan-specific content
        if "smart" in content:
            smart_docs.append(doc)
        if "all-inclusive" in content or "all inclusive" in content:
            all_inclusive_docs.append(doc)

    print(f"\n🔍 Content Analysis:")
    print(f"   • US equity related docs: {len(us_equity_docs)}")
    print(f"   • Smart plan docs: {len(smart_docs)}")
    print(f"   • All-inclusive plan docs: {len(all_inclusive_docs)}")

    # Show sample US equity content
    if us_equity_docs:
        print(f"\n📋 Sample US equity document content:")
        for i, doc in enumerate(us_equity_docs[:3]):
            print(f"   Document {i+1} ({doc.metadata.get('content_type', 'unknown')}):")
            content_preview = doc.page_content[:300].replace("\n", " ")
            print(f"   {content_preview}...")
            print()

    # Check for documents that mention both plans
    both_plans_docs = []
    for doc in documents:
        content = doc.page_content.lower()
        if "smart" in content and (
            "all-inclusive" in content or "all inclusive" in content
        ):
            both_plans_docs.append(doc)

    print(f"🎯 Documents with both Smart and All-inclusive: {len(both_plans_docs)}")

    if both_plans_docs:
        print("\n📋 Sample document with both plans:")
        doc = both_plans_docs[0]
        print(f"   Type: {doc.metadata.get('content_type', 'unknown')}")
        print(f"   Content preview:")
        content_preview = doc.page_content[:500].replace("\n", " ")
        print(f"   {content_preview}...")

    return len(documents) > 0


if __name__ == "__main__":
    success = test_document_content()
    if success:
        print("✅ Document content analysis complete")
    else:
        print("❌ Document content analysis failed")
