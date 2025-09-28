"""
End-to-end test to validate complete table preservation solution
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

import requests
import time
import json


def test_end_to_end_table_preservation():
    """Test complete pipeline with actual document"""

    base_url = "http://localhost:8000/api/v1"

    # Wait for backend to be ready
    print("Waiting for backend to start...")
    for i in range(30):
        try:
            response = requests.get(f"{base_url}/utils/health-check/")
            if response.status_code == 200:
                print("✅ Backend is ready!")
                break
        except requests.exceptions.ConnectionError:
            pass

        time.sleep(2)
        if i % 5 == 4:
            print(f"Still waiting... ({i+1}/30)")
    else:
        print("❌ Backend failed to start")
        return False

    # Test file path
    test_file = "test_files/Appendix 6 Fee Schedule.pdf"

    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False

    print(f"\n=== TESTING TABLE PRESERVATION WITH {test_file} ===")

    print("📤 Uploading document via chatbot query...")

    # Query with document upload
    print("🔍 Querying document for table content...")

    with open(test_file, "rb") as f:
        files = {"files": f}
        data = {
            "message": "What are the consultation fees and emergency rates shown in the tables?",
            "session_id": "test_table_preservation",
            "include_models": True,
            "search_mode": "vector",
        }

        response = requests.post(f"{base_url}/chat/document", files=files, data=data)

    if response.status_code != 200:
        print(f"❌ Query failed: {response.status_code}")
        print(response.text)
        return False

    result = response.json()

    # Analyze citations for table preservation
    print("\n=== ANALYZING CITATIONS ===")

    citations = result.get("citations", [])
    if not citations:
        print("❌ No citations found")
        return False

    print(f"Found {len(citations)} citations")

    complete_tables = 0
    broken_tables = 0
    citations_with_tables = 0

    table_markers = [
        ("=== STRUCTURED TABLE DATA ===", "=== END STRUCTURED TABLE DATA ==="),
        ("=== RAW TABLE CONTENT ===", "=== END RAW TABLE CONTENT ==="),
        ("=== SEARCHABLE SUMMARY ===", "=== END SEARCHABLE SUMMARY ==="),
    ]

    for i, citation in enumerate(citations):
        print(f"\n--- Citation {i+1} ---")

        content = citation.get("content", "")
        metadata = citation.get("metadata", {})

        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Page: {metadata.get('page', 'Unknown')}")
        print(f"Has table data: {metadata.get('has_table_data', False)}")
        print(f"Table count: {metadata.get('table_count', 0)}")
        print(f"Processing method: {metadata.get('processing_method', 'Unknown')}")

        # Check for table content
        has_table_content = False
        has_complete_table = False
        has_broken_table = False

        for start_marker, end_marker in table_markers:
            has_start = start_marker in content
            has_end = end_marker in content

            if has_start or has_end:
                has_table_content = True
                citations_with_tables += 1

                if has_start and has_end:
                    has_complete_table = True
                    complete_tables += 1
                    print(f"✅ Contains complete table ({start_marker[:20]}...)")
                elif has_start or has_end:
                    has_broken_table = True
                    broken_tables += 1
                    if has_start:
                        print(f"❌ BROKEN: Contains {start_marker[:20]}... without end")
                    if has_end:
                        print(f"❌ BROKEN: Contains {end_marker[:20]}... without start")

        if not has_table_content and metadata.get("has_table_data"):
            print("⚠️ Metadata indicates table data but no table markers found")
        elif not has_table_content:
            print("ℹ️ No table content")

        # Show content preview
        preview = content[:200].replace("\n", " ")
        if len(content) > 200:
            preview += "..."
        print(f"Content preview: {preview}")

    # Final assessment
    print("\n=== FINAL ASSESSMENT ===")
    print(f"Total citations: {len(citations)}")
    print(f"Citations with table content: {citations_with_tables}")
    print(f"Complete table blocks: {complete_tables}")
    print(f"Broken table blocks: {broken_tables}")

    if broken_tables == 0 and complete_tables > 0:
        print("✅ SUCCESS: All table structures preserved during chunking!")
        print("✅ Table metadata appears correctly in citations!")
        return True
    elif broken_tables > 0:
        print(f"❌ FAILURE: {broken_tables} table block(s) were broken during chunking")
        return False
    elif complete_tables == 0 and citations_with_tables == 0:
        print("⚠️ No table content found in citations - may indicate processing issues")
        return False
    else:
        print("ℹ️ Results inconclusive")
        return False


if __name__ == "__main__":
    success = test_end_to_end_table_preservation()
    sys.exit(0 if success else 1)
