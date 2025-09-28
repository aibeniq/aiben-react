"""
Unified document processing utilities.
Centralizes all document text extraction logic for consistent handling across the application.
"""

import tempfile
import os
import logging
from pathlib import Path
from typing import List, Union, Any, Tuple, Dict, Optional
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader

# Set up logger for document processing
logger = logging.getLogger(__name__)


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


def extract_text_from_csv_bytes(file_content: bytes, filename: str) -> str:
    """
    Extract text from CSV file content (bytes).

    Args:
        file_content: Raw bytes of the CSV file
        filename: Name of the file (for metadata/error reporting)

    Returns:
        Extracted text content as string
    """
    try:
        import pandas as pd
        from io import BytesIO

        # Try to read the CSV with different encodings
        try:
            # Try UTF-8 first
            csv_string = file_content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                # Fall back to latin-1
                csv_string = file_content.decode("latin-1")
            except UnicodeDecodeError:
                # Fall back to cp1252 (Windows encoding)
                csv_string = file_content.decode("cp1252")

        # Read CSV into DataFrame
        csv_io = BytesIO(csv_string.encode("utf-8"))
        df = pd.read_csv(csv_io)

        # Convert DataFrame to readable text format
        text_parts = []

        # Add column headers
        text_parts.append("Column Headers:")
        text_parts.append(" | ".join(df.columns.astype(str)))
        text_parts.append("")  # Empty line for separation

        # Add data rows (limit to reasonable number for text extraction)
        max_rows = min(1000, len(df))  # Limit to 1000 rows for performance
        text_parts.append(f"Data ({max_rows} of {len(df)} rows):")

        for index, row in df.head(max_rows).iterrows():
            row_text = " | ".join(row.astype(str).fillna(""))
            text_parts.append(row_text)

        # Add summary information
        text_parts.append("")
        text_parts.append(f"CSV Summary: {len(df)} rows, {len(df.columns)} columns")

        return "\n".join(text_parts)

    except Exception as e:
        print(f"Error extracting text from CSV {filename}: {e}")
        return f"Failed to extract text from CSV {filename}: {str(e)}"


