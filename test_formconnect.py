#!/usr/bin/env python3
"""
Test script for FormConnect API to verify template formatting fix
"""

import requests
import os

def test_formconnect():
    """Test the FormConnect API with the APA table PDF"""
    
    # API endpoint
    url = "http://localhost:8000/api/v1/formconnect/process"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {os.environ.get('TEST_TOKEN', 'your-token-here')}"
    }
    
    # Fields to extract  
    fields = [
        "Table Title",
        "Author(s) Name", 
        "Date of Data Collection",
        "Sample Size",
        "Gender (Demographic)",
        "Mean (M)",
        "Standard Deviation (SD)", 
        "P-Value"
    ]
    
    # File path
    file_path = "test_files/APA table example.pdf"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return
    
    try:
        # Prepare the files and data
        with open(file_path, 'rb') as f:
            files = {
                'digitized_files': (os.path.basename(file_path), f, 'application/pdf')
            }
            
            data = {
                'fields': ','.join(fields)
            }
            
            print("🚀 Making FormConnect API request...")
            print(f"📄 File: {file_path}")
            print(f"🔍 Fields: {', '.join(fields[:3])}... ({len(fields)} total)")
            
            # Make the request
            response = requests.post(url, headers=headers, files=files, data=data, timeout=300)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success! FormConnect API Response:")
                
                # Check if we have results
                if 'results' in result and result['results']:
                    for file_result in result['results']:
                        print(f"\n📋 Results for: {file_result.get('filename', 'Unknown')}")
                        
                        extracted_fields = file_result.get('extracted_fields', {})
                        print(f"🔢 Total fields attempted: {len(extracted_fields)}")
                        
                        # Count successes vs errors
                        success_count = 0
                        error_count = 0
                        
                        for field_name, field_value in extracted_fields.items():
                            if isinstance(field_value, str) and field_value.startswith("Error:"):
                                error_count += 1
                                print(f"❌ {field_name}: {field_value}")
                            else:
                                success_count += 1
                                print(f"✅ {field_name}: {field_value}")
                        
                        print(f"\n📈 Summary: {success_count} successful, {error_count} errors")
                        
                        if error_count == 0:
                            print("🎉 All fields extracted successfully! Template fix worked!")
                        elif error_count < len(extracted_fields):
                            print("🔧 Partial success - some template errors may remain")
                        else:
                            print("💥 All extractions failed - template fix needs more work")
                            
                else:
                    print("⚠️ No results found in response")
                    
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - this can happen with large files")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the backend running?")
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")

if __name__ == "__main__":
    # Set a dummy token for testing if not set
    if not os.environ.get('TEST_TOKEN'):
        # You would need to get a real token from the API
        print("⚠️ TEST_TOKEN not set, using dummy token")
        os.environ['TEST_TOKEN'] = 'dummy-token-for-testing'
    
    test_formconnect()