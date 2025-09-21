#!/usr/bin/env python3
"""
Test script to verify the new handwritten file logic - Standalone version
"""

from pathlib import Path
from typing import List, Dict, Any


class MockUploadFile:
    def __init__(self, filename: str):
        self.filename = filename


def validate_and_reclassify_files(
    digitized_files: List[MockUploadFile], handwritten_files: List[MockUploadFile]
) -> Dict[str, Any]:
    """
    Standalone version of the validation function for testing
    """
    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp",
    ]
    convertible_extensions = [".pdf", ".docx", ".doc"]
    incompatible_extensions = [".csv", ".xlsx", ".xls", ".txt", ".rtf"]

    new_digitized = []
    new_handwritten = []

    # Process digitized files - check for images that should be reclassified
    if digitized_files:
        for file in digitized_files:
            file_ext = Path(file.filename).suffix.lower()

            if file_ext in image_extensions:
                # Image files always go to handwritten processing
                print(
                    f"🔄 Reclassifying image file {file.filename} to handwritten processing"
                )
                new_handwritten.append(file)
            else:
                # Keep in digitized
                new_digitized.append(file)

    # Process handwritten files - validate compatibility
    if handwritten_files:
        for file in handwritten_files:
            file_ext = Path(file.filename).suffix.lower()

            if file_ext in incompatible_extensions:
                # These file types are not compatible with handwritten processing
                error_msg = f"File '{file.filename}' with extension '{file_ext.upper()}' is not compatible with handwritten processing. Supported handwritten file types are: images (JPG, PNG, etc.), PDF, DOCX, and DOC files."
                return {"error": error_msg}
            elif file_ext in image_extensions or file_ext in convertible_extensions:
                # These are valid for handwritten processing
                new_handwritten.append(file)
            else:
                # Unknown extension - allow but warn
                print(
                    f"⚠️ Unknown file extension {file_ext} for handwritten processing: {file.filename}"
                )
                new_handwritten.append(file)

    return {"digitized_files": new_digitized, "handwritten_files": new_handwritten}


def test_file_reclassification():
    """Test the new file reclassification logic"""
    print("🧪 Testing handwritten file reclassification logic...")
    print("=" * 60)

    # Test Case 1: Image files should always go to handwritten
    print("\n📋 Test Case 1: Image files reclassification")
    digitized = [MockUploadFile("photo.jpg"), MockUploadFile("document.pdf")]
    handwritten = []

    result = validate_and_reclassify_files(digitized, handwritten)
    print(f"Before: {len(digitized)} digitized, {len(handwritten)} handwritten")
    print(
        f"After: {len(result['digitized_files'])} digitized, {len(result['handwritten_files'])} handwritten"
    )
    print(
        f"✅ JPG file correctly moved to handwritten: {'photo.jpg' in [f.filename for f in result['handwritten_files']]}"
    )
    print(
        f"✅ PDF file stayed in digitized: {'document.pdf' in [f.filename for f in result['digitized_files']]}"
    )

    # Test Case 2: Incompatible handwritten files should error
    print("\n📋 Test Case 2: Incompatible handwritten files")
    digitized = []
    handwritten = [MockUploadFile("data.csv"), MockUploadFile("report.xlsx")]

    result = validate_and_reclassify_files(digitized, handwritten)
    print(f"Expected error for CSV/XLSX: {'error' in result}")
    if "error" in result:
        print(f"Error message: {result['error']}")

    # Test Case 3: Valid handwritten files should pass
    print("\n📋 Test Case 3: Valid handwritten files")
    digitized = []
    handwritten = [
        MockUploadFile("scan.png"),
        MockUploadFile("form.pdf"),
        MockUploadFile("notes.docx"),
    ]

    result = validate_and_reclassify_files(digitized, handwritten)
    print(f"No error for valid files: {'error' not in result}")
    print(
        f"All files in handwritten: {len(result['handwritten_files'])} == 3: {len(result['handwritten_files']) == 3}"
    )

    # Test Case 4: Mixed scenario
    print("\n📋 Test Case 4: Mixed scenario - image in digitized + PDF in handwritten")
    digitized = [MockUploadFile("screenshot.png"), MockUploadFile("text.docx")]
    handwritten = [MockUploadFile("scanned_form.pdf")]

    result = validate_and_reclassify_files(digitized, handwritten)
    print(f"Before: {len(digitized)} digitized, {len(handwritten)} handwritten")
    print(
        f"After: {len(result['digitized_files'])} digitized, {len(result['handwritten_files'])} handwritten"
    )
    print(
        f"✅ PNG moved to handwritten: {'screenshot.png' in [f.filename for f in result['handwritten_files']]}"
    )
    print(
        f"✅ DOCX stayed in digitized: {'text.docx' in [f.filename for f in result['digitized_files']]}"
    )
    print(
        f"✅ PDF stayed in handwritten: {'scanned_form.pdf' in [f.filename for f in result['handwritten_files']]}"
    )

    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    test_file_reclassification()
