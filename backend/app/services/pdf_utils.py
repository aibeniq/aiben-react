"""
PDF processing utilities with optional PyMuPDF4LLM support for enhanced table parsing.
"""

import tempfile
import os
from typing import List, Optional
from pathlib import Path

import pypdf
from langchain_core.documents import Document
from fastapi import HTTPException

# Optional PyMuPDF4LLM import
try:
    import pymupdf4llm

    PYMUPDF4LLM_AVAILABLE = True
    print("PyMuPDF4LLM available - using enhanced table parsing.")
except ImportError:
    PYMUPDF4LLM_AVAILABLE = False
    print("PyMuPDF4LLM not available - table parsing will use fallback method.")


def extract_pdf_with_pymupdf4llm(
    file_path: str, filename: str = None
) -> List[Document]:
    """
    Extract PDF content using PyMuPDF4LLM for enhanced table parsing.

    Args:
        file_path: Path to the PDF file
        filename: Optional filename for metadata

    Returns:
        List of Document objects with structured content
    """
    if not PYMUPDF4LLM_AVAILABLE:
        raise ImportError("PyMuPDF4LLM is not available")

    documents = []

    try:
        # Extract as Markdown (preserves tables and structure)
        print(f"Using PyMuPDF4LLM for enhanced table parsing on {filename}")
        md_text = pymupdf4llm.to_markdown(file_path)

        # Split into pages if possible (PyMuPDF4LLM may return full document)
        # Common page separator in Markdown output
        pages = md_text.split("\n---\n")

        for page_num, page_content in enumerate(pages, 1):
            if page_content.strip():  # Only add non-empty pages
                doc = Document(
                    page_content=page_content.strip(),
                    metadata={
                        "source": filename or file_path,
                        "page": page_num,
                        "extraction_method": "pymupdf4llm_markdown",
                        "has_tables": "|" in page_content,  # Simple table detection
                    },
                )
                documents.append(doc)

    except Exception as e:
        print(f"Error with PyMuPDF4LLM extraction for {filename}: {e}")
        raise

    return documents


def load_pdf_with_pypdf(
    file_path: str, filename: str = None, use_enhanced_parsing: bool = True
) -> List[Document]:
    """
    Load PDF using pypdf library with optional PyMuPDF4LLM enhancement.

    Args:
        file_path: Path to the PDF file
        filename: Optional filename for metadata
        use_enhanced_parsing: If True, attempt PyMuPDF4LLM extraction first

    Returns:
        List of Document objects
    """
    if use_enhanced_parsing and PYMUPDF4LLM_AVAILABLE:
        try:
            return extract_pdf_with_pymupdf4llm(file_path, filename)
        except Exception as e:
            print(f"PyMuPDF4LLM failed, falling back to pypdf: {e}")
            # Fall back to pypdf

    # Original pypdf logic
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
                                "extraction_method": "pypdf_text",
                            },
                        )
                        documents.append(doc)
                except Exception as e:
                    print(f"Error extracting page {page_num + 1}: {e}")
                    continue

    except Exception as e:
        print(f"Error reading PDF {filename}: {e}")
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

    return documents


def extract_text_from_pdf_bytes(
    file_content: bytes, filename: str, use_enhanced_parsing: bool = False
) -> str:
    """
    Extract text from PDF bytes with optional enhanced parsing.

    Args:
        file_content: PDF file content as bytes
        filename: Filename for error messages
        use_enhanced_parsing: If True, use PyMuPDF4LLM for better table handling

    Returns:
        Extracted text as string
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            if use_enhanced_parsing and PYMUPDF4LLM_AVAILABLE:
                # Use enhanced parsing
                documents = extract_pdf_with_pymupdf4llm(temp_file_path, filename)
                # Convert markdown back to text, preserving table structure
                text_parts = []
                for doc in documents:
                    content = doc.page_content
                    # Convert markdown tables to text representation
                    text_parts.append(content)
                return "\n\n".join(text_parts)
            else:
                # Use original pypdf method
                documents = load_pdf_with_pypdf(
                    temp_file_path, filename, use_enhanced_parsing=False
                )
                return "\n\n".join([doc.page_content for doc in documents])

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error extracting text from PDF {filename}: {str(e)}",
        )
