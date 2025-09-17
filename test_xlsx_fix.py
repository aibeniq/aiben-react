#!/usr/bin/env python3
"""
Test XLSX file processing for knowledge base creation.
"""

import pandas as pd
import tempfile
import requests
import os

def create_test_xlsx():
    """Create a test XLSX file."""
    data = {
        'Character': ['Alice', 'White Rabbit', 'Queen of Hearts', 'Cheshire Cat'],
        'Role': ['Protagonist', 'Guide', 'Antagonist', 'Mentor'],
        'Description': ['Curious young girl', 'Always running late', 'Temperamental ruler', 'Mysterious and wise'],
        'Chapter': [1, 2, 8, 6]
    }
    
    df = pd.DataFrame(data)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    temp_file.close()
    
    # Write to Excel
    df.to_excel(temp_file.name, index=False, sheet_name='Characters')
    
    return temp_file.name

def test_xlsx_processing():
    """Test that XLSX files can be processed correctly."""
    
    # Import the function we fixed
    import sys
    sys.path.append('/home/ec2-user/aiben-react/backend')
    
    try:
        from app.services.document_utils import extract_documents_from_file_unified
        
        # Create test file
        xlsx_path = create_test_xlsx()
        
        try:
            # Read file as bytes
            with open(xlsx_path, 'rb') as f:
                file_content = f.read()
            
            # Test processing
            print("🔍 Testing XLSX processing...")
            documents = extract_documents_from_file_unified(file_content, "Through the looking glass.xlsx")
            
            print(f"✅ Successfully processed XLSX file")
            print(f"📄 Number of documents created: {len(documents)}")
            
            if len(documents) > 0:
                print(f"📝 First document content preview:")
                content = documents[0].page_content
                print(content[:300] + "..." if len(content) > 300 else content)
                print(f"🏷️  Metadata: {documents[0].metadata}")
                
                # Check if it contains expected data
                if "Alice" in content and "Character" in content:
                    print("✅ XLSX content extraction successful!")
                    return True
                else:
                    print("❌ XLSX content doesn't contain expected data")
                    return False
            else:
                print("❌ No documents created from XLSX file")
                return False
                
        finally:
            # Clean up
            if os.path.exists(xlsx_path):
                os.unlink(xlsx_path)
                
    except Exception as e:
        print(f"❌ Error testing XLSX processing: {e}")
        return False

if __name__ == "__main__":
    success = test_xlsx_processing()
    print("\n" + "="*50)
    if success:
        print("🎉 XLSX processing fix is working correctly!")
        print("✅ Knowledge base creation with XLSX files should now work.")
    else:
        print("❌ XLSX processing is still not working properly.")
    
    exit(0 if success else 1)
