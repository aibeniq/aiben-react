"""
Test to check the format of topics returned by the generate-topics-json endpoint
"""

import requests
import json


def test_topics_format():
    url = "http://localhost:8001/api/v1/twincheck/generate-topics-json"

    data = {
        "description": "Compare two AI policy documents focusing on ethics, implementation timelines, and regulatory compliance",
        "comparison_type": "general",
        "num_topics": 5,
    }

    try:
        response = requests.post(
            url, json=data, headers={"Content-Type": "application/json"}
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Full Response: {json.dumps(result, indent=2)}")

            topics = result.get("topics", [])
            print(f"\nNumber of topics: {len(topics)}")
            print("Topics:")
            for i, topic in enumerate(topics):
                print(f"  {i}: '{topic}' (type: {type(topic)})")

            return topics
        else:
            print(f"Error Response: {response.text}")
            return None

    except Exception as e:
        print(f"Connection error: {e}")
        return None


if __name__ == "__main__":
    test_topics_format()
