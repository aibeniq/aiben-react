"""
PDF processing utilities with optional PyMuPDF4LLM support for enhanced table parsing.
"""

import tempfile
import os
import asyncio
from typing import List, Optional, Tuple
from pathlib import Path

import pypdf
import fitz  # PyMuPDF for fast table detection
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


def has_tables_fast(file_path: str) -> Tuple[bool, int]:
    """
    Fast table detection using vanilla PyMuPDF geometric analysis.

    This function quickly scans the PDF for tables without heavy processing,
    using PyMuPDF's built-in table detection based on geometric cues.

    Args:
        file_path: Path to the PDF file

    Returns:
        Tuple of (has_tables: bool, table_count: int)
    """
    try:
        doc = fitz.open(file_path)
        table_count = 0

        for page_num in range(len(doc)):
            page = doc[page_num]
            tables = page.find_tables()
            if tables.tables:
                table_count += len(tables.tables)

        doc.close()
        has_tables = table_count > 0

        if has_tables:
            print(f"Fast table detection: Found {table_count} table(s) in {file_path}")
        else:
            print(f"Fast table detection: No tables found in {file_path}")

        return has_tables, table_count

    except Exception as e:
        print(
            f"Error during fast table detection: {e}. Assuming tables present for safety."
        )
        # If detection fails, assume tables are present to be safe
        return True, 0


def _extract_pdf_with_pymupdf4llm_sync(
    file_path: str, filename: str = None
) -> List[str]:
    """
    Synchronous helper to extract PDF content using PyMuPDF4LLM.
    This function runs the CPU-intensive extraction in a separate thread.

    Args:
        file_path: Path to the PDF file
        filename: Optional filename for logging

    Returns:
        List of page chunks extracted from the PDF using native page boundaries
    """
    print(f"Using PyMuPDF4LLM for enhanced table parsing on {filename}")
    # Use page_chunks=True to get native page boundaries from PyMuPDF4LLM
    page_chunks = pymupdf4llm.to_markdown(file_path, page_chunks=True)
    return page_chunks


async def extract_pdf_with_pymupdf4llm(
    file_path: str, filename: str = None, skip_table_check: bool = False
) -> List[Document]:
    """
    Extract PDF content using PyMuPDF4LLM for enhanced table parsing.

    This function runs the CPU-intensive PyMuPDF processing in a thread pool
    to avoid blocking the async event loop, allowing progress updates to be served.

    This function first performs a fast table detection check using vanilla PyMuPDF.
    If no tables are detected, it falls back to basic pypdf extraction to avoid
    unnecessary heavy processing.

    Args:
        file_path: Path to the PDF file
        filename: Optional filename for metadata
        skip_table_check: If True, skip the fast table check and force PyMuPDF4LLM usage

    Returns:
        List of Document objects with structured content
    """
    if not PYMUPDF4LLM_AVAILABLE:
        raise ImportError("PyMuPDF4LLM is not available")

    # Fast table detection pre-check (unless explicitly skipped)
    if not skip_table_check:
        has_tables, table_count = has_tables_fast(file_path)
        if not has_tables:
            print(
                f"No tables detected in {filename}. Using fast pypdf extraction instead."
            )
            # Note: load_pdf_with_pypdf is now async, so we need to await it
            return await load_pdf_with_pypdf(file_path, filename, parsing_mode="basic")

    documents = []

    try:
        # Run the CPU-intensive extraction in a thread pool to avoid blocking
        # the async event loop. This allows progress API requests to be served
        # while PyMuPDF4LLM is processing the PDF.
        page_chunks = await asyncio.to_thread(
            _extract_pdf_with_pymupdf4llm_sync, file_path, filename
        )

        # Process each page chunk with correct page numbering
        for page_num, page_chunk in enumerate(page_chunks, 1):
            # Extract text from the chunk dictionary
            if isinstance(page_chunk, dict) and "text" in page_chunk:
                page_content = page_chunk["text"]
            else:
                # Fallback for unexpected format
                page_content = str(page_chunk)

            # Add page even if content appears empty - PyMuPDF4LLM page_chunks are reliable
            # (empty pages are valid, e.g., cover pages, separator pages)
            doc = Document(
                page_content=page_content.strip() if page_content else "",
                metadata={
                    "source": filename or file_path,
                    "page": page_num,
                    "extraction_method": "pymupdf4llm_native_chunks",
                    "has_tables": "|" in page_content if page_content else False,
                },
            )
            documents.append(doc)

        # DEBUG: Print info about the extracted chunks
        print(f"[DEBUG] PyMuPDF4LLM extracted {len(page_chunks)} page chunks")
        print(f"[DEBUG] Created {len(documents)} Document objects")
        print(
            f"[DEBUG] Document page numbers: {[d.metadata.get('page') for d in documents[:10]]}..."
        )

    except Exception as e:
        print(f"Error with PyMuPDF4LLM extraction for {filename}: {e}")
        raise

    return documents


