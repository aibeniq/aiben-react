"""
Direct validation of table preservation in existing vector store
"""

import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))


def test_vector_store_table_preservation():
    """Test table preservation by checking existing vector store data"""

    print("=== VECTOR STORE TABLE PRESERVATION TEST ===")

    # Path to ChromaDB storage
    chroma_path = os.path.join("backend", "vector_stores")

    if not os.path.exists(chroma_path):
        print(f"❌ ChromaDB path not found: {chroma_path}")
        print("This suggests no documents have been processed yet.")
        return False

    print(f"✅ Found ChromaDB directory: {chroma_path}")

    # List available collections
    collections = []
    for item in os.listdir(chroma_path):
        collection_path = os.path.join(chroma_path, item)
        if os.path.isdir(collection_path):
            collections.append(item)

    if not collections:
        print("❌ No collections found in ChromaDB")
        return False

    print(f"Found {len(collections)} collections: {collections}")

    # Look for documents with table content
    table_documents_found = 0
    broken_table_documents = 0

    table_markers = [
        ("=== STRUCTURED TABLE DATA ===", "=== END STRUCTURED TABLE DATA ==="),
        ("=== RAW TABLE CONTENT ===", "=== END RAW TABLE CONTENT ==="),
        ("=== SEARCHABLE SUMMARY ===", "=== END SEARCHABLE SUMMARY ==="),
    ]

    # Initialize ChromaDB client to read stored documents
    try:
        import chromadb

        client = chromadb.PersistentClient(path=chroma_path)

        for collection_name in collections:
            try:
                collection = client.get_collection(collection_name)

                # Get all documents from this collection
                results = collection.get(include=["documents", "metadatas"])

                print(f"\n--- Collection: {collection_name} ---")
                print(f"Total documents: {len(results['documents'])}")

                # Check each document for table preservation
                for i, (doc_content, metadata) in enumerate(
                    zip(results["documents"], results["metadatas"])
                ):

                    # Check for table markers
                    has_table_content = False
                    has_complete_table = False
                    has_broken_table = False

                    for start_marker, end_marker in table_markers:
                        has_start = start_marker in doc_content
                        has_end = end_marker in doc_content

                        if has_start or has_end:
                            has_table_content = True

                            if has_start and has_end:
                                has_complete_table = True
                                table_documents_found += 1
                                print(
                                    f"✅ Doc {i+1}: Complete table ({start_marker[:20]}...)"
                                )
                            elif has_start or has_end:
                                has_broken_table = True
                                broken_table_documents += 1
                                if has_start:
                                    print(
                                        f"❌ Doc {i+1}: BROKEN - Contains {start_marker[:20]}... without end"
                                    )
                                if has_end:
                                    print(
                                        f"❌ Doc {i+1}: BROKEN - Contains {end_marker[:20]}... without start"
                                    )

                                # Show some content for debugging
                                preview = doc_content[:200].replace("\n", " ")
                                print(f"    Content preview: {preview}...")

                    # Check metadata for table information
                    if metadata and metadata.get("has_table_data"):
                        if not has_table_content:
                            print(
                                f"⚠️  Doc {i+1}: Metadata indicates table data but no markers found"
                            )
                        else:
                            source = metadata.get("source", "Unknown")
                            page = metadata.get("page", "Unknown")
                            print(
                                f"ℹ️  Doc {i+1}: Table content from {source}, page {page}"
                            )

            except Exception as e:
                print(f"❌ Error reading collection {collection_name}: {e}")
                continue

    except Exception as e:
        print(f"❌ Error accessing ChromaDB: {e}")
        return False

    # Final assessment
    print(f"\n=== RESULTS ===")
    print(f"Documents with complete tables: {table_documents_found}")
    print(f"Documents with broken tables: {broken_table_documents}")

    if broken_table_documents == 0 and table_documents_found > 0:
        print("✅ SUCCESS: All table structures are preserved!")
        print("✅ No broken table markers found in vector store!")
        return True
    elif broken_table_documents > 0:
        print(
            f"❌ FAILURE: Found {broken_table_documents} documents with broken table structures"
        )
        print("❌ Table preservation is not working correctly")
        return False
    elif table_documents_found == 0:
        print("ℹ️ No table content found in vector store")
        print(
            "ℹ️ This could indicate documents haven't been processed with table extraction"
        )
        return None  # Inconclusive
    else:
        print("ℹ️ Unexpected result state")
        return None


if __name__ == "__main__":
    result = test_vector_store_table_preservation()
    if result is True:
        sys.exit(0)
    elif result is False:
        sys.exit(1)
    else:
        sys.exit(2)  # Inconclusive
