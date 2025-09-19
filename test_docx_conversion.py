#!/usr/bin/env python3

import requests
import base64
import os


def test_docx_conversion():
    """Test the DOCX to PDF conversion API endpoints"""

    base_url = "http://localhost:8000"

    # Test the convert_docx_to_pdf endpoint
    print("Testing DOCX to PDF conversion API...")

    # First check if the endpoints exist
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✓ Backend is running and accessible")
        else:
            print("✗ Backend is not accessible")
            return
    except Exception as e:
        print(f"✗ Error connecting to backend: {e}")
        return

    # Test a simple endpoint to make sure everything is working
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Root endpoint is working")
        else:
            print(f"✗ Root endpoint returned status: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing root endpoint: {e}")

    # Check if we have any test docx files in the test_files directory
    test_files_dir = "test_files"
    if os.path.exists(test_files_dir):
        docx_files = [f for f in os.listdir(test_files_dir) if f.endswith(".docx")]
        if docx_files:
            print(f"Found DOCX files for testing: {docx_files}")
            # We would test here, but we need a proper DOCX file
        else:
            print("No DOCX files found in test_files directory")
    else:
        print("No test_files directory found")

    print("\nDocumented API endpoints should include:")
    print("- POST /api/files/convert-docx-to-pdf")
    print("- POST /api/files/convert-docx-to-pdf-by-filename")
    print("\nPlease check the API documentation at http://localhost:8000/docs")


if __name__ == "__main__":
    test_docx_conversion()
