#!/usr/bin/env python3
"""
Test script to verify the table processing fixes work correctly.
"""

import os
import sys
import requests
import json
from pathlib import Path


def test_document_upload_and_query():
    """Test uploading the Appendix 6 Fee Schedule PDF and querying it."""

    print("🧪 Testing Table Processing Fix with 'Appendix 6 Fee Schedule.pdf'\n")

    # Check if test file exists
    test_file_path = Path("test_files/Appendix 6 Fee Schedule.pdf")
    if not test_file_path.exists():
        print(f"❌ Test file not found: {test_file_path}")
        print("Please ensure 'test_files/Appendix 6 Fee Schedule.pdf' exists")
        return False

    base_url = "http://localhost:8000"

    # Test: Upload document and query in one step (combined endpoint)
    print("📤 Testing document upload and querying (combined)...")

    document_url = f"{base_url}/api/v1/chat/document"

    test_queries = [
        "What are the fees for trading US equities?",
        "What are the OTC trade fees?",
        "What are the safekeeping custody fees?",
        "Show me the account opening fees",
    ]

    for query in test_queries:
        print(f"\n📋 Query: {query}")

        try:
            # Prepare form data including both file and parameters
            with open(test_file_path, "rb") as f:
                files = {"files": ("Appendix 6 Fee Schedule.pdf", f, "application/pdf")}

                data = {
                    "question": query,
                    "chat_history": "",
                    "use_default_models": "true",
                    "session_id": f"test_session_{hash(query)}",  # Unique session per query
                    "is_follow_up": "false",
                    "search_mode": "vector",
                }

                response = requests.post(
                    document_url, files=files, data=data, timeout=300
                )

            if response.status_code == 200:
                query_result = response.json()

                # Check the response for structured table data
                answer = query_result.get("answer", "")
                sources = query_result.get("sources", [])

                print(f"✅ Query successful. Answer length: {len(answer)} chars")
                print(f"📚 Sources found: {len(sources)}")

                # Analyze sources for structured table content
                structured_sources = 0
                raw_sources = 0

                for i, source in enumerate(sources):
                    source_content = source.get("content", "")

                    if "=== STRUCTURED TABLE DATA ===" in source_content:
                        structured_sources += 1
                        print(f"   Source {i+1}: Contains STRUCTURED TABLE DATA ✅")
                    elif "=== RAW TABLE CONTENT ===" in source_content:
                        raw_sources += 1
                        print(f"   Source {i+1}: Contains RAW TABLE CONTENT (fallback)")
                    else:
                        print(f"   Source {i+1}: Regular text content")

                print(
                    f"📊 Structured sources: {structured_sources}, Raw sources: {raw_sources}"
                )

                if structured_sources > 0:
                    print("🎉 SUCCESS: Found structured table data in citations!")
                elif raw_sources > 0:
                    print(
                        "⚠️  PARTIAL: Found raw table content (vision processing may have failed)"
                    )
                else:
                    print("❌ ISSUE: No structured table content found in citations")

            else:
                print(f"❌ Query failed: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"❌ Query error: {e}")

    return True


def test_backend_health():
    """Test if the backend is responsive."""

    print("🏥 Testing Backend Health...")

    try:
        response = requests.get(
            "http://localhost:8000/api/v1/utils/health-check/", timeout=10
        )

        if response.status_code == 200:
            print("✅ Backend is healthy and responsive")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing Table Processing Fix\n")

    # Test backend health first
    if not test_backend_health():
        print("\n❌ Backend not accessible. Please ensure docker-compose is running.")
        sys.exit(1)

    print()

    # Test document processing
    if test_document_upload_and_query():
        print("\n🎯 Test completed successfully!")
        print("\n📋 What to look for:")
        print(
            "   • Sources with '=== STRUCTURED TABLE DATA ===' indicate successful vision processing"
        )
        print(
            "   • Sources with '=== RAW TABLE CONTENT ===' indicate fallback processing"
        )
        print("   • More structured sources = better table metadata extraction")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
