#!/usr/bin/env python3
"""
Test CSV and XLSX file extraction functionality.
"""

import sys
import os
import tempfile
from pathlib import Path

# Add the backend to the path
sys.path.append('/home/ec2-user/aiben-react/backend')

def test_csv_extraction():
    """Test CSV file text extraction."""
    print("🔍 Testing CSV file extraction...")
    
    try:
        from app.services.document_utils import extract_text_from_csv_bytes
        
        # Create sample CSV content
        csv_content = """Name,Age,City,Occupation
John Doe,30,New York,Engineer
Jane Smith,25,Los Angeles,Designer
Bob Johnson,35,Chicago,Manager
Alice Brown,28,Houston,Developer"""
        
        csv_bytes = csv_content.encode('utf-8')
        
        # Extract text
        result = extract_text_from_csv_bytes(csv_bytes, "test.csv")
        
        print("📄 CSV extraction result:")
        print(result)
        print()
        
        # Check if extraction was successful
        if "Column Headers:" in result and "Name | Age | City | Occupation" in result:
            print("✅ CSV extraction: SUCCESS")
            return True
        else:
            print("❌ CSV extraction: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ CSV extraction error: {e}")
        return False

def test_xlsx_creation_and_extraction():
    """Create a test XLSX file and extract text from it."""
    print("🔍 Testing XLSX file extraction...")
    
    try:
        import pandas as pd
        from app.services.document_utils import extract_text_from_xlsx_bytes
        
        # Create sample DataFrame
        data = {
            'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
            'Price': [1200, 25, 75, 300],
            'Stock': [10, 50, 30, 15],
            'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics']
        }
        df = pd.DataFrame(data)
        
        # Create XLSX file in memory
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_file_path = temp_file.name
            
        try:
            # Write to Excel file
            df.to_excel(temp_file_path, index=False, sheet_name='Products')
            
            # Read the file back as bytes
            with open(temp_file_path, 'rb') as f:
                xlsx_bytes = f.read()
            
            # Extract text
            result = extract_text_from_xlsx_bytes(xlsx_bytes, "test.xlsx")
            
            print("📄 XLSX extraction result:")
            print(result)
            print()
            
            # Check if extraction was successful
            if "Sheet: Products" in result and "Product | Price | Stock | Category" in result:
                print("✅ XLSX extraction: SUCCESS")
                return True
            else:
                print("❌ XLSX extraction: FAILED")
                return False
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        print(f"❌ XLSX extraction error: {e}")
        return False

def test_unified_extraction():
    """Test the unified extraction functions."""
    print("🔍 Testing unified extraction functions...")
    
    try:
        from app.services.document_utils import extract_text_from_file_unified, extract_documents_from_file_unified
        
        # Test CSV
        csv_content = "Name,Score\nAlice,95\nBob,87"
        csv_bytes = csv_content.encode('utf-8')
        
        csv_text = extract_text_from_file_unified(csv_bytes, "data.csv")
        csv_docs = extract_documents_from_file_unified(csv_bytes, "data.csv")
        
        print("📄 Unified CSV text extraction:")
        print(csv_text[:200] + "..." if len(csv_text) > 200 else csv_text)
        print(f"📄 CSV documents count: {len(csv_docs)}")
        print()
        
        if "Name | Score" in csv_text and len(csv_docs) == 1:
            print("✅ Unified CSV extraction: SUCCESS")
            csv_success = True
        else:
            print("❌ Unified CSV extraction: FAILED")
            csv_success = False
            
        # Test XLSX (create simple one)
        import pandas as pd
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_file_path = temp_file.name
            
        try:
            df.to_excel(temp_file_path, index=False)
            
            with open(temp_file_path, 'rb') as f:
                xlsx_bytes = f.read()
            
            xlsx_text = extract_text_from_file_unified(xlsx_bytes, "data.xlsx")
            xlsx_docs = extract_documents_from_file_unified(xlsx_bytes, "data.xlsx")
            
            print("📄 Unified XLSX text extraction:")
            print(xlsx_text[:200] + "..." if len(xlsx_text) > 200 else xlsx_text)
            print(f"📄 XLSX documents count: {len(xlsx_docs)}")
            print()
            
            if "A | B" in xlsx_text and len(xlsx_docs) == 1:
                print("✅ Unified XLSX extraction: SUCCESS")
                xlsx_success = True
            else:
                print("❌ Unified XLSX extraction: FAILED")
                xlsx_success = False
                
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
        return csv_success and xlsx_success
        
    except Exception as e:
        print(f"❌ Unified extraction error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 CSV and XLSX File Extraction Tests")
    print("=" * 50)
    
    results = []
    
    # Test individual functions
    results.append(test_csv_extraction())
    results.append(test_xlsx_creation_and_extraction())
    results.append(test_unified_extraction())
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 ALL TESTS PASSED ({success_count}/{total_count})")
        print("✅ CSV and XLSX file processing is working correctly!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({success_count}/{total_count})")
        
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