async def load_pdf_with_pypdf(
    file_path: str, filename: str = None, parsing_mode: str = "auto"
) -> List[Document]:
    """
    Load PDF using pypdf library with optional PyMuPDF4LLM enhancement.

    This function is async to allow the CPU-intensive PyMuPDF4LLM processing
    to run in a thread pool without blocking the event loop.

    Parsing modes:
    - 'auto': Automatically detect tables and use enhanced parsing if tables exist
    - 'enhanced': Always use PyMuPDF4LLM if available (force enhanced parsing)
    - 'basic': Always use basic pypdf extraction (skip enhanced parsing)

    Args:
        file_path: Path to the PDF file
        filename: Optional filename for metadata
        parsing_mode: PDF parsing mode ('auto', 'enhanced', or 'basic')

    Returns:
        List of Document objects
    """
    # Normalize mode to lowercase
    mode = parsing_mode.lower()

    # DEBUG: Log the parsing mode being used
    print(f"[PDF_UTILS] load_pdf_with_pypdf called with mode='{mode}' for {filename}")

    if mode == "enhanced":
        # Force enhanced parsing if available
        if PYMUPDF4LLM_AVAILABLE:
            try:
                print(f"Using enhanced parsing (forced) for {filename}")
                return await extract_pdf_with_pymupdf4llm(
                    file_path, filename, skip_table_check=True
                )
            except Exception as e:
                print(f"PyMuPDF4LLM failed, falling back to pypdf: {e}")
                # Fall back to pypdf
        else:
            print(
                f"Enhanced parsing requested but PyMuPDF4LLM not available, using basic pypdf for {filename}"
            )

    elif mode == "auto" and PYMUPDF4LLM_AVAILABLE:
        # Fast table detection pre-check
        has_tables, table_count = has_tables_fast(file_path)

        if has_tables:
            try:
                # Tables detected - use PyMuPDF4LLM for better extraction
                print(
                    f"Tables detected ({table_count}), using PyMuPDF4LLM for {filename}"
                )
                return await extract_pdf_with_pymupdf4llm(
                    file_path, filename, skip_table_check=True
                )
            except Exception as e:
                print(f"PyMuPDF4LLM failed, falling back to pypdf: {e}")
                # Fall back to pypdf
        else:
            print(f"No tables detected, using fast pypdf extraction for {filename}")

    # Use basic pypdf for mode='basic' or as fallback

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
    file_content: bytes, filename: str, parsing_mode: str = "auto"
) -> str:
    """
    Extract text from PDF bytes with configurable parsing mode.

    This is a SYNC wrapper that runs the async PDF extraction in a new event loop.
    Use this when called from synchronous code that needs PDF text extraction.

    Parsing modes:
    - 'auto': Automatically detect tables and use enhanced parsing if tables exist
    - 'enhanced': Always use PyMuPDF4LLM if available (force enhanced parsing)
    - 'basic': Always use basic pypdf extraction (skip enhanced parsing)

    Args:
        file_content: PDF file content as bytes
        filename: Filename for error messages
        parsing_mode: PDF parsing mode ('auto', 'enhanced', or 'basic')

    Returns:
        Extracted text as string
    """
    import asyncio

    # Run the async version in a new event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                extract_text_from_pdf_bytes_async(file_content, filename, parsing_mode)
            )
        finally:
            loop.close()
    except RuntimeError as e:
        # If there's already a running loop, try to get it
        if "There is no current event loop" not in str(e):
            raise
        # Fallback: run in the current loop if it exists
        return asyncio.run(
            extract_text_from_pdf_bytes_async(file_content, filename, parsing_mode)
        )


async def extract_text_from_pdf_bytes_async(
    file_content: bytes, filename: str, parsing_mode: str = "auto"
) -> str:
    """
    Extract text from PDF bytes with configurable parsing mode (ASYNC version).

    Parsing modes:
    - 'auto': Automatically detect tables and use enhanced parsing if tables exist
    - 'enhanced': Always use PyMuPDF4LLM if available (force enhanced parsing)
    - 'basic': Always use basic pypdf extraction (skip enhanced parsing)

    Args:
        file_content: PDF file content as bytes
        filename: Filename for error messages
        parsing_mode: PDF parsing mode ('auto', 'enhanced', or 'basic')

    Returns:
        Extracted text as string
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # Normalize mode to lowercase
            mode = parsing_mode.lower()

            if mode == "enhanced":
                # Force enhanced parsing if available
                if PYMUPDF4LLM_AVAILABLE:
                    print(f"Using enhanced parsing (forced) for {filename}")
                    documents = await extract_pdf_with_pymupdf4llm(
                        temp_file_path, filename, skip_table_check=True
                    )
                    return "\n\n".join([doc.page_content for doc in documents])
                else:
                    print(
                        f"Enhanced parsing requested but PyMuPDF4LLM not available, using basic pypdf for {filename}"
                    )
                    documents = await load_pdf_with_pypdf(
                        temp_file_path, filename, parsing_mode="basic"
                    )
                    return "\n\n".join([doc.page_content for doc in documents])

            elif mode == "auto" and PYMUPDF4LLM_AVAILABLE:
                # Fast table detection pre-check
                has_tables, table_count = has_tables_fast(temp_file_path)

                if has_tables:
                    # Tables detected - use enhanced parsing
                    print(
                        f"Tables detected ({table_count}), using PyMuPDF4LLM for {filename}"
                    )
                    documents = await extract_pdf_with_pymupdf4llm(
                        temp_file_path, filename, skip_table_check=True
                    )
                    return "\n\n".join([doc.page_content for doc in documents])
                else:
                    print(
                        f"No tables detected, using fast pypdf extraction for {filename}"
                    )
                    # No tables - use fast pypdf method
                    documents = await load_pdf_with_pypdf(
                        temp_file_path, filename, parsing_mode="basic"
                    )
                    return "\n\n".join([doc.page_content for doc in documents])
            else:
                # Use basic pypdf method (mode='basic' or fallback)
                documents = await load_pdf_with_pypdf(
                    temp_file_path, filename, parsing_mode="basic"
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
