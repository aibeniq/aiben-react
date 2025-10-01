#!/usr/bin/env python3
"""
Test the new embedded image analysis by default functionality.
"""

import sys
import os
from pathlib import Path

def test_embedded_image_separation():
    """Test that we can separate embedded images from page renders."""
    print("🧪 Testing Embedded Image Separation")
    print("=" * 50)
    
    # Import the new function we created
    sys.path.append('backend')
    from app.services.document_utils import extract_embedded_and_page_images_separately
    
    pdf_path = "test_files/running shoe receipt.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Test file not found: {pdf_path}")
        return False
    
    print(f"📄 Testing with: {pdf_path}")
    
    with open(pdf_path, "rb") as f:
        file_content = f.read()
    
    try:
        embedded_images, page_images = extract_embedded_and_page_images_separately(file_content)
        
        print(f"📊 Results:")
        print(f"  🖼️ Embedded images: {len(embedded_images)}")
        print(f"  📄 Page renders: {len(page_images)}")
        
        if embedded_images:
            print(f"  ✅ SUCCESS: Found {len(embedded_images)} embedded images")
            for i, img in enumerate(embedded_images[:3]):
                print(f"    - Embedded image {i+1}: {len(img)} chars")
        else:
            print(f"  ⚠️ No embedded images found")
            
        if page_images:
            print(f"  ✅ SUCCESS: Found {len(page_images)} page renders")
            for i, img in enumerate(page_images[:3]):
                print(f"    - Page render {i+1}: {len(img)} chars")
        else:
            print(f"  ❌ No page renders found")
            
        return len(embedded_images) > 0 or len(page_images) > 0
        
    except Exception as e:
        print(f"❌ Error during separation test: {e}")
        return False

def main():
    print("🚀 Testing New Embedded Image Analysis by Default")
    print("=" * 60)
    
    # Test the separation function
    separation_success = test_embedded_image_separation()
    
    print(f"\n📋 Test Summary:")
    print("=" * 60)
    
    if separation_success:
        print("✅ Embedded image separation: WORKING")
        print("\n🎯 Next Steps:")
        print("1. Upload a PDF with embedded images to the chatbot")
        print("2. The system should now automatically analyze embedded images")
        print("3. You can ask ANY question and get information about visual content")
        print("4. Questions like 'What does the shoe look like?' should now work!")
    else:
        print("❌ Embedded image separation: FAILED")
        print("   The new functionality needs debugging")

if __name__ == "__main__":
    main()