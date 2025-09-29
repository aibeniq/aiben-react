#!/usr/bin/env python3
"""Test to trigger vision processing and see debug output"""

import requests
import json


# Test the upload endpoint
def test_vision_processing():
    # Upload the test file
    url = "http://localhost:8000/api/v1/knowledge-bases/"

    # Test with the APA table file
    with open("test_files/APA table example.pdf", "rb") as f:
        files = {"file": f}
        data = {"name": "APA Test Document"}

        # Make request
        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print(f"✅ Upload successful: {response.json()}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")


if __name__ == "__main__":
    test_vision_processing()