def extract_text_from_xlsx_bytes(file_content: bytes, filename: str) -> str:
    """
    Extract text from XLSX file content (bytes).

    Args:
        file_content: Raw bytes of the XLSX file
        filename: Name of the file (for metadata/error reporting)

    Returns:
        Extracted text content as string
    """
    try:
        import pandas as pd
        from io import BytesIO

        # Read XLSX into DataFrame
        xlsx_io = BytesIO(file_content)

        # Read all sheets
        excel_file = pd.ExcelFile(xlsx_io)
        text_parts = []

        text_parts.append(f"Excel file with {len(excel_file.sheet_names)} sheet(s)")
        text_parts.append("")

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(xlsx_io, sheet_name=sheet_name)

            text_parts.append(f"=== Sheet: {sheet_name} ===")

            # Add column headers
            text_parts.append("Column Headers:")
            text_parts.append(" | ".join(df.columns.astype(str)))
            text_parts.append("")

            # Add data rows (limit to reasonable number for text extraction)
            max_rows = min(500, len(df))  # Limit to 500 rows per sheet for performance
            text_parts.append(f"Data ({max_rows} of {len(df)} rows):")

            for index, row in df.head(max_rows).iterrows():
                row_text = " | ".join(row.astype(str).fillna(""))
                text_parts.append(row_text)

            # Add summary for this sheet
            text_parts.append("")
            text_parts.append(
                f"Sheet Summary: {len(df)} rows, {len(df.columns)} columns"
            )
            text_parts.append("")

        return "\n".join(text_parts)

    except Exception as e:
        print(f"Error extracting text from XLSX {filename}: {e}")
        return f"Failed to extract text from XLSX {filename}: {str(e)}"


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

        elif file_ext == ".csv":
            # Handle CSV files
            return extract_text_from_csv_bytes(file_content, filename)

        elif file_ext in [".xlsx", ".xls"]:
            # Handle Excel files
            return extract_text_from_xlsx_bytes(file_content, filename)

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

        elif file_ext == ".csv":
            # Handle CSV files
            text_content = extract_text_from_csv_bytes(file_content, filename)
            return [
                Document(
                    page_content=text_content,
                    metadata={"source": filename, "content_type": "text/csv"},
                )
            ]

        elif file_ext in [".xlsx", ".xls"]:
            # Handle Excel files
            text_content = extract_text_from_xlsx_bytes(file_content, filename)
            return [
                Document(
                    page_content=text_content,
                    metadata={
                        "source": filename,
                        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    },
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


def extract_documents_and_images_from_file_unified(
    file_content: bytes, filename: str
) -> Tuple[List[Document], List[str]]:
    """
    Enhanced unified extraction that returns both text documents and images.

    Args:
        file_content: Raw bytes of the file
        filename: Name of the file

    Returns:
        Tuple of (text_documents, image_list_base64)
    """
    import base64
    import logging

    logger = logging.getLogger(__name__)

    # Get existing text extraction
    documents = extract_documents_from_file_unified(file_content, filename)

    # Extract images based on file type
    images = []
    file_ext = Path(filename).suffix.lower() if "." in filename else ""

    try:
        if file_ext == ".pdf":
            images = extract_images_from_pdf_bytes(file_content)
        elif file_ext in [".docx", ".doc"]:
            images = extract_images_from_docx_bytes(file_content)
        elif file_ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]:
            # Single image file
            img_base64 = base64.b64encode(file_content).decode()
            images = [img_base64]
    except Exception as e:
        logger.error(f"Error extracting images from {filename}: {e}")

    return documents, images


def extract_images_from_pdf_bytes(file_content: bytes) -> List[str]:
    """Extract images from PDF bytes using PyMuPDF or similar library."""
    import base64
    import logging

    logger = logging.getLogger(__name__)
    images = []

    try:
        # Try to import fitz (PyMuPDF)
        import fitz

        doc = fitz.open("pdf", file_content)

        for page_num in range(min(doc.page_count, 10)):  # Limit pages
            page = doc[page_num]

            # Convert page to image for comprehensive analysis
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode()
            images.append(img_base64)

            # Extract embedded images
            image_list = page.get_images()
            for img_index, img in enumerate(image_list[:3]):  # Limit embedded images
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    img_base64 = base64.b64encode(image_bytes).decode()
                    images.append(img_base64)
                except:
                    continue

        doc.close()

    except ImportError:
        logger.warning("PyMuPDF not available for PDF image extraction")
        # Fallback: Convert entire PDF to page images using pdf2image
        try:
            from pdf2image import convert_from_bytes

            pages = convert_from_bytes(file_content, dpi=150, fmt="PNG")
            for page in pages[:5]:  # Limit to 5 pages
                import io

                img_buffer = io.BytesIO()
                page.save(img_buffer, format="PNG")
                img_data = img_buffer.getvalue()
                img_base64 = base64.b64encode(img_data).decode()
                images.append(img_base64)

        except ImportError:
            logger.warning("pdf2image not available for PDF image extraction")
    except Exception as e:
        logger.error(f"PDF image extraction error: {e}")

    return images


def extract_images_from_docx_bytes(file_content: bytes) -> List[str]:
    """Extract images from DOCX bytes."""
    import base64
    import tempfile
    import logging

    logger = logging.getLogger(__name__)
    images = []

    try:
        from docx import Document as DocxDocument
        import io

        # Create document from bytes
        doc = DocxDocument(io.BytesIO(file_content))

        # Extract embedded images from document relationships
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                try:
                    img_data = rel.target_part.blob
                    img_base64 = base64.b64encode(img_data).decode()
                    images.append(img_base64)
                except:
                    continue

    except Exception as e:
        logger.error(f"DOCX image extraction error: {e}")

    return images


def create_fallback_document_for_vision(
    images: List[str], source_filename: str
) -> Document:
    """
    Create a fallback document when no text is extractable but images are available.
    This ensures vector search doesn't fail when documents contain only images.

    Args:
        images: List of base64 encoded images
        source_filename: Name of the source file

    Returns:
        A Document with minimal text content for vector processing
    """
    fallback_content = f"This document '{source_filename}' contains {len(images)} image(s) with visual content that can be analyzed using vision-enabled models."

    return Document(
        page_content=fallback_content,
        metadata={
            "source_filename": source_filename,
            "is_vision_fallback": True,
            "image_count": len(images),
            "content_type": "images_only",
        },
    )


def ensure_documents_for_vector_search(
    documents: List[Document],
    images: List[str] = None,
    source_filename: str = "document",
) -> List[Document]:
    """
    Ensure there are documents available for vector search, creating fallback documents if needed.
    This prevents vector search failures when documents contain only images or no extractable content.

    Args:
        documents: List of extracted documents (may be empty)
        images: Optional list of base64 encoded images
        source_filename: Name of the source file

    Returns:
        List of documents guaranteed to have at least one document for vector search
    """
    # Filter out empty documents
    valid_documents = [doc for doc in documents if doc.page_content.strip()]

    # If we have valid text documents, return them
    if valid_documents:
        return valid_documents

    # If no text documents but we have images, create fallback for vision processing
    if images and len(images) > 0:
        fallback_doc = create_fallback_document_for_vision(images, source_filename)
        return [fallback_doc]

    # Last resort: create a minimal document to prevent vector search failure
    fallback_content = f"This document '{source_filename}' appears to be empty or contains no extractable content."
    fallback_doc = Document(
        page_content=fallback_content,
        metadata={
            "source_filename": source_filename,
            "is_empty_fallback": True,
            "content_type": "empty",
        },
    )

    return [fallback_doc]


async def extract_text_with_vision_enhancement(
    file_content: bytes, filename: str, llm, purpose: str = "analysis"
) -> str:
    """
    Enhanced document processing that combines text extraction with visual processing.
    Used for suggestion endpoints (generate questions, outline, form fields, etc.)

    Args:
        file_content: Raw bytes of the document
        filename: Original filename
        llm: Language model instance
        purpose: Purpose of extraction (e.g., "checklist generation", "outline creation")

    Returns:
        Combined text content from both text extraction and vision analysis
    """
    from app.services.vision_service import VisionService

    # Check file extension
    file_ext = Path(filename).suffix.lower() if filename else ""

    # Always try text extraction first
    print(f"📄 Extracting text from {filename} for {purpose}")
    text_content = extract_text_from_file_unified(file_content, filename)

    # Check if vision processing should be attempted
    vision_enabled = VisionService.is_vision_enabled(llm)

    if not vision_enabled:
        print(f"ℹ️ Vision not enabled, using text-only extraction for {filename}")
        return text_content

    # Try vision enhancement for PDFs and DOCX files (both can contain images)
    if file_ext not in [".pdf", ".docx"]:
        print(
            f"ℹ️ File {filename} format doesn't support embedded images, skipping vision enhancement"
        )
        return text_content

    # Try to extract images from PDF or DOCX
    try:
        print(f"🖼️ Attempting to extract images from {file_ext.upper()}: {filename}")
        _, document_images = extract_documents_and_images_from_file_unified(
            file_content, filename
        )

        if not document_images:
            print(f"ℹ️ No images found in {filename}, using text-only content")
            return text_content

        print(
            f"✅ Found {len(document_images)} images in {filename}, performing vision analysis"
        )

        # Convert images for vision analysis
        vision_images = []
        for i, img_b64 in enumerate(document_images):
            vision_images.append(
                {
                    "image_data": img_b64,
                    "metadata": {"source": filename, "page": i + 1},
                }
            )

        # Create purpose-specific vision prompt
        vision_prompt = f"""Analyze the visual content in these document images to extract information relevant for {purpose}.

Document: {filename}
Images: {len(document_images)} pages

Please extract any visual information that would be helpful for {purpose}, including:
1. Charts, graphs, diagrams, and visual data
2. Form fields, tables, and structured layouts  
3. Images, photos, and visual elements
4. Text that may not have been captured in standard text extraction
5. Visual indicators, symbols, and formatting

Provide a detailed description of the visual content that would be useful for {purpose}:"""

        # Perform vision analysis
        vision_result = VisionService.safe_vision_analysis(
            llm=llm,
            prompt_template=vision_prompt,
            variables={},
            images=vision_images,
        )

        if (
            vision_result
            and isinstance(vision_result, str)
            and len(vision_result.strip()) > 50
        ):
            # Combine text and vision results
            combined_content = text_content
            if combined_content.strip():
                combined_content += (
                    f"\n\n--- VISUAL ANALYSIS OF {filename.upper()} ---\n"
                )
            else:
                combined_content = f"--- VISUAL ANALYSIS OF {filename.upper()} ---\n"
            combined_content += vision_result.strip()

            print(
                f"✅ Successfully enhanced {filename} with vision analysis (+{len(vision_result)} chars)"
            )
            return combined_content
        else:
            print(
                f"⚠️ Vision analysis of {filename} produced minimal content, using text only"
            )
            return text_content

    except Exception as e:
        print(f"⚠️ Vision enhancement failed for {filename}: {str(e)}")
        return text_content


def extract_documents_with_table_processing(
    file_content: bytes, filename: str, llm=None
) -> Tuple[List[Document], Dict[str, Any]]:
    """
    Enhanced document extraction that processes tables with vision when detected.

    Args:
        file_content: Raw bytes of the file
        filename: Name of the file
        llm: LLM instance for vision processing (optional)

    Returns:
        Tuple of (processed_documents, table_data)
    """
    from app.services.table_detection import TableDetector
    from app.services.vision_service import VisionService

    print(f"🔍 Processing {filename} with table-aware document extraction")

    # First, extract documents normally
    documents = extract_documents_from_file_unified(file_content, filename)
    logger.info(f"📄 Extracted {len(documents)} documents from {filename}")

    # Detect which pages have tables
    table_pages = TableDetector.identify_table_pages(documents)

    table_data = {}
    processed_documents = []
    file_ext = Path(filename).suffix.lower() if filename else ""

    # Enhanced diagnostic logging for table processing conditions
    logger.info(f"🔍 TABLE PROCESSING DIAGNOSTIC:")
    logger.info(f"  📊 Table pages detected: {len(table_pages)} pages {table_pages}")

    # For table processing, we need PAGE IMAGES, not embedded images
    page_images = []
    if table_pages and file_ext == ".pdf":
        logger.info(f"  🖼️ Generating page images for PDF table processing...")

        # Try PyMuPDF first (already installed in your system)
        try:
            import fitz  # PyMuPDF
            import base64  # Add missing import

            doc = fitz.open(stream=file_content, filetype="pdf")

            for page_num in range(doc.page_count):
                page = doc[page_num]
                # Render page as image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img_base64 = base64.b64encode(img_data).decode()
                page_images.append(img_base64)

            doc.close()
            logger.info(f"  ✅ Generated {len(page_images)} page images using PyMuPDF")

        except ImportError:
            logger.warning(f"  ⚠️ PyMuPDF not available, trying pdf2image...")
            # Fallback to pdf2image
            try:
                from pdf2image import convert_from_bytes
                import io
                import base64

                pages = convert_from_bytes(file_content, dpi=150, fmt="PNG")
                for page in pages:
                    img_buffer = io.BytesIO()
                    page.save(img_buffer, format="PNG")
                    img_str = base64.b64encode(img_buffer.getvalue()).decode()
                    page_images.append(img_str)
                logger.info(
                    f"  ✅ Generated {len(page_images)} page images using pdf2image"
                )
            except ImportError:
                logger.error(
                    f"  ❌ Neither PyMuPDF nor pdf2image available - cannot generate page images"
                )
            except Exception as e:
                logger.error(f"  ❌ Error with pdf2image: {e}")

        except Exception as e:
            logger.error(f"  ❌ Error with PyMuPDF: {e}")

    logger.info(f"  🖼️ Page images available: {len(page_images)} images")

    # Check vision capability
    vision_enabled = VisionService.is_vision_enabled(llm)
    logger.info(f"  🔮 Vision enabled: {vision_enabled}")

    # Enhanced LLM debugging
    if llm:
        model_name = (
            getattr(llm, "model_name", "")
            or getattr(llm, "model", "")
            or str(type(llm).__name__)
        )
        class_name = type(llm).__name__
        logger.info(f"  🤖 LLM model: '{model_name}', type: {class_name}")

        # Check for wrapped models
        if hasattr(llm, "_llm"):
            inner_llm = getattr(llm, "_llm", None)
            if inner_llm:
                inner_model = getattr(inner_llm, "model_name", "") or getattr(
                    inner_llm, "model", ""
                )
                inner_class = type(inner_llm).__name__
                logger.info(f"  🤖 Inner LLM: '{inner_model}', type: {inner_class}")

        # Debug vision-enabled models list
        from app.core.config import settings

        logger.info(
            f"  🔮 Vision-enabled models in config: {settings.VISION_ENABLED_MODELS}"
        )

        # Check if model matches any vision-enabled model
        matches = [
            vm for vm in settings.VISION_ENABLED_MODELS if vm in model_name.lower()
        ]
        if matches:
            logger.info(f"  ✅ Model matches vision patterns: {matches}")
        else:
            logger.warning(
                f"  ❌ Model '{model_name}' doesn't match any vision-enabled patterns"
            )
            logger.warning(
                f"  💡 Add '{model_name.lower()}' to VISION_ENABLED_MODELS if it supports vision"
            )

        # If vision is not enabled, explain why
        if not vision_enabled:
            logger.warning(f"  ❌ VISION DISABLED for model '{model_name}'")
            logger.warning(
                f"  💡 Ensure model name contains one of: {settings.VISION_ENABLED_MODELS}"
            )
        else:
            logger.info(f"  ✅ VISION ENABLED for model '{model_name}'")
    else:
        logger.warning(f"  ❌ No LLM provided for vision processing")
        logger.warning(f"  💡 LLM parameter is None - check chatbot LLM initialization")

    # Check each condition separately
    if not table_pages:
        logger.info(f"❌ CONDITION 1 FAILED: No table pages detected")
    else:
        logger.info(f"✅ CONDITION 1 PASSED: {len(table_pages)} table pages detected")

    if not page_images:
        logger.info(
            f"❌ CONDITION 2 FAILED: No page images generated for table processing"
        )
    else:
        logger.info(
            f"✅ CONDITION 2 PASSED: {len(page_images)} page images available for table processing"
        )

    if not vision_enabled:
        logger.info(
            f"❌ CONDITION 3 FAILED: Vision processing not enabled for this LLM"
        )
    else:
        logger.info(f"✅ CONDITION 3 PASSED: Vision processing enabled")

    # Try vision processing if all conditions are met
    vision_processing_attempted = False

    if table_pages and page_images and VisionService.is_vision_enabled(llm):
        logger.info(f"🔍 Detected tables on pages: {table_pages}")

        # Check if we should use vision for these tables
        should_use_vision = TableDetector.should_use_vision_for_tables(
            documents, file_ext
        )

        if should_use_vision:
            vision_processing_attempted = True
            logger.info(
                f"📊 Tables are complex enough to benefit from vision processing"
            )

            # Extract table page images for vision processing
            table_images = []
            table_page_numbers = []

            for page_num in table_pages:
                # Use 0-based indexing for page_images array
                page_index = page_num - 1 if page_num > 0 else page_num
                if page_index < len(page_images):
                    table_images.append(page_images[page_index])
                    table_page_numbers.append(page_num)

            # Process tables with vision
            if table_images:
                logger.info(
                    f"� VISION PROCESSING INVOKED: Processing {len(table_images)} table pages with vision model"
                )
                logger.debug(
                    f"Vision processing details: pages={table_page_numbers}, model={getattr(llm, 'model_name', 'unknown')}"
                )
                try:
                    table_data = VisionService.extract_table_as_json(
                        llm=llm,
                        page_images=table_images,
                        page_numbers=table_page_numbers,
                        filename=filename,
                    )
                    if table_data.get("extraction_successful", False):
                        logger.info(
                            f"✅ Vision processing complete: extracted data for {len(table_data.get('tables', []))} tables"
                        )
                    else:
                        error_msg = table_data.get("error", "Unknown error")
                        logger.warning(f"⚠️ Vision processing failed: {error_msg}")
                except Exception as vision_error:
                    logger.error(
                        f"💥 Vision processing error: {type(vision_error).__name__}: {vision_error}"
                    )
                    # Create empty table_data to trigger fallback processing
                    table_data = {}
            else:
                logger.warning(
                    f"⚠️ No valid table images found despite detecting table pages"
                )
        else:
            logger.info(
                f"📄 Tables are simple, using text-only processing (vision not needed)"
            )
    else:
        # Log which specific condition failed
        failed_conditions = []
        if not table_pages:
            failed_conditions.append("no table pages")
        if not page_images:
            failed_conditions.append("no page images generated")
        if not VisionService.is_vision_enabled(llm):
            failed_conditions.append("vision not enabled")

        logger.info(f"❌ TABLE ENHANCEMENT SKIPPED: {', '.join(failed_conditions)}")

        # Even without vision, mark table pages for enhanced text processing
        if table_pages:
            logger.info(
                f"📄 Using enhanced text-based table processing for {len(table_pages)} table pages"
            )

    # Process documents and enhance table-containing ones
    for i, doc in enumerate(documents):
        page_num = doc.metadata.get("page", doc.metadata.get("page_number", i))

        if page_num in table_pages:
            # Check if we have vision-extracted tables for this page
            vision_tables = []
            if table_data.get("tables"):
                vision_tables = [
                    table
                    for table in table_data["tables"]
                    if table.get("page") == page_num
                ]

            if vision_tables:
                # Replace raw table content with clean JSON formatted data
                logger.info(
                    f"📊 Processing page {page_num} with {len(vision_tables)} vision-extracted tables"
                )

                # For pages with tables, replace the raw content entirely with clean JSON
                # This prevents duplicate/conflicting information in citations
                all_table_content = []

                # Process each vision-extracted table
                for table in vision_tables:
                    import json

                    # Create structured JSON representation for table data
                    table_json = {
                        "table_id": table.get(
                            "table_id", f"table_{page_num}_{vision_tables.index(table)}"
                        ),
                        "page": page_num,
                        "title": table.get("title", table.get("summary", "Data Table")),
                        "headers": table.get("headers", []),
                        "rows": table.get("rows", []),
                        "summary": table.get("summary", ""),
                        "context": table.get("context", ""),
                        "metadata": {
                            "row_count": table.get("metadata", {}).get(
                                "row_count", len(table.get("rows", []))
                            ),
                            "column_count": table.get("metadata", {}).get(
                                "column_count", len(table.get("headers", []))
                            ),
                            "table_type": table.get("metadata", {}).get(
                                "table_type", "data"
                            ),
                            "processing_method": "vision_enhanced",
                            "source_filename": filename,
                            "extraction_timestamp": table.get("metadata", {}).get(
                                "extraction_timestamp", ""
                            ),
                        },
                    }

                    # Convert table data to JSON array format for better LLM interpretation
                    json_rows = []

                    # Get headers and validate we have data
                    headers = table_json.get("headers", [])
                    rows = table_json.get("rows", [])

                    if headers and rows:
                        # Convert each row to a JSON object using headers as keys
                        for row in rows:
                            if isinstance(row, list) and len(row) > 0:
                                # Create object with header-value pairs
                                row_obj = {}
                                for i, header in enumerate(headers):
                                    # Get value at index i, or empty string if index doesn't exist
                                    value = row[i] if i < len(row) else ""
                                    # Clean up the value
                                    if value is None:
                                        value = ""
                                    else:
                                        value = str(value).strip()
                                    row_obj[header] = value
                                json_rows.append(row_obj)

                    # Create clean JSON table representation WITHOUT wrapper markers
                    # This makes it more LLM-friendly and eliminates parsing issues
                    table_content = {
                        "table_metadata": {
                            "title": table_json.get("title", "Data Table"),
                            "page": page_num,
                            "summary": table_json.get("summary", ""),
                            "context": table_json.get("context", ""),
                            "dimensions": f"{len(json_rows)} rows × {len(headers)} columns",
                        },
                        "table_data": json_rows,
                    }

                    all_table_content.append(table_content)

                # Create enhanced content with proper wrapper markers for chunking system
                # Each table gets its own JSON block with proper markers
                enhanced_content_parts = []

                for table_content in all_table_content:
                    table_block = f"\n=== TABLE DATA (JSON) ===\n"

                    # Add metadata header
                    metadata_header = {
                        "_table_metadata": table_content["table_metadata"]
                    }
                    table_block += (
                        json.dumps(metadata_header, indent=2, ensure_ascii=False)
                        + "\n\n"
                    )

                    # Add table data as JSON array
                    table_block += json.dumps(
                        table_content["table_data"], indent=2, ensure_ascii=False
                    )
                    table_block += "\n=== END TABLE DATA ===\n"

                    enhanced_content_parts.append(table_block)

                # Combine all table blocks
                enhanced_content = "\n".join(enhanced_content_parts)

                # Create new document with enhanced content for vision processing
                enhanced_doc = Document(
                    page_content=enhanced_content,
                    metadata={
                        **doc.metadata,
                        "has_processed_tables": True,
                        "table_count": len(vision_tables),
                        "processing_method": "vision_enhanced",
                    },
                )
                processed_documents.append(enhanced_doc)

            else:
                # Vision processing failed or returned no tables for this page
                # Create a fallback structured representation from the raw content
                enhanced_content = doc.page_content

                logger.warning(
                    f"⚠️ Page {page_num} detected as table page but no vision data available. Creating fallback structure."
                )

                # Create a fallback table structure from raw content
                import json

                fallback_table = {
                    "table_id": f"fallback_table_{page_num}",
                    "page": page_num,
                    "title": f"Table Content from Page {page_num}",
                    "headers": [],  # We don't have structured headers
                    "rows": [],  # We don't have structured rows
                    "raw_content": doc.page_content.strip(),  # Include the raw content
                    "summary": "Table content extracted as raw text (vision processing unavailable)",
                    "context": f"Content from page {page_num} of {filename}",
                    "metadata": {
                        "row_count": 0,
                        "column_count": 0,
                        "table_type": "raw_text_fallback",
                        "processing_method": "text_only_fallback",
                        "source_filename": filename,
                        "extraction_timestamp": "",
                    },
                }

                # Format as JSON array for consistency (even for fallback)
                # Create a single JSON object representing the raw text content
                fallback_json_rows = [
                    {
                        "content_type": "raw_text",
                        "page_content": doc.page_content.strip(),
                        "processing_note": "Vision processing was unavailable - content preserved as raw text",
                    }
                ]

                table_text = f"\n\n=== TABLE DATA (JSON) ===\n"

                # Add metadata header for fallback context
                metadata_header = {
                    "_table_metadata": {
                        "title": f"Table Content from Page {page_num}",
                        "page": page_num,
                        "summary": "Table content extracted as raw text (vision processing unavailable)",
                        "context": f"Content from page {page_num} of {filename}",
                        "dimensions": "1 content block (fallback mode)",
                        "processing_method": "text_only_fallback",
                    }
                }

                table_text += (
                    json.dumps(metadata_header, indent=2, ensure_ascii=False) + "\n\n"
                )
                table_text += json.dumps(
                    fallback_json_rows, indent=2, ensure_ascii=False
                )
                table_text += "\n=== END TABLE DATA ===\n"

                enhanced_content += table_text

                # Create new document with enhanced content (fallback mode)
                enhanced_doc = Document(
                    page_content=enhanced_content,
                    metadata={
                        **doc.metadata,
                        "has_processed_tables": True,
                        "table_count": 1,  # One fallback table
                        "processing_method": "text_only_fallback",
                    },
                )
                processed_documents.append(enhanced_doc)
        else:
            # No tables detected on this page
            processed_documents.append(doc)

    # Log processing results
    if table_data.get("tables"):
        print(
            f"✅ Enhanced {len(processed_documents)} documents with {len(table_data['tables'])} extracted tables"
        )
    else:
        print(
            f"📄 Processed {len(processed_documents)} documents (no table enhancement)"
        )

    return processed_documents, table_data


def search_in_table_data(
    field_name: str, field_description: str, table_data: Dict[str, Any]
) -> Optional[str]:
    """
    Search for field values in extracted table data.

    Args:
        field_name: The field name to search for
        field_description: Description of the field for better matching
        table_data: Dictionary containing extracted table data

    Returns:
        Found value or None
    """
    from typing import Optional

    if not table_data.get("tables"):
        return None

    # Normalize search terms
    field_lower = field_name.lower().strip()
    desc_lower = field_description.lower().strip()

    # Extract key terms from field name and description
    field_terms = set(field_lower.split())
    desc_terms = set(desc_lower.split())
    search_terms = field_terms.union(desc_terms)

    # Remove common stop words
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "is",
        "are",
        "was",
        "were",
    }
    search_terms = search_terms - stop_words

    # Search through all tables
    for table in table_data["tables"]:
        headers = table.get("headers", [])
        rows = table.get("rows", [])

        if not headers or not rows:
            continue

        # Search in headers for field name matches
        for header_idx, header in enumerate(headers):
            header_lower = header.lower().strip()

            # Direct match
            if field_lower in header_lower or header_lower in field_lower:
                column_values = extract_column_values(rows, header_idx)
                if column_values:
                    return format_column_values(column_values)

            # Term-based matching
            header_terms = set(header_lower.split())
            if search_terms.intersection(header_terms):
                # Calculate match score
                match_score = len(search_terms.intersection(header_terms)) / len(
                    search_terms
                )
                if match_score >= 0.5:  # At least 50% of search terms match
                    column_values = extract_column_values(rows, header_idx)
                    if column_values:
                        return format_column_values(column_values)

        # Search in table title/summary
        title = table.get("title", "").lower()
        summary = table.get("summary", "").lower()
        context = table.get("context", "").lower()

        table_text = f"{title} {summary} {context}"
        if any(term in table_text for term in search_terms):
            # If field name relates to table content, return a summary
            return f"Found in {table.get('title', 'table')}: {table.get('summary', 'Contains relevant data')}"

    return None


