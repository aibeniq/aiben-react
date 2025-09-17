#!/usr/bin/env python3
"""
Test specific functionality to ensure CSV and XLSX work with the knowledge base system.
"""

import sys
import os
import tempfile
import pandas as pd

# Add the backend to the path
sys.path.append('/home/ec2-user/aiben-react/backend')

def test_csv_to_langchain_docs():
    """Test CSV file conversion to LangChain documents."""
    print("🔍 Testing CSV to LangChain documents conversion...")
    
    try:
        from app.services.document_utils import extract_documents_from_file_unified
        
        # Read the test CSV file
        with open('/home/ec2-user/aiben-react/test_employees.csv', 'rb') as f:
            csv_content = f.read()
        
        # Convert to documents
        documents = extract_documents_from_file_unified(csv_content, "test_employees.csv")
        
        print(f"📄 Generated {len(documents)} document(s)")
        
        if len(documents) > 0:
            doc = documents[0]
            print(f"📄 Document content preview (first 300 chars):")
            print(doc.page_content[:300] + "...")
            print(f"📄 Document metadata: {doc.metadata}")
            
            # Check if it contains the expected data
            if "John Doe" in doc.page_content and "Engineering" in doc.page_content:
                print("✅ CSV to LangChain documents: SUCCESS")
                return True
            else:
                print("❌ CSV to LangChain documents: FAILED - Missing expected content")
                return False
        else:
            print("❌ CSV to LangChain documents: FAILED - No documents generated")
            return False
            
    except Exception as e:
        print(f"❌ CSV to LangChain documents error: {e}")
        return False

def test_xlsx_creation_and_conversion():
    """Test XLSX file creation and conversion to LangChain documents."""
    print("🔍 Testing XLSX creation and conversion...")
    
    try:
        from app.services.document_utils import extract_documents_from_file_unified
        
        # Create a test XLSX file
        data = {
            'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Webcam'],
            'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Electronics'],
            'Price': [1200, 25, 75, 300, 150],
            'Stock': [10, 50, 30, 15, 25],
            'Supplier': ['TechCorp', 'AccessCorp', 'AccessCorp', 'TechCorp', 'MediaCorp']
        }
        
        df = pd.DataFrame(data)
        
        # Save to temporary XLSX file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
            temp_file_path = temp_file.name
            
        try:
            df.to_excel(temp_file_path, index=False, sheet_name='Inventory')
            
            # Read it back and convert to documents
            with open(temp_file_path, 'rb') as f:
                xlsx_content = f.read()
            
            documents = extract_documents_from_file_unified(xlsx_content, "test_inventory.xlsx")
            
            print(f"📄 Generated {len(documents)} document(s)")
            
            if len(documents) > 0:
                doc = documents[0]
                print(f"📄 Document content preview (first 400 chars):")
                print(doc.page_content[:400] + "...")
                print(f"📄 Document metadata: {doc.metadata}")
                
                # Check if it contains the expected data
                if "Laptop" in doc.page_content and "TechCorp" in doc.page_content and "Inventory" in doc.page_content:
                    print("✅ XLSX creation and conversion: SUCCESS")
                    return True
                else:
                    print("❌ XLSX creation and conversion: FAILED - Missing expected content")
                    return False
            else:
                print("❌ XLSX creation and conversion: FAILED - No documents generated")
                return False
                
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        print(f"❌ XLSX creation and conversion error: {e}")
        return False

def test_knowledge_base_compatibility():
    """Test that our CSV/XLSX functions work with knowledge base components."""
    print("🔍 Testing knowledge base compatibility...")
    
    try:
        from app.services.document_utils import extract_documents_from_file_unified
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        # Test with the CSV file
        with open('/home/ec2-user/aiben-react/test_employees.csv', 'rb') as f:
            csv_content = f.read()
        
        # Convert to documents
        documents = extract_documents_from_file_unified(csv_content, "employees.csv")
        
        # Test text splitting (this is what happens in knowledge base creation)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        print(f"📄 Original documents: {len(documents)}")
        print(f"📄 Text chunks after splitting: {len(chunks)}")
        
        if len(chunks) > 0:
            print(f"📄 First chunk preview:")
            print(chunks[0].page_content[:200] + "...")
            
            # Check if chunks maintain metadata
            if chunks[0].metadata and 'source' in chunks[0].metadata:
                print("✅ Knowledge base compatibility: SUCCESS")
                return True
            else:
                print("❌ Knowledge base compatibility: FAILED - Metadata not preserved")
                return False
        else:
            print("❌ Knowledge base compatibility: FAILED - No chunks generated")
            return False
            
    except Exception as e:
        print(f"❌ Knowledge base compatibility error: {e}")
        return False

def main():
    """Run all targeted tests."""
    print("🧪 CSV and XLSX Functionality Tests")
    print("=" * 50)
    
    results = []
    
    # Test individual components
    results.append(test_csv_to_langchain_docs())
    print()
    results.append(test_xlsx_creation_and_conversion())
    print()
    results.append(test_knowledge_base_compatibility())
    print()
    
    # Summary
    print("📋 TEST SUMMARY")
    print("=" * 30)
    
    success_count = sum(results)
    total_count = len(results)
    
    if success_count == total_count:
        print(f"🎉 ALL TESTS PASSED ({success_count}/{total_count})")
        print("✅ CSV and XLSX files are fully compatible with the knowledge base system!")
        print("✅ Your application now supports the following file types:")
        print("   • PDF files")
        print("   • TXT files") 
        print("   • DOCX files")
        print("   • CSV files ⭐ NEW")
        print("   • XLSX files ⭐ NEW")
    else:
        print(f"⚠️  SOME TESTS FAILED ({success_count}/{total_count})")
        
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
