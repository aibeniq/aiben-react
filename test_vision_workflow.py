#!/usr/bin/env python3
"""
Test the vision processing workflow with the actual test document.
"""

import sys
import os
import base64
import json

def test_vision_question_detection():
    """Test if the vision question detection works."""
    print("🧠 Testing vision question detection...")
    
    # Test the exact question you asked
    test_question = "What is the logo at the top of the letter?"
    
    # Copy the exact logic from chatbot.py
    def is_vision_related_question(question: str) -> bool:
        """Check if a question is related to visual content."""
        vision_keywords = [
            'logo', 'image', 'picture', 'photo', 'diagram', 'chart', 'graph', 'table',
            'visual', 'figure', 'illustration', 'graphic', 'color', 'colours', 'layout',
            'format', 'design', 'signature', 'stamp', 'letterhead', 'header', 'footer'
        ]
        
        vision_phrases = [
            r'what.*(?:logo|image|picture|photo)',
            r'show.*(?:logo|image|picture|photo)', 
            r'describe.*(?:visual|image|picture|photo)',
            r'what.*(?:color|colour)',
            r'how.*(?:look|appear)',
            r'what.*(?:see|shown|displayed)',
            r'analyze.*(?:image|visual|picture)'
        ]
        
        import re
        question_lower = question.lower()
        
        # Check for vision keywords
        for keyword in vision_keywords:
            if keyword in question_lower:
                print(f"  ✅ Matched keyword: '{keyword}'")
                return True
        
        # Check for vision phrases
        for phrase_pattern in vision_phrases:
            if re.search(phrase_pattern, question_lower):
                print(f"  ✅ Matched phrase pattern: '{phrase_pattern}'")
                return True
        
        print("  ❌ No vision-related content detected")
        return False
    
    result = is_vision_related_question(test_question)
    print(f"Question: '{test_question}'")
    print(f"Is vision-related: {result}")
    
    return result

def test_image_extraction():
    """Test image extraction from the PDF."""
    print("\n🖼️ Testing image extraction...")
    
    pdf_path = "test_files/david employment verification letter.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return None
    
    with open(pdf_path, "rb") as f:
        file_content = f.read()
    
    # Use the same extraction logic as the application
    try:
        import fitz
        doc = fitz.open("pdf", file_content)
        
        images = []
        page = doc[0]  # First page
        
        # Extract embedded images
        image_list = page.get_images()
        print(f"Found {len(image_list)} embedded images")
        
        for img_index, img in enumerate(image_list[:3]):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                img_base64 = base64.b64encode(image_bytes).decode()
                images.append(img_base64)
                print(f"  - Extracted embedded image {img_index + 1}: {len(img_base64)} chars")
            except Exception as e:
                print(f"  - Failed to extract embedded image {img_index + 1}: {e}")
        
        # Convert page to image
        try:
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode()
            images.append(img_base64)
            print(f"  - Page as image: {len(img_base64)} chars")
        except Exception as e:
            print(f"  - Failed to convert page to image: {e}")
        
        doc.close()
        
        print(f"Total images extracted: {len(images)}")
        return images
        
    except Exception as e:
        print(f"❌ Image extraction failed: {e}")
        return None

def main():
    print("🧪 Testing Complete Vision Processing Workflow")
    print("=" * 50)
    
    # Test 1: Vision question detection
    is_vision_question = test_vision_question_detection()
    
    # Test 2: Image extraction
    images = test_image_extraction()
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 50)
    
    if is_vision_question:
        print("✅ Vision question detection: WORKING")
    else:
        print("❌ Vision question detection: FAILED")
    
    if images and len(images) > 0:
        print(f"✅ Image extraction: WORKING ({len(images)} images)")
    else:
        print("❌ Image extraction: FAILED")
    
    if is_vision_question and images:
        print("\n🎉 CONCLUSION: The vision processing should work!")
        print("   Both vision detection and image extraction are functioning.")
        print("   If it's still not working, the issue might be in the backend integration.")
    else:
        print("\n⚠️ CONCLUSION: Vision processing has issues.")
        if not is_vision_question:
            print("   - Vision question detection needs fixing")
        if not images:
            print("   - Image extraction needs fixing")

if __name__ == "__main__":
    main()