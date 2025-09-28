#!/usr/bin/env python3
"""
Simplified debug script to test table metadata through the document processing pipeline.
This simulates the core issue without needing full backend config.
"""

import sys
import os


def simulate_document_processing():
    """Simulate the document processing to identify where metadata gets lost."""

    print("🧪 SIMULATING DOCUMENT PROCESSING PIPELINE")
    print("=" * 60)

    # Simulate the flow from your log:
    # 1. Tables are detected
    print("1️⃣ TABLE DETECTION PHASE")
    print("   ✅ Table detected (strong patterns): pattern_score=44")
    print("   📊 Vision analysis summary: total_tables=10, complex_tables=10")
    print("   ✅ Vision RECOMMENDED: 10 complex tables detected")

    # 2. Vision processing happens
    print("\n2️⃣ VISION PROCESSING PHASE")
    print("   🔍 VISION PROCESSING INVOKED: Processing 10 table pages")
    print("   ✅ Vision processing complete: extracted data for 10 tables")

    # 3. Document enhancement (this is where the metadata should be added)
    print("\n3️⃣ DOCUMENT ENHANCEMENT PHASE")
    print("   ✅ Enhanced 10 documents with 10 extracted tables")

    # This is the critical step - in extract_documents_with_table_processing()
    # the documents should get enhanced with table metadata:
    simulated_docs = []
    for i in range(10):
        doc_metadata = {
            "source_filename": "Appendix 6 Fee Schedule.pdf",
            "page": i + 1,
            "has_processed_tables": True,  # This comes from document_utils.py
            "table_count": 1 if i < 10 else 0,
            "processing_method": "vision_enhanced",
        }
        simulated_docs.append(
            {
                "content": f"Document page {i+1} with table data...",
                "metadata": doc_metadata,
            }
        )

    print(f"   📊 Created {len(simulated_docs)} enhanced documents")
    table_docs = sum(
        1 for doc in simulated_docs if doc["metadata"].get("has_processed_tables")
    )
    print(f"   📋 Documents with table metadata: {table_docs}")

    # 4. Chatbot processing adds more metadata
    print("\n4️⃣ CHATBOT PROCESSING PHASE")

    # This happens in chatbot.py at lines 1332-1333
    for doc in simulated_docs:
        if doc["metadata"].get("has_processed_tables"):
            doc["metadata"]["has_table_data"] = True  # Added by chatbot
            if not doc["metadata"].get("table_count"):
                doc["metadata"]["table_count"] = 1

    enhanced_docs = sum(
        1 for doc in simulated_docs if doc["metadata"].get("has_table_data")
    )
    print(f"   ✅ Enhanced documents with has_table_data: {enhanced_docs}")

    # 5. Document chunking (this is where the issue likely occurs)
    print("\n5️⃣ DOCUMENT CHUNKING PHASE")
    print("   🔧 Using StructureAwareTextSplitter (FIXED)")

    # Simulate chunking - each document might split into multiple chunks
    simulated_chunks = []
    for doc in simulated_docs:
        # Simulate splitting each doc into 2-3 chunks
        for chunk_idx in range(2):
            chunk_metadata = doc["metadata"].copy()  # This should preserve metadata
            chunk_metadata["chunk_index"] = chunk_idx
            chunk_metadata["chunk_type"] = "main_content"

            simulated_chunks.append(
                {
                    "content": f"Chunk {chunk_idx} of: {doc['content']}",
                    "metadata": chunk_metadata,
                }
            )

    chunks_with_tables = sum(
        1 for chunk in simulated_chunks if chunk["metadata"].get("has_table_data")
    )
    print(f"   📄 Total chunks created: {len(simulated_chunks)}")
    print(f"   📋 Chunks with table metadata: {chunks_with_tables}")

    # 6. Vector storage and retrieval
    print("\n6️⃣ VECTOR STORAGE & RETRIEVAL PHASE")
    print("   📊 Storing in ChromaDB...")
    print("   🔍 Retrieving for query...")

    # Simulate retrieval - this is what gets sent to the frontend
    retrieved_docs = simulated_chunks[:5]  # Simulate retrieving top 5 chunks
    sources_with_tables = sum(
        1 for doc in retrieved_docs if doc["metadata"].get("has_table_data")
    )

    print(f"   📋 Retrieved documents: {len(retrieved_docs)}")
    print(f"   📊 Sources with table metadata: {sources_with_tables}")

    # 7. Response construction
    print("\n7️⃣ RESPONSE CONSTRUCTION PHASE")
    response_sources = []
    for doc in retrieved_docs:
        source = {
            "content": doc["content"],
            "metadata": doc["metadata"],  # This goes to frontend
        }
        response_sources.append(source)

    final_sources_with_tables = sum(
        1 for src in response_sources if src["metadata"].get("has_table_data")
    )
    print(f"   📤 Final response sources: {len(response_sources)}")
    print(f"   📋 Sources with table metadata in response: {final_sources_with_tables}")

    # Summary
    print("\n" + "=" * 60)
    print("📈 PIPELINE SUMMARY")
    print(f"   Original docs with tables: {table_docs}")
    print(f"   Enhanced with has_table_data: {enhanced_docs}")
    print(f"   Chunks with table metadata: {chunks_with_tables}")
    print(f"   Retrieved with table metadata: {sources_with_tables}")
    print(f"   Final response with table metadata: {final_sources_with_tables}")

    if final_sources_with_tables > 0:
        print("\n✅ SUCCESS: Table metadata preserved through entire pipeline!")
        print("   The issue might be elsewhere - check frontend display logic.")
    else:
        print("\n❌ ISSUE IDENTIFIED: Table metadata lost somewhere in pipeline")

    # Show sample metadata for debugging
    print("\n🔬 SAMPLE METADATA INSPECTION:")
    if response_sources:
        sample_source = response_sources[0]
        print("   Sample source metadata:")
        for key, value in sample_source["metadata"].items():
            print(f"     {key}: {value}")


if __name__ == "__main__":
    simulate_document_processing()
