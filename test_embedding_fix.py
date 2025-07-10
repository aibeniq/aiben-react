#!/usr/bin/env python3
"""
Simple test script to trigger embedding requests and verify the Ollama fix
"""
import requests
import json


def test_embedding_api():
    """Test the embedding API to trigger Ollama requests"""
    base_url = "http://localhost:8000"

    # Test the new registry endpoint
    try:
        print("Testing /api/v1/embedding-models/registry...")
        response = requests.get(f"{base_url}/api/v1/embedding-models/registry")
        print(f"Registry response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} embedding models in registry")
            for model in data:
                print(f"  - {model['id']} ({model['provider']})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing registry: {e}")

    # Test the providers endpoint
    try:
        print("\nTesting /api/v1/embedding-models/providers...")
        response = requests.get(f"{base_url}/api/v1/embedding-models/providers")
        print(f"Providers response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available providers: {data}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing providers: {e}")


if __name__ == "__main__":
    test_embedding_api()
