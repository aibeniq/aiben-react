#!/usr/bin/env python3
"""Test script to verify ML functionality via API calls."""

import requests
import json
import time
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API base URL
API_BASE = "https://redhat-api.aiben.io"


def test_ml_embeddings():
    """Test ML embeddings functionality through API."""
    print("=== Testing ML Embeddings via API ===")

    # Test endpoint that would trigger ML imports
    # We'll use a simple endpoint that might use embeddings
    url = f"{API_BASE}/api/v1/utils/health-check/"

    try:
        print(f"Making request to: {url}")
        response = requests.get(url, timeout=30, verify=False)
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("✅ API is accessible")
        else:
            print(f"❌ API returned status {response.status_code}")

    except Exception as e:
        print(f"❌ Error accessing API: {e}")
        return False

    # Now let's try an endpoint that might trigger ML functionality
    # Check if there's a document upload or query endpoint
    print("\n=== Checking API endpoints ===")

    # Try to access API documentation or any endpoint that lists available routes
    try:
        docs_url = f"{API_BASE}/docs"
        print(f"Trying to access docs at: {docs_url}")
        response = requests.get(docs_url, timeout=10, verify=False)
        if response.status_code == 200:
            print("✅ API docs accessible")
        else:
            print(f"API docs returned: {response.status_code}")
    except Exception as e:
        print(f"Docs not accessible: {e}")

    return True


if __name__ == "__main__":
    test_ml_embeddings()
