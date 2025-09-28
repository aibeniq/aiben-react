#!/usr/bin/env python3
"""
Debug script to verify ChromaDB metadata storage and retrieval.
This script tests if table metadata is lost during ChromaDB operations.
"""

import sys
import os
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from app.services.embeddings import load_embeddings_model


def test_chromadb_metadata_preservation():
    """Test that table metadata is preserved during ChromaDB storage/retrieval."""

    print("🧪 TESTING CHROMADB METADATA PRESERVATION")
    print("=" * 60)

    # Create test documents with table metadata
    test_docs = [
        Document(
            page_content="This is a document with table data about financial schedules and fee structures.",
            metadata={
                "source_filename": "Appendix 6 Fee Schedule.pdf",
                "page": 1,
                "has_table_data": True,
                "table_count": 3,
                "has_processed_tables": True,
                "processing_method": "vision_enhanced",
            },
        ),
        Document(
            page_content="Another document chunk with complex table structures containing pricing information.",
            metadata={
                "source_filename": "Appendix 6 Fee Schedule.pdf",
                "page": 2,
                "has_table_data": True,
                "table_count": 2,
                "has_processed_tables": True,
                "processing_method": "vision_enhanced",
            },
        ),
        Document(
            page_content="This is a regular text chunk without any table data.",
            metadata={
                "source_filename": "Appendix 6 Fee Schedule.pdf",
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

    # Load embedding model
    print("\n🔗 Loading embedding model...")
    try:
        embeddings = load_embeddings_model(
            provider="openai", model_id="text-embedding-3-small"
        )
        print("✅ Embedding model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading embedding model: {e}")
        return

    # Create ChromaDB vector store
    print("\n📊 Creating ChromaDB vector store...")
    vector_dir = tempfile.mkdtemp()
    try:
        vector_store = Chroma.from_documents(
            documents=test_docs, embedding=embeddings, persist_directory=vector_dir
        )
        print(f"✅ Vector store created in {vector_dir}")
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        return

    # Test retrieval
    print("\n🔍 Testing metadata preservation through retrieval...")

    # Retrieve similar documents
    try:
        query = "table data financial information"
        results = vector_store.similarity_search(query, k=5)

        print(f"📋 Retrieved {len(results)} documents for query: '{query}'")

        results_with_tables = 0
        for i, result in enumerate(results):
            has_table = result.metadata.get("has_table_data", False)
            table_count = result.metadata.get("table_count", 0)
            page = result.metadata.get("page", "unknown")

            print(
                f"  Result {i+1}: Page {page}, Has Tables: {has_table}, Count: {table_count}"
            )
            if has_table:
                results_with_tables += 1

        print(f"\n📈 RESULTS SUMMARY:")
        print(
            f"  Original docs with tables: {sum(1 for doc in test_docs if doc.metadata.get('has_table_data'))}"
        )
        print(f"  Retrieved docs with tables: {results_with_tables}")

        if results_with_tables > 0:
            print("✅ SUCCESS: Table metadata preserved through ChromaDB")
        else:
            print("❌ PROBLEM: Table metadata lost in ChromaDB")

    except Exception as e:
        print(f"❌ Error during retrieval test: {e}")

    # Test direct collection access
    print("\n🔬 Testing direct collection access...")
    try:
        collection = vector_store._collection
        all_data = collection.get(include=["documents", "metadatas"])

        print(f"📄 Collection contains {len(all_data['documents'])} documents")

        stored_with_tables = 0
        for i, metadata in enumerate(all_data.get("metadatas", [])):
            has_table = metadata.get("has_table_data", False) if metadata else False
            if has_table:
                stored_with_tables += 1
                table_count = metadata.get("table_count", 0)
                page = metadata.get("page", "unknown")
                print(f"  Stored doc {i+1}: Page {page}, Tables: {table_count}")

        print(f"\n📊 STORAGE SUMMARY:")
        print(f"  Documents stored with table metadata: {stored_with_tables}")

        if stored_with_tables > 0:
            print("✅ SUCCESS: Table metadata stored correctly in ChromaDB")
        else:
            print("❌ PROBLEM: Table metadata not stored in ChromaDB")

    except Exception as e:
        print(f"❌ Error during direct collection test: {e}")

    # Cleanup
    print(
        f"\n🧹 Cleanup: Temp directory {vector_dir} can be manually removed if needed"
    )


if __name__ == "__main__":
    test_chromadb_metadata_preservation()
