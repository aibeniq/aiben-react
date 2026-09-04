#!/usr/bin/env python3

import requests
import json


def test_direct_api_call():
    """Test direct API call to the DOCX conversion endpoint"""

    # Use the exact endpoint from the logs
    source_id = "d3919ba1-870e-45c5-bec1-93b42e6143c1"
    url = f"http://localhost:8000/api/v1/files/source/{source_id}/pdf"

    print(f"Testing direct API call to: {url}")

    try:
        # First, let's check what headers we need
        response = requests.options(url)
        print(f"OPTIONS response status: {response.status_code}")
        print(f"OPTIONS response headers: {response.headers}")

        # Now make the actual GET request
        response = requests.get(url)
        print(f"GET response status: {response.status_code}")
        print(f"GET response headers: {response.headers}")

        if response.status_code == 200:
            print(f"Success! Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {len(response.content)} bytes")

            # Check if it's actually a PDF
            if response.content.startswith(b"%PDF"):
                print("✓ Response contains valid PDF content")
            else:
                print("✗ Response does not start with PDF magic bytes")
                print(f"First 100 bytes: {response.content[:100]}")

        else:
            print(f"Error response: {response.status_code}")
            print(f"Error content: {response.text}")

    except Exception as e:
        print(f"Exception occurred: {e}")


if __name__ == "__main__":
    test_direct_api_call()
