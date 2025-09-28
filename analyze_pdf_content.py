#!/usr/bin/env python3
"""
Analyze the actual content of the Fee Schedule PDF to understand table patterns.
"""

import sys
import os
from pathlib import Path

# Add the backend app to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def analyze_pdf_content():
    """Analyze the PDF content to understand table patterns."""
    print("🔍 Analyzing Fee Schedule PDF Content")
    print("=" * 50)

    # Set up environment
    os.environ.setdefault("PROJECT_NAME", "debug")
    os.environ.setdefault("POSTGRES_SERVER", "localhost")
    os.environ.setdefault("POSTGRES_USER", "test")
    os.environ.setdefault("FIRST_SUPERUSER", "debug@example.com")
    os.environ.setdefault("FIRST_SUPERUSER_PASSWORD", "test")

    try:
        test_file = Path(__file__).parent / "test_files" / "Appendix 6 Fee Schedule.pdf"

        with open(test_file, "rb") as f:
            file_content = f.read()

        from app.services.document_utils import (
            extract_documents_and_images_from_file_unified,
        )

        documents, images = extract_documents_and_images_from_file_unified(
            file_content, test_file.name
        )

        print(f"📄 Analyzing {len(documents)} document pages")

        for i, doc in enumerate(documents):
            content = doc.page_content
            print(f"\n📋 Page {i} Content ({len(content)} chars):")
            print("-" * 40)

            # Show first 1000 characters of each page
            preview = content[:1000] if len(content) > 1000 else content
            print(preview)

            if len(content) > 1000:
                print("... [content truncated] ...")

            # Look for table-like patterns
            lines = content.split("\n")
            numeric_lines = [line for line in lines if any(c.isdigit() for c in line)]

            if numeric_lines:
                print(f"\n🔢 Found {len(numeric_lines)} lines with numbers:")
                for line in numeric_lines[:5]:  # Show first 5 numeric lines
                    print(f"   {line.strip()}")
                if len(numeric_lines) > 5:
                    print(f"   ... and {len(numeric_lines) - 5} more")

            print("\n" + "=" * 50)

        return True

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    analyze_pdf_content()
