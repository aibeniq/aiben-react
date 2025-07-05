"""
Quick test to verify the generate-topics-json endpoint is working
"""

import requests
import json


def test_endpoint():
    url = "http://localhost:8001/api/v1/twincheck/generate-topics-json"

    # Simple test data
    data = {
        "description": "Compare two healthcare policy documents",
        "comparison_type": "general",
        "num_topics": 3,
    }

    try:
        response = requests.post(
            url, json=data, headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Generated {len(result.get('topics', []))} topics")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


if __name__ == "__main__":
    test_endpoint()
