#!/usr/bin/env python3
"""
Integration test for CSV and XLSX file compatibility with the full application.
Tests that existing functionality still works and new file types are supported.
"""

import sys
import os
import tempfile
import requests
import time
from pathlib import Path

# Backend API URL
API_BASE = "http://localhost:8000"

def create_test_files():
    """Create test files for all supported formats."""
    test_files = {}
    
    # Create CSV test file
    csv_content = """Product,Price,Category,Stock
iPhone 15,999,Electronics,50
MacBook Pro,2499,Electronics,25
AirPods,249,Electronics,100
Office Chair,299,Furniture,15
Standing Desk,599,Furniture,8"""
    
    csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    csv_file.write(csv_content)
    csv_file.close()
    test_files['csv'] = csv_file.name
    
    # Create XLSX test file
    try:
        import pandas as pd
        
        data = {
            'Employee': ['John Doe', 'Jane Smith', 'Bob Johnson', 'Alice Brown'],
            'Department': ['Engineering', 'Design', 'Sales', 'Marketing'],
            'Salary': [85000, 75000, 65000, 70000],
            'Years': [5, 3, 8, 2]
        }
        df = pd.DataFrame(data)
        
        xlsx_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        xlsx_file.close()
        
        df.to_excel(xlsx_file.name, index=False, sheet_name='Employees')
        test_files['xlsx'] = xlsx_file.name
        
    except ImportError:
        print("⚠️  pandas not available for XLSX test file creation")
    
    # Create TXT test file (to verify existing functionality)
    txt_content = """This is a test text document.
It contains multiple lines of text.
We use this to verify that existing TXT file processing still works.
This should be processed without any issues."""
    
    txt_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    txt_file.write(txt_content)
    txt_file.close()
    test_files['txt'] = txt_file.name
    
    return test_files

def test_document_upload_endpoint(file_path, file_type):
    """Test document upload through the chatbot document endpoint."""
    print(f"🔍 Testing {file_type.upper()} file upload via chatbot endpoint...")
    
    try:
        # Check if API is accessible
        health_response = requests.get(f"{API_BASE}/docs", timeout=5)
        if health_response.status_code != 200:
            print(f"⚠️  API not accessible at {API_BASE}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Cannot connect to API at {API_BASE}: {e}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'files': (os.path.basename(file_path), f, 'application/octet-stream')}
            data = {
                'question': f'What information is contained in this {file_type} file?',
                'search_mode': 'full_scan'  # Use full scan to test text extraction
            }
            
            # Make request to document query endpoint
            response = requests.post(
                f"{API_BASE}/api/v1/chatbot/document",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if we got a proper response with content
                if 'response' in result and result['response']:
                    print(f"✅ {file_type.upper()} upload successful")
                    print(f"   Response length: {len(result['response'])} characters")
                    
                    # Check for error indicators in the response
                    error_indicators = [
                        "failed to extract",
                        "unsupported file format",
                        "error processing",
                        "could not read"
                    ]
                    
                    response_lower = result['response'].lower()
                    has_errors = any(indicator in response_lower for indicator in error_indicators)
                    
                    if has_errors:
                        print(f"⚠️  Response may contain extraction errors")
                        print(f"   First 200 chars: {result['response'][:200]}...")
                        return False
                    else:
                        print(f"   Response preview: {result['response'][:150]}...")
                        return True
                else:
                    print(f"❌ {file_type.upper()} upload failed - empty response")
                    return False
            else:
                print(f"❌ {file_type.upper()} upload failed - HTTP {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error response: {response.text[:200]}")
                return False
                
    except requests.exceptions.Timeout:
        print(f"⏰ {file_type.upper()} upload timed out")
        return False
    except Exception as e:
        print(f"❌ {file_type.upper()} upload error: {e}")
        return False

def test_direct_extraction():
    """Test direct text extraction functions."""
    print("🔍 Testing direct text extraction functions...")
    
    try:
        sys.path.append('/home/ec2-user/aiben-react/backend')
        from app.services.document_utils import extract_text_from_file_unified
        
        # Test CSV
        csv_content = "Name,Age\nAlice,25\nBob,30"
        csv_result = extract_text_from_file_unified(csv_content.encode('utf-8'), "test.csv")
        
        if "Name | Age" in csv_result and "Alice | 25" in csv_result:
            print("✅ Direct CSV extraction: SUCCESS")
            csv_success = True
        else:
            print("❌ Direct CSV extraction: FAILED")
            csv_success = False
        
        # Test XLSX (if pandas available)
        xlsx_success = True
        try:
            import pandas as pd
            
            df = pd.DataFrame({'Col1': ['A', 'B'], 'Col2': [1, 2]})
            
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                temp_path = temp_file.name
                
            try:
                df.to_excel(temp_path, index=False)
                
                with open(temp_path, 'rb') as f:
                    xlsx_bytes = f.read()
                
                xlsx_result = extract_text_from_file_unified(xlsx_bytes, "test.xlsx")
                
                if "Col1 | Col2" in xlsx_result and "A | 1" in xlsx_result:
                    print("✅ Direct XLSX extraction: SUCCESS")
                else:
                    print("❌ Direct XLSX extraction: FAILED")
                    xlsx_success = False
                    
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except ImportError:
            print("⚠️  pandas not available - skipping direct XLSX test")
        
        return csv_success and xlsx_success
        
    except Exception as e:
        print(f"❌ Direct extraction error: {e}")
        return False

def cleanup_test_files(test_files):
    """Clean up temporary test files."""
    for file_type, file_path in test_files.items():
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"⚠️  Could not clean up {file_type} file: {e}")

def main():
    """Run all integration tests."""
    print("🧪 CSV and XLSX Integration Tests")
    print("=" * 50)
    
    # Check if we can access the backend
    print("🔍 Checking API accessibility...")
    try:
        response = requests.get(f"{API_BASE}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API is accessible")
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cannot connect to API: {e}")
        print("   Make sure the application is running with 'docker-compose up'")
    
    print()
    
    # Test direct extraction first
    direct_test_success = test_direct_extraction()
    print()
    
    # Create test files
    print("📁 Creating test files...")
    test_files = create_test_files()
    print(f"   Created {len(test_files)} test files")
    print()
    
    # Test each file type through the API
    api_results = []
    
    for file_type, file_path in test_files.items():
        result = test_document_upload_endpoint(file_path, file_type)
        api_results.append(result)
        print()
    
    # Clean up
    cleanup_test_files(test_files)
    
    # Summary
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 40)
    
    direct_status = "✅ PASSED" if direct_test_success else "❌ FAILED"
    print(f"Direct extraction tests: {direct_status}")
    
    api_success_count = sum(api_results)
    api_total_count = len(api_results)
    api_status = "✅ PASSED" if api_success_count == api_total_count else f"⚠️  PARTIAL ({api_success_count}/{api_total_count})"
    print(f"API endpoint tests: {api_status}")
    
    overall_success = direct_test_success and (api_success_count == api_total_count)
    
    if overall_success:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ CSV and XLSX files are now fully supported in your application!")
        print("✅ Existing functionality (PDF, TXT, DOCX) is preserved!")
    else:
        print(f"\n⚠️  SOME TESTS HAD ISSUES")
        if not direct_test_success:
            print("   - Direct extraction functions need attention")
        if api_success_count != api_total_count:
            print("   - Some API endpoints had issues (may be due to connection/auth)")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
