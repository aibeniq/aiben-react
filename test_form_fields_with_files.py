#!/usr/bin/env python3
"""
Test script to verify the new form fields generation with files endpoint
"""

import requests
import json
import tempfile
import os

def create_test_document():
    """Create a simple test document for field extraction"""
    content = """
Patient Intake Form

PATIENT INFORMATION:
- Full Name: John Smith
- Date of Birth: 01/15/1980
- Social Security Number: 123-45-6789
- Phone Number: (555) 123-4567
- Email Address: john.smith@email.com
- Emergency Contact: Jane Smith (555) 987-6543

ADDRESS INFORMATION:
- Street Address: 123 Main Street
- City: Anytown
- State: CA
- ZIP Code: 12345

INSURANCE INFORMATION:
- Insurance Provider: Blue Cross Blue Shield
- Policy Number: ABC123456789
- Group Number: XYZ987
- Member ID: 123456789

MEDICAL HISTORY:
- Allergies: Penicillin, Peanuts
- Current Medications: Lisinopril 10mg daily
- Previous Surgeries: Appendectomy (2010)
- Chronic Conditions: Hypertension
"""
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        return f.name

def test_form_fields_with_files():
    """Test the new form fields generation endpoint with file upload"""
    
    # Create test document
    test_file_path = create_test_document()
    
    try:
        # API endpoint URL
        url = "http://localhost:8000/api/v1/formconnect/generate-fields-with-files"
        
        # Prepare the form data
        files = {
            'files': ('patient_form.txt', open(test_file_path, 'rb'), 'text/plain')
        }
        
        data = {
            'description': 'Medical patient intake form with personal information, address, insurance, and medical history',
            'num_fields': 15,
            'search_mode': 'full_scan'
        }
        
        print("🧪 Testing Form Fields Generation with File Upload")
        print(f"📄 Using test document: {test_file_path}")
        print(f"🔗 API URL: {url}")
        print(f"📝 Description: {data['description']}")
        print(f"🔍 Search Mode: {data['search_mode']}")
        print(f"📊 Requested Fields: {data['num_fields']}")
        print("-" * 50)
        
        # Make the API request
        response = requests.post(url, files=files, data=data)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS!")
            print(f"📈 Generated {len(result.get('fields', []))} fields:")
            print("-" * 30)
            
            for i, field in enumerate(result.get('fields', []), 1):
                print(f"  {i:2d}. {field}")
            
            print("-" * 30)
            print(f"🔍 Analysis: {result.get('description_analysis', 'N/A')}")
            
            return True
            
        else:
            print("❌ ERROR!")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        return False
        
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
            print(f"🧹 Cleaned up test file: {test_file_path}")

def test_without_files():
    """Test that the original endpoint still works for comparison"""
    
    url = "http://localhost:8000/api/v1/formconnect/generate-fields-json"
    
    data = {
        'description': 'Medical patient intake form with personal information, address, insurance, and medical history',
        'num_fields': 15,
        'search_mode': 'full_scan'
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("\n🧪 Testing Original Endpoint (No Files) for Comparison")
    print(f"🔗 API URL: {url}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS!")
            print(f"📈 Generated {len(result.get('fields', []))} fields:")
            print("-" * 30)
            
            for i, field in enumerate(result.get('fields', []), 1):
                print(f"  {i:2d}. {field}")
            
            print("-" * 30)
            print(f"🔍 Analysis: {result.get('description_analysis', 'N/A')}")
            
            return True
            
        else:
            print("❌ ERROR!")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception occurred: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Testing Form Fields Generation with File Upload Feature")
    print("=" * 60)
    
    # Test with files
    success_with_files = test_form_fields_with_files()
    
    # Test without files for comparison
    success_without_files = test_without_files()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"   • With Files: {'✅ PASSED' if success_with_files else '❌ FAILED'}")
    print(f"   • Without Files: {'✅ PASSED' if success_without_files else '❌ FAILED'}")
    
    if success_with_files and success_without_files:
        print("\n🎉 All tests PASSED! The file upload feature is working correctly!")
    else:
        print("\n💥 Some tests FAILED. Check the output above for details.")
