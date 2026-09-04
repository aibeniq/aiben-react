#!/usr/bin/env python3
"""Debug embedding models issue."""

import requests
import json


def test_endpoints():
    base_url = "http://localhost:8000/api/v1"

    # Test system config
    print("=== System Config ===")
    try:
        response = requests.get(f"{base_url}/utils/system-config")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test default embedding model
    print("\n=== Default Embedding Model ===")
    try:
        response = requests.get(f"{base_url}/embedding-models/default")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test available embedding models
    print("\n=== Available Embedding Models ===")
    try:
        response = requests.get(f"{base_url}/embedding-models/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"Found {len(models.get('data', []))} models:")
            for model in models.get("data", [])[:10]:  # Limit to first 10
                print(f"  - {model.get('model_id')} ({model.get('provider')})")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_endpoints()
