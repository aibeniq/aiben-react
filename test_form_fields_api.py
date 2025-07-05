#!/usr/bin/env python3
"""
Test the form fields generation API endpoint
"""
import requests
import json


def test_form_fields_api():
    # Test the basic description-only endpoint
    url = "http://localhost:8000/api/v1/formconnect/generate-fields-json"

    # Test data
    data = {
        "description": "A medical intake form for new patients with basic health information",
        "num_fields": 10,
    }

    try:
        print("Testing form fields generation API...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(url, json=data)

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Generated {len(result.get('fields', []))} fields:")
            for i, field in enumerate(result.get("fields", []), 1):
                print(f"  {i}. {field}")
            print(f"Analysis: {result.get('description_analysis', 'N/A')}")
        else:
            print("❌ Error!")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Exception: {e}")


if __name__ == "__main__":
    test_form_fields_api()
