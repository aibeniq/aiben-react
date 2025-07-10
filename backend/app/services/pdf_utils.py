"""
PDF processing utilities using pypdf library (BSD license).
Replaces PyMuPDF (AGPL license) for commercial compatibility.
"""

import tempfile
import os
from typing import List
from pathlib import Path

import pypdf
from langchain_core.documents import Document
from fastapi import HTTPException


def load_pdf_with_pypdf(file_path: str, filename: str = None) -> List[Document]:
    """
    Load PDF using pypdf library (BSD license) instead of PyMuPDF.

    Args:
        file_path: Path to the PDF file
        filename: Optional filename for metadata

    Returns:
        List of Document objects with page content and metadata

    Raises:
        HTTPException: If PDF cannot be read or processed
    """
    documents = []

    try:
        with open(file_path, "rb") as file:
            pdf_reader = pypdf.PdfReader(file)

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():  # Only add pages with content
                        doc = Document(
                            page_content=text,
                            metadata={
                                "source": filename or file_path,
                                "page": page_num + 1,
                                "total_pages": len(pdf_reader.pages),
                            },
                        )
                        documents.append(doc)
                except Exception as e:
                    print(f"Error extracting text from page {page_num + 1}: {e}")
                    continue

    except Exception as e:
        print(f"Error reading PDF {filename}: {e}")
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    return documents


def extract_text_from_pdf_bytes(file_content: bytes, filename: str) -> str:
    """
    Extract text from PDF bytes using pypdf.

    Args:
        file_content: PDF file content as bytes
        filename: Filename for error messages

    Returns:
        Extracted text as string

    Raises:
        HTTPException: If PDF cannot be processed
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Load and extract text
            documents = load_pdf_with_pypdf(temp_file_path, filename)
            # Combine all page contents
            text = "\n\n".join([doc.page_content for doc in documents])
            return text
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extracting text from PDF {filename}: {str(e)}",
        )
