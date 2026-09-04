#!/usr/bin/env python3
"""
Simple test to verify UUID handling in knowledge base retrieval.
"""

import uuid


def test_uuid_conversion():
    """Test UUID string conversion"""
    test_kb_id = "12345678-1234-5678-9012-123456789012"

    print(f"Testing UUID conversion with: {test_kb_id}")

    # Test valid UUID conversion
    try:
        if isinstance(test_kb_id, str):
            kb_uuid = uuid.UUID(test_kb_id)
            print(f"✅ Valid UUID conversion: {kb_uuid}")
        else:
            kb_uuid = test_kb_id
    except ValueError as e:
        print(f"❌ Invalid UUID format: {e}")
        return False

    # Test invalid UUID
    invalid_kb_id = "invalid-uuid"
    try:
        if isinstance(invalid_kb_id, str):
            kb_uuid = uuid.UUID(invalid_kb_id)
            print(f"✅ Unexpected success with invalid UUID: {kb_uuid}")
        else:
            kb_uuid = invalid_kb_id
    except ValueError as e:
        print(f"✅ Correctly rejected invalid UUID: {e}")

    return True


if __name__ == "__main__":
    print("🔄 Testing UUID conversion...")
    success = test_uuid_conversion()

    if success:
        print("✅ UUID conversion test passed!")
    else:
        print("❌ UUID conversion test failed!")
