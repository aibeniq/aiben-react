#!/usr/bin/env python3
"""
Test script to verify knowledge base content retrieval functionality.
"""

import sys
import os
import uuid

sys.path.append("./backend")


# Mock classes for testing
class MockUser:
    def __init__(self, user_id="test-user-id"):
        self.id = user_id


class MockSession:
    def exec(self, query):
        return MockResult()

    def get(self, model, id):
        return None


class MockResult:
    def first(self):
        return None

    def all(self):
        return []


async def test_retrieve_knowledge_base_content():
    """Test the retrieve_knowledge_base_content function"""
    try:
        from app.services.content_retrieval import retrieve_knowledge_base_content

        # Test with string UUID
        mock_session = MockSession()
        mock_user = MockUser()
        test_kb_id = "12345678-1234-5678-9012-123456789012"

        print(f"Testing with knowledge base ID: {test_kb_id}")

        content, instruction = await retrieve_knowledge_base_content(
            session=mock_session,
            current_user=mock_user,
            knowledge_base_id=test_kb_id,
            search_mode="full_scan",
            query="test query",
        )

        print(f"✅ Function executed successfully!")
        print(f"Content length: {len(content)}")
        print(f"Instruction: {instruction}")

        # Test with invalid UUID
        try:
            content, instruction = await retrieve_knowledge_base_content(
                session=mock_session,
                current_user=mock_user,
                knowledge_base_id="invalid-uuid",
                search_mode="full_scan",
                query="test query",
            )
            print(f"Invalid UUID handling: {len(content)}")
        except Exception as e:
            print(f"❌ Error with invalid UUID: {e}")

        return True

    except Exception as e:
        print(f"❌ Error testing knowledge base retrieval: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    import asyncio

    print("🔄 Testing knowledge base content retrieval...")
    success = asyncio.run(test_retrieve_knowledge_base_content())

    if success:
        print("✅ Knowledge base retrieval test completed!")
    else:
        print("❌ Knowledge base retrieval test failed!")
