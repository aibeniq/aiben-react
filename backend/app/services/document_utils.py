"""
Unified document processing utilities.
Centralizes all document text extraction logic for consistent handling across the application.
"""

import tempfile
import os
from pathlib import Path
from typing import List, Union, Any
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader


def extract_text_from_docx_bytes(file_content: bytes, filename: str) -> str:
    """
    Extract text from DOCX file content (bytes).

    Args:
        file_content: Raw bytes of the DOCX file
        filename: Name of the file (for metadata/error reporting)

    Returns:
        Extracted text content as string
    """
    try:
        from docx import Document as DocxDocument

        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        # File is now closed and ready to be read by docx

        try:
            doc = DocxDocument(temp_file_path)
            text_parts = []

            # Extract text from paragraphs
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)

            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        text_parts.append(" | ".join(row_text))

            return "\n\n".join(text_parts)

        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        print(f"Error extracting text from DOCX {filename}: {e}")
        return f"Failed to extract text from {filename}: {str(e)}"


def extract_text_from_docx_path(file_path: str, filename: str) -> str:
    """
    Extract text from DOCX file path.

    Args:
        file_path: Path to the DOCX file
        filename: Name of the file (for metadata/error reporting)

    Returns:
        Extracted text content as string
    """
    try:
        from docx import Document as DocxDocument

        doc = DocxDocument(file_path)
        text_parts = []

        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_parts.append(" | ".join(row_text))

        return "\n\n".join(text_parts)

    except Exception as e:
        print(f"Error extracting text from DOCX {filename}: {e}")
        return f"Failed to extract text from {filename}: {str(e)}"


def extract_text_from_docx_langchain(file_path: str, filename: str) -> List[Document]:
    """
    Extract text from DOCX file and return as LangChain Document objects.
    Compatible with existing knowledge base processing.

    Args:
        file_path: Path to the DOCX file
        filename: Name of the file (for metadata)

    Returns:
        List of LangChain Document objects
    """
    try:
        from docx import Document as DocxDocument

        doc = DocxDocument(file_path)
        text_parts = []

        # Extract text from paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_parts.append(" | ".join(row_text))

        combined_text = "\n\n".join(text_parts)

        # Create metadata
        metadata = {
            "source": filename,
            "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }

        # Try to get document properties
        try:
            core_properties = doc.core_properties
            if core_properties.title:
                metadata["title"] = core_properties.title
            if core_properties.author:
                metadata["author"] = core_properties.author
            if core_properties.created:
                metadata["created"] = str(core_properties.created)
            if core_properties.modified:
                metadata["modified"] = str(core_properties.modified)
        except Exception as e:
            print(f"Could not extract document properties: {str(e)}")

        return [Document(page_content=combined_text, metadata=metadata)]

    except Exception as e:
        print(f"Error extracting text from DOCX {filename}: {e}")
        error_doc = Document(
            page_content=f"Failed to extract text from {filename}: {str(e)}",
            metadata={"source": filename, "error": True},
        )
        return [error_doc]


def extract_text_from_file_unified(file_content: bytes, filename: str) -> str:
    """
    Unified file text extraction function that handles multiple file types.
    This is the main entry point for document text extraction.

    Args:
        file_content: Raw bytes of the file
        filename: Name of the file

    Returns:
        Extracted text content as string
    """
    try:
        # Determine file type from extension
        file_ext = Path(filename).suffix.lower()

        if file_ext == ".pdf":
            # Handle PDF files
            from app.services.pdf_utils import extract_text_from_pdf_bytes

            return extract_text_from_pdf_bytes(file_content, filename)

        elif file_ext in [".docx", ".doc"]:
            # Handle Word documents using our unified DOCX function
            if file_ext == ".docx":
                return extract_text_from_docx_bytes(file_content, filename)
            else:
                # For .doc files, fall back to textloader approach
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=file_ext
                ) as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                try:
                    loader = TextLoader(temp_file_path, encoding="utf-8")
                    documents = loader.load()
                    return "\n\n".join([doc.page_content for doc in documents])
                except UnicodeDecodeError:
                    try:
                        loader = TextLoader(temp_file_path, encoding="latin-1")
                        documents = loader.load()
                        return "\n\n".join([doc.page_content for doc in documents])
                    except Exception as e:
                        return f"Failed to extract text from {filename}: {str(e)}"
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

        elif file_ext in [".txt", ".md"]:
            # Handle text files
            try:
                return file_content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    return file_content.decode("latin-1")
                except UnicodeDecodeError:
                    return f"Unable to extract text from {filename} - encoding issue"

        else:
            # Try to decode as text for unknown file types
            try:
                return file_content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    return file_content.decode("latin-1")
                except UnicodeDecodeError:
                    return f"Unable to extract text from {filename} - unsupported file format"

    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return f"Failed to extract text from {filename}: {str(e)}"


def extract_documents_from_file_unified(
    file_content: bytes, filename: str
) -> List[Document]:
    """
    Unified file extraction function that returns LangChain Document objects.
    Used by vector search and knowledge base processing.

    Args:
        file_content: Raw bytes of the file
        filename: Name of the file

    Returns:
        List of LangChain Document objects
    """
    try:
        # Determine file type from extension
        file_ext = Path(filename).suffix.lower()

        if file_ext == ".pdf":
            # Handle PDF files
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                from app.services.pdf_utils import load_pdf_with_pypdf

                return load_pdf_with_pypdf(temp_file_path, filename)
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        elif file_ext in [".docx", ".doc"]:
            # Handle Word documents
            if file_ext == ".docx":
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".docx"
                ) as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                try:
                    return extract_text_from_docx_langchain(temp_file_path, filename)
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            else:
                # For .doc files, fall back to textloader
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=file_ext
                ) as temp_file:
                    temp_file.write(file_content)
                    temp_file_path = temp_file.name

                try:
                    loader = TextLoader(temp_file_path, encoding="utf-8")
                    documents = loader.load()
                    return documents
                except UnicodeDecodeError:
                    try:
                        loader = TextLoader(temp_file_path, encoding="latin-1")
                        documents = loader.load()
                        return documents
                    except Exception as e:
                        error_doc = Document(
                            page_content=f"Failed to extract text from {filename}: {str(e)}",
                            metadata={"source": filename, "error": True},
                        )
                        return [error_doc]
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

        elif file_ext in [".txt", ".md"]:
            # Handle text files
            try:
                text_content = file_content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text_content = file_content.decode("latin-1")
                except UnicodeDecodeError:
                    text_content = (
                        f"Unable to extract text from {filename} - encoding issue"
                    )

            return [
                Document(
                    page_content=text_content,
                    metadata={"source": filename, "content_type": "text/plain"},
                )
            ]

        else:
            # Try to decode as text for unknown file types
            try:
                text_content = file_content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text_content = file_content.decode("latin-1")
                except UnicodeDecodeError:
                    text_content = f"Unable to extract text from {filename} - unsupported file format"

            return [
                Document(
                    page_content=text_content,
                    metadata={"source": filename, "content_type": "unknown"},
                )
            ]

    except Exception as e:
        print(f"Error extracting documents from {filename}: {e}")
        error_doc = Document(
            page_content=f"Failed to extract text from {filename}: {str(e)}",
            metadata={"source": filename, "error": True},
        )
        return [error_doc]