def extract_column_values(rows: List[List], column_index: int) -> List[str]:
    """Extract non-empty values from a specific column."""
    column_values = []
    for row in rows:
        if isinstance(row, list) and column_index < len(row):
            value = str(row[column_index]).strip()
            if value and value.lower() not in ["", "null", "none", "n/a", "-", "--"]:
                column_values.append(value)
    return column_values


def format_column_values(values: List[str]) -> str:
    """Format column values for display."""
    if not values:
        return None

    # Remove duplicates while preserving order
    seen = set()
    unique_values = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique_values.append(value)

    if len(unique_values) == 1:
        return unique_values[0]
    elif len(unique_values) <= 3:
        return ", ".join(unique_values)
    else:
        # Return first 3 values and indicate more
        return f"{', '.join(unique_values[:3])} (and {len(unique_values) - 3} more)"


async def extract_documents_with_table_processing_async(
    file_content: bytes, filename: str, llm=None
) -> Tuple[List[Document], Dict[str, Any]]:
    """
    Async version of table-aware document extraction.

    Args:
        file_content: Raw bytes of the file
        filename: Name of the file
        llm: LLM instance for vision processing (optional)

    Returns:
        Tuple of (processed_documents, table_data)
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    # Use thread pool for CPU-intensive document processing
    with ThreadPoolExecutor() as executor:
        future = executor.submit(
            extract_documents_with_table_processing, file_content, filename, llm
        )
        return await asyncio.wrap_future(future)
