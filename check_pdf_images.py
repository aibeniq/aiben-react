#!/usr/bin/env python3
"""
Script to check if a PDF has embedded images using the same logic as the application.
"""

import sys
import os
from pathlib import Path
import base64

def extract_images_from_pdf_bytes(file_content: bytes):
    """Extract images from PDF bytes using PyMuPDF."""
    import logging
    
    logger = logging.getLogger(__name__)
    images = []
    embedded_images = []
    page_images = []

    try:
        # Try to import fitz (PyMuPDF)
        import fitz

        doc = fitz.open("pdf", file_content)
        print(f"📄 PDF Info: {doc.page_count} pages")

        for page_num in range(min(doc.page_count, 10)):  # Limit pages
            page = doc[page_num]
            print(f"\n📃 Page {page_num + 1}:")

            # Check for embedded images first
            image_list = page.get_images()
            print(f"  🖼️ Embedded images found: {len(image_list)}")
            
            for img_index, img in enumerate(image_list[:3]):  # Limit embedded images
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    img_base64 = base64.b64encode(image_bytes).decode()
                    embedded_images.append(img_base64)
                    print(f"    - Embedded image {img_index + 1}: {len(image_bytes)} bytes -> {len(img_base64)} chars base64")
                    print(f"      Format: {base_image.get('ext', 'unknown')}")
                except Exception as e:
                    print(f"    - Failed to extract embedded image {img_index + 1}: {e}")
                    continue

            # Convert page to image for comprehensive analysis
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                img_data = pix.tobytes("png")
                img_base64 = base64.b64encode(img_data).decode()
                page_images.append(img_base64)
                print(f"  📸 Page as image: {len(img_data)} bytes -> {len(img_base64)} chars base64")
            except Exception as e:
                print(f"  ❌ Failed to convert page to image: {e}")

        doc.close()
        
        # Combine all images
        all_images = embedded_images + page_images
        
        print(f"\n📊 Summary:")
        print(f"  - Embedded images: {len(embedded_images)}")
        print(f"  - Page images: {len(page_images)}")
        print(f"  - Total images: {len(all_images)}")
        
        return all_images

    except ImportError:
        print("❌ PyMuPDF not available for PDF image extraction")
        return []
    except Exception as e:
        print(f"❌ PDF image extraction error: {e}")
        return []

def main():
    pdf_path = "test_files/david employment verification letter.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"🔍 Analyzing PDF: {pdf_path}")
    
    with open(pdf_path, "rb") as f:
        file_content = f.read()
    
    print(f"📁 File size: {len(file_content):,} bytes")
    
    images = extract_images_from_pdf_bytes(file_content)
    
    print(f"\n🎯 Result: {'Has images' if images else 'No images found'}")
    
    if images:
        print(f"\n✅ This PDF contains {len(images)} extractable images!")
        print("   The vision processing should be able to analyze them.")
    else:
        print("\n❌ No images found in this PDF.")
        print("   This explains why vision processing isn't triggered.")

if __name__ == "__main__":
    main()