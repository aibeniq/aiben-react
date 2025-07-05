"""
Test script to verify the generate-outline-json endpoint works
"""

import requests
import json


# Test the endpoint
def test_generate_outline_endpoint():
    url = "http://localhost:8001/api/v1/reportgenie/generate-outline-json"

    # Sample request data
    data = {
        "description": "Create a technical report on AI in healthcare",
        "report_type": "technical",
        "num_sections": 5,
        "knowledge_base_id": None,  # Test without knowledge base first
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✅ Endpoint is working!")
            result = response.json()
            print(f"Generated {len(result.get('sections', []))} sections")
        else:
            print("❌ Endpoint returned an error")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to backend server. Make sure it's running on port 8001."
        )
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_generate_outline_endpoint()
