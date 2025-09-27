#!/usr/bin/env python3
"""Direct test of pdfplumber table extraction with proper debugging"""

import pdfplumber
from io import BytesIO
import os


def test_pdfplumber_direct():
    """Test pdfplumber table extraction directly"""
    print("=== Direct pdfplumber Test ===")

    pdf_path = "test_files/Appendix 6 Fee Schedule.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"✅ PDF found: {pdf_path}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"\n📄 Page {page_num + 1}:")

            # Extract tables
            tables = page.extract_tables()
            print(f"   Found {len(tables)} tables")

            for table_idx, table in enumerate(tables):
                print(f"\n   Table {table_idx + 1}:")
                print(f"   Rows: {len(table)}")
                if table:
                    print(f"   Columns: {len(table[0])}")

                    # Show first few rows
                    for row_idx, row in enumerate(table[:3]):
                        print(f"   Row {row_idx + 1}: {row}")

                        # Check for corruption
                        for cell_idx, cell in enumerate(row):
                            if cell and isinstance(cell, str):
                                # Check if cell contains binary data
                                try:
                                    cell.encode("ascii")
                                except UnicodeEncodeError:
                                    print(
                                        f"      ⚠️  Cell {cell_idx + 1} contains non-ASCII: {repr(cell[:50])}"
                                    )

            # Also try extracting text to compare
            page_text = page.extract_text()
            if "Smart" in page_text or "All-inclusive" in page_text:
                print(f"\n   📝 Page text contains target terms:")
                lines = page_text.split("\n")
                for line in lines:
                    if "Smart" in line or "All-inclusive" in line:
                        print(f"      {line.strip()}")

            # Just check first page for now
            if page_num == 0:
                break


if __name__ == "__main__":
    test_pdfplumber_direct()
