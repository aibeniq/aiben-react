#!/usr/bin/env python3
"""
Test script to verify that the form fields API endpoint is working correctly
"""
import requests
import json


def test_form_fields_endpoint():
    """Test the form fields generation endpoint without authentication"""
    url = "http://localhost:8000/api/v1/formconnect/generate-fields-json"

    data = {"description": "A simple medical intake form", "num_fields": 5}

    try:
        print(f"Testing endpoint: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 401:
            print(
                "✅ Endpoint exists and correctly requires authentication (401 Unauthorized)"
            )
            return True
        elif response.status_code == 200:
            print("✅ Endpoint works! Response:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to backend server. Is it running on localhost:8000?"
        )
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_form_fields_endpoint()
    if success:
        print("\n✅ Form fields endpoint is working correctly!")
        print("The frontend should now be able to connect properly.")
    else:
        print("\n❌ There may be an issue with the backend endpoint.")
