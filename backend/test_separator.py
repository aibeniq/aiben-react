import sys
import os
import asyncio

sys.path.append(".")

from app.services.pdf_utils import extract_pdf_with_pymupdf4llm


async def test_extraction():
    # Test with a PDF file from test_files directory
    pdf_path = "../test_files/SBI.pdf"  # Use SBI.pdf as test file

    if os.path.exists(pdf_path):
        print(f"Testing PDF extraction with: {pdf_path}")
        result = await extract_pdf_with_pymupdf4llm(pdf_path)
        print("Extraction completed. Check debug output above.")
    else:
        print(f"PDF file not found: {pdf_path}")


# Run the async test
asyncio.run(test_extraction())
