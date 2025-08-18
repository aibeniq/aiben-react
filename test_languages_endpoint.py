#!/usr/bin/env python3
"""
Test the supported languages endpoint
"""

import requests
import json


def test_supported_languages_endpoint():
    """Test the new supported languages endpoint"""
    try:
        # Test the endpoint
        response = requests.get(
            "http://localhost:8000/api/v1/users/supported-languages"
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint working!")
            print(f"Response: {json.dumps(data, indent=2)}")

            # Check if Spanish is in the supported languages
            languages = data.get("languages", {})
            if "es" in languages:
                print(f"✅ Spanish supported: {languages['es']}")
            else:
                print("❌ Spanish not found in supported languages")

            if "fi" in languages:
                print(f"✅ Finnish supported: {languages['fi']}")
            else:
                print("❌ Finnish not found in supported languages")

        else:
            print(f"❌ Endpoint failed with status: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_supported_languages_endpoint()
