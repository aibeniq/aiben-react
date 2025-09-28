#!/usr/bin/env python3
"""
Debug script to verify table metadata preservation fix.
This script tests the document chunking process to ensure table metadata is preserved.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from langchain.schema import Document
from app.services.smart_chunking import StructureAwareTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter


def test_table_metadata_preservation():
    """Test that table metadata is preserved during document chunking."""

    print("🧪 TESTING TABLE METADATA PRESERVATION")
    print("=" * 60)

    # Create test documents with table metadata
    test_docs = [
        Document(
            page_content="This is a document with table data. "
            * 50,  # Make it long enough to chunk
            metadata={
                "source_filename": "test.pdf",
                "page": 1,
                "has_table_data": True,
                "table_count": 3,
                "has_processed_tables": True,
                "processing_method": "vision_enhanced",
            },
        ),
        Document(
            page_content="This is another document with more table content. "
            * 50,  # Make it long enough to chunk
            metadata={
                "source_filename": "test.pdf",
                "page": 2,
                "has_table_data": True,
                "table_count": 2,
                "has_processed_tables": True,
                "processing_method": "vision_enhanced",
            },
        ),
        Document(
            page_content="This document has no tables. " * 30,
            metadata={
                "source_filename": "test.pdf",
                "page": 3,
            },
        ),
    ]

    print(f"📄 Created {len(test_docs)} test documents")
    for i, doc in enumerate(test_docs):
        has_table = doc.metadata.get("has_table_data", False)
        table_count = doc.metadata.get("table_count", 0)
        print(
            f"  Doc {i+1}: Page {doc.metadata.get('page')}, Has Tables: {has_table}, Count: {table_count}"
        )

    print("\n" + "=" * 60)

    # Test 1: RecursiveCharacterTextSplitter (old method)
    print("🔍 TEST 1: RecursiveCharacterTextSplitter (old method)")
    old_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
    old_chunks = old_splitter.split_documents(test_docs)

    old_table_chunks = sum(
        1 for chunk in old_chunks if chunk.metadata.get("has_table_data")
    )
    print(f"📊 Chunks created: {len(old_chunks)}")
    print(f"📋 Chunks with table metadata: {old_table_chunks}")

    if old_table_chunks > 0:
        print("✅ OLD METHOD: Table metadata preserved")
        for i, chunk in enumerate(old_chunks):
            if chunk.metadata.get("has_table_data"):
                print(
                    f"  Chunk {i}: Tables={chunk.metadata.get('table_count')}, Page={chunk.metadata.get('page')}"
                )
    else:
        print("❌ OLD METHOD: Table metadata LOST")

    print("\n" + "=" * 60)

    # Test 2: StructureAwareTextSplitter (new method)
    print("🔍 TEST 2: StructureAwareTextSplitter (new method)")
    new_splitter = StructureAwareTextSplitter(chunk_size=200, chunk_overlap=50)
    new_chunks = new_splitter.split_documents(test_docs)

    new_table_chunks = sum(
        1 for chunk in new_chunks if chunk.metadata.get("has_table_data")
    )
    print(f"📊 Chunks created: {len(new_chunks)}")
    print(f"📋 Chunks with table metadata: {new_table_chunks}")

    if new_table_chunks > 0:
        print("✅ NEW METHOD: Table metadata preserved")
        for i, chunk in enumerate(new_chunks):
            if chunk.metadata.get("has_table_data"):
                print(
                    f"  Chunk {i}: Tables={chunk.metadata.get('table_count')}, Page={chunk.metadata.get('page')}"
                )
    else:
        print("❌ NEW METHOD: Table metadata LOST")

    print("\n" + "=" * 60)

    # Summary
    print("📈 SUMMARY")
    print(
        f"  Original docs with table metadata: {sum(1 for doc in test_docs if doc.metadata.get('has_table_data'))}"
    )
    print(f"  Old method preserved: {old_table_chunks} chunks")
    print(f"  New method preserved: {new_table_chunks} chunks")

    if new_table_chunks > old_table_chunks:
        print("🎉 FIX SUCCESS: New method preserves more table metadata!")
    elif new_table_chunks == old_table_chunks and new_table_chunks > 0:
        print("✅ Both methods preserve table metadata equally")
    else:
        print("⚠️ Investigation needed: Metadata preservation issue")


if __name__ == "__main__":
    test_table_metadata_preservation()
