#!/usr/bin/env python3
"""
Test script to verify the knowledge base integration fix by making a direct API call.
This script simulates what the frontend does when calling the generate-questions endpoint.
"""

import requests
import json
import uuid


def test_generate_questions_endpoint():
    """Test the /generate-questions endpoint with knowledge base integration"""

    # API endpoint
    base_url = "http://localhost:8000"  # Adjust if different
    endpoint = f"{base_url}/api/v1/veradoc/generate-questions"

    # Test data - using a valid UUID format
    test_data = {
        "description": "Create questions for evaluating AI safety protocols in healthcare applications",
        "checklist_type": "general",
        "knowledge_base_id": "12345678-1234-5678-9012-123456789012",  # Valid UUID format
        "search_mode": "vector",
        "num_questions": 5,
    }

    print(f"🔄 Testing endpoint: {endpoint}")
    print(f"📝 Request data: {json.dumps(test_data, indent=2)}")

    try:
        # Make the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer dummy-token",  # You'll need a real token for actual testing
        }

        response = requests.post(endpoint, json=test_data, headers=headers, timeout=30)

        print(f"📊 Response status: {response.status_code}")
        print(f"📋 Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Generated {len(result.get('questions', []))} questions")
            print(f"🔍 Questions: {result.get('questions', [])}")
            print(f"📝 Analysis: {result.get('description_analysis', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Error details: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(
            "❌ Connection error - make sure the backend server is running on localhost:8000"
        )
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_uuid_validation():
    """Test UUID validation logic"""
    print("\n🔄 Testing UUID validation logic...")

    # Test valid UUID
    valid_uuid = "12345678-1234-5678-9012-123456789012"
    try:
        parsed = uuid.UUID(valid_uuid)
        print(f"✅ Valid UUID parsed successfully: {parsed}")
    except ValueError as e:
        print(f"❌ Failed to parse valid UUID: {e}")

    # Test invalid UUID
    invalid_uuid = "invalid-uuid"
    try:
        parsed = uuid.UUID(invalid_uuid)
        print(f"❌ Unexpected success with invalid UUID: {parsed}")
    except ValueError:
        print(f"✅ Invalid UUID correctly rejected")

    return True


if __name__ == "__main__":
    print("🚀 Testing Knowledge Base Integration Fix")
    print("=" * 50)

    # Test UUID validation first
    uuid_test_passed = test_uuid_validation()

    # Test the API endpoint
    api_test_passed = test_generate_questions_endpoint()

    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"UUID Validation: {'✅ PASSED' if uuid_test_passed else '❌ FAILED'}")
    print(f"API Endpoint: {'✅ PASSED' if api_test_passed else '❌ FAILED'}")

    if uuid_test_passed and api_test_passed:
        print("\n🎉 All tests passed! Knowledge base integration should now work.")
    elif uuid_test_passed and not api_test_passed:
        print(
            "\n⚠️  UUID validation passed, but API test failed. Check server status and authentication."
        )
    else:
        print("\n❌ Some tests failed. Check the implementation.")
