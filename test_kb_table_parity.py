#!/usr/bin/env python3
"""
Test script to verify Knowledge Base and Chatbot table processing parity.
Uploads the same document to both and compares citation formats.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_PDF = "test_files/Appendix 6 Fee Schedule.pdf"  # File path in test_files directory
TEST_QUESTION = "What are the fees for trading US equities?"


def test_chatbot_tables():
    """Test chatbot document upload with table processing"""
    print("\n🤖 Testing Chatbot Table Processing...")

    # Upload document to chatbot and ask question
    try:
        with open(TEST_PDF, "rb") as f:
            files = {"files": (TEST_PDF, f, "application/pdf")}
            params = {
                "question": TEST_QUESTION,
                "use_default_models": "true",
                "search_mode": "vector",
            }

            response = requests.post(
                f"{BASE_URL}/chat/document", files=files, params=params
            )

            if response.status_code == 200:
                data = response.json()
                sources = data.get("sources", [])
                print(f"✅ Chatbot: Got {len(sources)} sources")

                # Check for JSON table content
                json_table_found = False
                for i, source in enumerate(sources):
                    content = source.get("content", "")
                    if "=== TABLE DATA (JSON) ===" in content:
                        json_table_found = True
                        print(f"📊 Chatbot Source {i+1}: Contains JSON table data")
                        # Show first 200 chars of table content
                        table_start = content.find("=== TABLE DATA (JSON) ===")
                        table_sample = content[table_start : table_start + 300] + "..."
                        print(f"   Sample: {table_sample}")
                        break

                if json_table_found:
                    print("✅ Chatbot: JSON table format FOUND in citations")
                else:
                    print("❌ Chatbot: JSON table format NOT found in citations")

                return json_table_found
            else:
                print(f"❌ Chatbot request failed: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Chatbot test error: {e}")
        return False


def create_knowledge_base():
    """Create a knowledge base with the test document"""
    print("\n📚 Creating Knowledge Base...")

    try:
        # Create knowledge base
        kb_data = {
            "title": "Test KB for Table Parity",
            "description": "Testing table processing parity",
            "embedding_model_id": "1",  # Default embedding model
        }

        with open(TEST_PDF, "rb") as f:
            files = {"files": (TEST_PDF, f, "application/pdf")}

            response = requests.post(
                f"{BASE_URL}/knowledge-bases/", data=kb_data, files=files
            )

            if response.status_code == 200:
                kb_response = response.json()
                kb_id = kb_response["knowledge_base"]["id"]
                task_id = kb_response.get("task_id")
                print(f"✅ Created KB with ID: {kb_id}")

                # Wait for processing to complete
                if task_id:
                    print(f"⏳ Waiting for KB processing (task: {task_id})...")
                    for i in range(30):  # Wait up to 30 seconds
                        time.sleep(1)
                        progress_response = requests.get(
                            f"{BASE_URL}/progress/{task_id}"
                        )
                        if progress_response.status_code == 200:
                            progress = progress_response.json()
                            if progress.get("status") == "completed":
                                print("✅ KB processing completed")
                                break
                            elif progress.get("status") == "failed":
                                print(
                                    f"❌ KB processing failed: {progress.get('message')}"
                                )
                                return None
                        print(f"   Progress check {i+1}/30...")
                    else:
                        print("⚠️ KB processing timeout, continuing anyway...")

                return kb_id
            else:
                print(f"❌ KB creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None

    except Exception as e:
        print(f"❌ KB creation error: {e}")
        return None


def test_knowledge_base_tables(kb_id):
    """Test knowledge base query with table processing"""
    print(f"\n📚 Testing Knowledge Base Table Processing (ID: {kb_id})...")

    try:
        params = {
            "question": TEST_QUESTION,
            "use_default_models": "true",
            "search_mode": "vector",
        }

        response = requests.post(
            f"{BASE_URL}/chat/knowledge-base/{kb_id}", params=params
        )

        if response.status_code == 200:
            data = response.json()
            sources = data.get("sources", [])
            print(f"✅ Knowledge Base: Got {len(sources)} sources")

            # Check for JSON table content
            json_table_found = False
            for i, source in enumerate(sources):
                content = source.get("content", "")
                if "=== TABLE DATA (JSON) ===" in content:
                    json_table_found = True
                    print(f"📊 KB Source {i+1}: Contains JSON table data")
                    # Show first 200 chars of table content
                    table_start = content.find("=== TABLE DATA (JSON) ===")
                    table_sample = content[table_start : table_start + 300] + "..."
                    print(f"   Sample: {table_sample}")
                    break

            if json_table_found:
                print("✅ Knowledge Base: JSON table format FOUND in citations")
            else:
                print("❌ Knowledge Base: JSON table format NOT found in citations")
                # Show sample of what we got instead
                if sources:
                    sample_content = sources[0].get("content", "")[:300] + "..."
                    print(f"   Instead got: {sample_content}")

            return json_table_found
        else:
            print(f"❌ KB query failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ KB test error: {e}")
        return False


def cleanup_knowledge_base(kb_id):
    """Clean up the test knowledge base"""
    if kb_id:
        try:
            response = requests.delete(f"{BASE_URL}/knowledge-bases/{kb_id}")
            if response.status_code == 200:
                print(f"✅ Cleaned up KB {kb_id}")
            else:
                print(f"⚠️ Failed to cleanup KB {kb_id}: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


def main():
    """Run the parity test"""
    print("🔍 Testing Knowledge Base and Chatbot Table Processing Parity")
    print("=" * 60)

    # Test chatbot first
    chatbot_has_json = test_chatbot_tables()

    # Create and test knowledge base
    kb_id = create_knowledge_base()
    kb_has_json = False

    if kb_id:
        kb_has_json = test_knowledge_base_tables(kb_id)
        cleanup_knowledge_base(kb_id)

    # Results
    print("\n" + "=" * 60)
    print("🎯 PARITY TEST RESULTS:")
    print(f"   Chatbot JSON Tables: {'✅ YES' if chatbot_has_json else '❌ NO'}")
    print(f"   Knowledge Base JSON Tables: {'✅ YES' if kb_has_json else '❌ NO'}")

    if chatbot_has_json and kb_has_json:
        print("🎉 SUCCESS: Both systems use JSON table processing!")
    elif chatbot_has_json and not kb_has_json:
        print("⚠️ ISSUE: Knowledge Base missing JSON table processing")
    elif not chatbot_has_json and kb_has_json:
        print("⚠️ ISSUE: Chatbot missing JSON table processing")
    else:
        print("❌ PROBLEM: Neither system has JSON table processing")


if __name__ == "__main__":
    main()
