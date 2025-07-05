#!/usr/bin/env python3
"""
Test the form fields generation API endpoint with authentication
"""
import requests
import json


def test_authenticated_form_fields_api():
    # First, get a token by logging in
    login_url = "http://localhost:8000/api/v1/login/access-token"
    login_data = {
        "username": "admin@example.com",  # Use your test credentials
        "password": "changethis",  # Use your test password
    }

    try:
        print("Getting access token...")
        login_response = requests.post(login_url, data=login_data)

        if login_response.status_code != 200:
            print(
                f"❌ Login failed: {login_response.status_code} - {login_response.text}"
            )
            return

        token_data = login_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            print("❌ No access token received")
            return

        print("✅ Got access token")

        # Now test the form fields generation endpoint
        url = "http://localhost:8000/api/v1/formconnect/generate-fields-json"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Test data
        data = {
            "description": "A medical intake form for new patients with basic health information",
            "num_fields": 10,
        }

        print("Testing form fields generation API with authentication...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")

        response = requests.post(url, json=data, headers=headers)

        print(f"Status Code: {response.status_code}")

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
    test_authenticated_form_fields_api()
