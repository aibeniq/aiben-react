#!/usr/bin/env python3
"""
Test script for the Generate Outline endpoint
Run this after starting the backend server to verify the implementation
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/v1/reportgenie/generate-outline"

# Test data
test_data = {
    "description": "Create a comprehensive research report on artificial intelligence in healthcare, covering current applications, benefits, challenges, and future prospects",
    "report_type": "research",
    "num_sections": 8,
}


def test_generate_outline():
    """Test the generate outline endpoint"""
    print("🧪 Testing Generate Outline Endpoint")
    print(f"📡 URL: {API_ENDPOINT}")
    print(f"📝 Description: {test_data['description']}")
    print("=" * 80)

    try:
        # Note: This test doesn't include authentication
        # In real usage, you'll need proper JWT tokens
        response = requests.post(
            API_ENDPOINT, json=test_data, headers={"Content-Type": "application/json"}
        )

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Generated outline sections:")
            print(f"📊 Number of sections: {len(result.get('sections', []))}")
            print(f"📈 Analysis: {result.get('description_analysis', 'N/A')}")
            print()
            print("📋 Generated Sections:")
            for i, section in enumerate(result.get("sections", []), 1):
                print(f"  {i}. {section}")

        elif response.status_code == 401:
            print("🔐 Authentication required - this is expected without login")
            print("💡 To test with authentication:")
            print("   1. Login to the frontend")
            print("   2. Copy JWT token from browser dev tools")
            print("   3. Add Authorization header: 'Bearer <token>'")

        elif response.status_code == 422:
            print("❌ Validation Error:")
            print(json.dumps(response.json(), indent=2))

        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("🚫 Connection Error!")
        print("💡 Make sure the backend server is running:")
        print(
            "   cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
        )

    except Exception as e:
        print(f"💥 Error: {str(e)}")


if __name__ == "__main__":
    test_generate_outline()
