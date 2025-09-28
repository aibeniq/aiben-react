#!/usr/bin/env python3
"""
Test script to verify table-aware processing functionality
"""
import requests
import json
import os

# Configuration
BASE_URL = "http://localhost:8000"
TEST_FILE_PATH = "c:\\miniconda\\aibeniq-react\\Appendix 6 Fee Schedule.pdf"


def test_table_processing():
    """Test table-aware document processing"""

    # Check if test file exists
    if not os.path.exists(TEST_FILE_PATH):
        print(f"❌ Test file not found: {TEST_FILE_PATH}")
        return False

    print(f"✅ Found test file: {TEST_FILE_PATH}")

    # Prepare the file upload
    files = {
        "files": (
            "Appendix 6 Fee Schedule.pdf",
            open(TEST_FILE_PATH, "rb"),
            "application/pdf",
        )
    }

    # Prepare form data
    data = {
        "question": "What are the key fee structures in this schedule?",
        "search_mode": "vector",  # This should trigger table-aware processing
    }

    try:
        print("\n🔄 Uploading file and testing table processing...")

        # Make the request to the document query endpoint
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/query_document",
            files=files,
            data=data,
            timeout=60,  # Give it time to process
        )

        print(f"📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(
                f"📄 Response: {result.get('response', 'No response field')[:200]}..."
            )

            # Check for table processing indicators in the response
            if "metadata" in result:
                metadata = result["metadata"]
                print(f"\n📋 Metadata found:")
                for key, value in metadata.items():
                    print(f"  - {key}: {value}")

            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Close the file
        files["files"][1].close()


def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not reachable: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing Table-Aware Processing Functionality")
    print("=" * 50)

    # First check if backend is running
    if not test_backend_health():
        print("\n❌ Backend is not running. Please start the backend first.")
        exit(1)

    # Test table processing
    success = test_table_processing()

    if success:
        print("\n🎉 Table processing test completed successfully!")
    else:
        print("\n❌ Table processing test failed!")

    print("\n📝 Check the backend logs for detailed table processing information.")
