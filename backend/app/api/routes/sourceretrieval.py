import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlmodel import Session, select
from app.api.deps import CurrentUser, SessionDep
from app.models import Source, SourceData, KnowledgeBase, SourceContentResponse
import zipfile
from io import BytesIO
import base64
import mimetypes
import tempfile
import os
import mammoth
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from bs4 import BeautifulSoup
import re

# RTF processing
try:
    from striprtf.striprtf import rtf_to_text

    RTF_PROCESSING_AVAILABLE = True
except ImportError:
    print("Warning: striprtf not available, using basic RTF conversion")
    RTF_PROCESSING_AVAILABLE = False

    def rtf_to_text(rtf_content: str) -> str:
        """
        Enhanced RTF to text conversion - properly extracts clean text from RTF.
        This is a more robust fallback when striprtf is not available.
        """
        import re

        if not rtf_content.strip():
            return ""

        # Ensure we have RTF content
        if not rtf_content.startswith("{\\rtf"):
            # If it's not RTF format, return as-is
            return rtf_content

        text = rtf_content

        # Remove RTF header info
        text = re.sub(r"{\\rtf\d+[^}]*}", "", text)

        # Remove font table (more comprehensive)
        text = re.sub(r"{\\fonttbl[^{}]*(?:{[^{}]*}[^{}]*)*}", "", text)

        # Remove color table
        text = re.sub(r"{\\colortbl[^}]*}", "", text)

        # Remove style definitions
        text = re.sub(r"{\\stylesheet[^{}]*(?:{[^{}]*}[^{}]*)*}", "", text)

        # Remove info group
        text = re.sub(r"{\\info[^{}]*(?:{[^{}]*}[^{}]*)*}", "", text)

        # Remove document formatting information
        text = re.sub(r"\\viewkind\d+", "", text)
        text = re.sub(r"\\uc\d+", "", text)
        text = re.sub(r"\\deff\d+", "", text)
        text = re.sub(r"\\deflang\d+", "", text)
        text = re.sub(r"\\deflangfe\d+", "", text)

        # Remove positioning and spacing controls that create artifacts
        text = re.sub(r"\\tx\d+", "", text)  # Tab positions
        text = re.sub(r"\\li\d+", "", text)  # Left indent
        text = re.sub(r"\\ri\d+", "", text)  # Right indent
        text = re.sub(r"\\fi\d+", "", text)  # First line indent
        text = re.sub(r"\\sb\d+", "", text)  # Space before
        text = re.sub(r"\\sa\d+", "", text)  # Space after
        text = re.sub(r"\\sl\d+", "", text)  # Line spacing
        text = re.sub(r"\\slmult\d+", "", text)  # Line spacing multiple

        # Handle paragraph and line control words
        text = re.sub(r"\\par\b", "\n", text)  # Paragraph breaks
        text = re.sub(r"\\line\b", "\n", text)  # Line breaks
        text = re.sub(r"\\tab\b", "\t", text)  # Tabs
        text = re.sub(r"\\cell\b", "\t", text)  # Table cells
        text = re.sub(r"\\row\b", "\n", text)  # Table rows

        # Handle special characters properly
        text = re.sub(r"\\bullet\b", "•", text)  # Bullet points
        text = re.sub(r"\\endash\b", "–", text)  # En dash
        text = re.sub(r"\\emdash\b", "—", text)  # Em dash
        text = re.sub(
            r"\\ldblquote\b",
            """, text)  # Left double quote
        text = re.sub(r"\\rdblquote\b", """,
            text,
        )  # Right double quote
        text = re.sub(r"\\lquote\b", "'", text)  # Left single quote
        text = re.sub(r"\\rquote\b", "'", text)  # Right single quote

        # Handle bullet points that appear as negative numbers
        text = re.sub(r"-720\s*", "• ", text)  # Common RTF bullet point indicator

        # Remove font formatting control words
        text = re.sub(r"\\[bi]\d*\b", "", text)  # Bold, italic
        text = re.sub(r"\\ul\d*\b", "", text)  # Underline
        text = re.sub(r"\\strike\d*\b", "", text)  # Strikethrough
        text = re.sub(r"\\fs\d+\b", "", text)  # Font size
        text = re.sub(r"\\f\d+\b", "", text)  # Font family
        text = re.sub(r"\\cf\d+\b", "", text)  # Color
        text = re.sub(r"\\highlight\d+\b", "", text)  # Highlight

        # Remove groups that we don't need (like {\*\generator...})
        text = re.sub(r"{\\\*[^}]*}", "", text)

        # Remove remaining braces
        text = re.sub(r"[{}]", "", text)

        # Handle escaped characters
        text = text.replace("\\\\", "\\")  # Escaped backslash
        text = re.sub(r"\\{", "{", text)  # Escaped left brace
        text = re.sub(r"\\}", "}", text)  # Escaped right brace
        text = re.sub(r"\\-", "-", text)  # Optional hyphen
        text = re.sub(r"\\_", " ", text)  # Non-breaking space
        text = re.sub(r"\\~", " ", text)  # Non-breaking space

        # Remove any remaining control words and their numeric parameters
        text = re.sub(
            r"\\[a-z]+\d*\s*", " ", text
        )  # Control words with optional numbers
        text = re.sub(r"\\[^a-zA-Z\s]", "", text)  # Backslash + non-letter

        # Remove standalone numbers that are formatting artifacts
        text = re.sub(
            r"\b\d+\s*;\s*;\s*-?\d+\s*;\s*", "", text
        )  # Pattern like "01 ; ; -360 ;"
        text = re.sub(
            r"\b\d{4,}\b", "", text
        )  # Remove long number sequences (4+ digits)
        text = re.sub(
            r"\b-\d{3,}\b", "", text
        )  # Remove negative numbers with 3+ digits

        # Clean up whitespace and formatting
        text = re.sub(r"\n\s*\n", "\n\n", text)  # Multiple newlines to double newline
        text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces/tabs to single space
        text = re.sub(r" *\n *", "\n", text)  # Remove spaces around newlines
        text = re.sub(r"^\s+", "", text)  # Remove leading whitespace
        text = text.strip()

        return text


router = APIRouter(prefix="/files", tags=["files"])


def html_to_pdf_with_reportlab(html_content: str, output_path: str) -> None:
    """
    Convert HTML content to PDF using ReportLab.
    This is a simple implementation that handles basic HTML tags.
    """
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Define custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceAfter=8,
        spaceBefore=8,
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=6,
        leading=14,
    )

    # Process HTML elements
    for element in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "br"]
    ):
        if element.name in ["h1", "h2", "h3"]:
            text = element.get_text().strip()
            if text:
                if element.name == "h1":
                    story.append(Paragraph(text, title_style))
                else:
                    story.append(Paragraph(text, heading_style))
                story.append(Spacer(1, 6))
        elif element.name in ["p", "div"]:
            text = element.get_text().strip()
            if text:
                # Clean up text - remove extra whitespace
                text = re.sub(r"\s+", " ", text)
                story.append(Paragraph(text, normal_style))
                story.append(Spacer(1, 6))
        elif element.name == "br":
            story.append(Spacer(1, 12))

    # If no content was found, add the raw text
    if not story:
        text = soup.get_text().strip()
        if text:
            # Split into paragraphs and add each one
            paragraphs = text.split("\n\n")
            for para in paragraphs:
                para = para.strip()
                if para:
                    # Clean up text
                    para = re.sub(r"\s+", " ", para)
                    story.append(Paragraph(para, normal_style))
                    story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)


def text_to_pdf_with_reportlab(
    text_content: str, output_path: str, title: str = "Document"
) -> None:
    """
    Convert plain text content to PDF using ReportLab.
    This is used for RTF and other text-based formats.
    """
    # Create PDF document
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Define custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12,
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=6,
        spaceBefore=6,
    )

    # Add title
    if title and title != "Document":
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))

    # Split text into paragraphs and add to story
    paragraphs = text_content.split("\n")

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if paragraph:  # Skip empty paragraphs
            # Escape HTML characters for ReportLab
            paragraph = paragraph.replace("&", "&amp;")
            paragraph = paragraph.replace("<", "&lt;")
            paragraph = paragraph.replace(">", "&gt;")

            story.append(Paragraph(paragraph, normal_style))
        else:
            story.append(Spacer(1, 6))

    # Build the PDF
    doc.build(story)


@router.get("/source/{source_id}", response_model=SourceContentResponse)
async def get_source_content(
    source_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> SourceContentResponse:
    """
    Retrieve a source file by ID.
    Available to all authenticated users in shared deployment.
    """
    try:
        # Find the source data
        source_data = session.get(SourceData, source_id)

        if not source_data:
            raise HTTPException(status_code=404, detail="Source file not found")

        # Simply verify that the source exists in the database
        source = session.exec(
            select(Source).where(Source.source_data_id == source_id)
        ).first()

        if not source:
            raise HTTPException(status_code=404, detail="Source reference not found")

        # Get source name from the associated Source (just for display)
        file_name = source.name if source else f"file-{source_id}.txt"

        # Try to extract file content - handle both ZIP and non-ZIP formats
        try:
            # First, try ZIP format (most files are stored this way)
            zip_data = BytesIO(source_data.data)
            with zipfile.ZipFile(zip_data, "r") as zip_file:
                # Get the first file in the archive
                file_info = zip_file.infolist()[0]
                file_content = zip_file.read(file_info.filename)
        except zipfile.BadZipFile:
            # If not a ZIP file, assume it's stored as raw data (e.g., .txt files)
            print(f"File {file_name} is not in ZIP format, using raw data")
            file_content = source_data.data

        # Determine content type
        content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"

        # Base64 encode for transmission
        content_base64 = base64.b64encode(file_content).decode("utf-8")

        return {
            "id": str(source_id),
            "name": file_name,
            "data_base64": content_base64,
            "content_type": content_type,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")


@router.get("/source/{source_id}/pdf")
async def convert_docx_to_pdf(
    source_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    """
    Convert a DOCX source file to PDF on-demand.
    Only works with DOCX files that the user has access to.
    """
    try:
        # Find the source data
        source_data = session.get(SourceData, source_id)

        if not source_data:
            raise HTTPException(status_code=404, detail="Source file not found")

        # Check if current user has access to this file (same logic as get_source_content)
        source = session.exec(
            select(Source)
            .where(Source.source_data_id == source_id)
            .where(Source.owner_id == current_user.id)
        ).first()

        if not source and not current_user.is_superuser:
            kb_access = session.exec(
                select(KnowledgeBase)
                .join(Source, KnowledgeBase.id == Source.knowledge_base_id)
                .where(Source.source_data_id == source_id)
                .where(KnowledgeBase.owner_id == current_user.id)
            ).first()

            if not kb_access:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to access this file",
                )

        # Get source name for validation
        file_source = session.exec(
            select(Source).where(Source.source_data_id == source_id)
        ).first()
        file_name = file_source.name if file_source else f"file-{source_id}.txt"

        # Check if it's a DOCX file
        if not file_name.lower().endswith(".docx"):
            raise HTTPException(status_code=400, detail="File is not a DOCX document")

        # DOCX files are already ZIP files internally, so we don't need to extract from another ZIP
        # Write the source data directly to a temporary DOCX file
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_docx:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                try:
                    # Write the source data directly as DOCX content
                    temp_docx.write(source_data.data)
                    temp_docx.flush()

                    print(f"Converting DOCX to PDF: {file_name}")

                    # Convert DOCX to HTML using mammoth
                    with open(temp_docx.name, "rb") as docx_file:
                        result = mammoth.convert_to_html(docx_file)
                        html_content = result.value

                    print(f"Converting HTML to PDF for: {file_name}")

                    # Convert HTML to PDF using ReportLab
                    html_to_pdf_with_reportlab(html_content, temp_pdf.name)

                    # Read the generated PDF
                    with open(temp_pdf.name, "rb") as pdf_file:
                        pdf_content = pdf_file.read()

                    # Generate PDF filename
                    pdf_filename = f"{os.path.splitext(file_name)[0]}.pdf"

                    print(
                        f"Successfully converted {file_name} to PDF ({len(pdf_content)} bytes)"
                    )

                    # Return the PDF
                    return Response(
                        content=pdf_content,
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": f'inline; filename="{pdf_filename}"'
                        },
                    )

                finally:
                    # Clean up temp files
                    try:
                        os.unlink(temp_docx.name)
                        os.unlink(temp_pdf.name)
                    except Exception as cleanup_error:
                        print(
                            f"Warning: Failed to clean up temp files: {cleanup_error}"
                        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")


@router.get("/source/by-filename/{filename}/pdf")
async def convert_docx_to_pdf_by_filename(
    filename: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    """
    Convert a DOCX source file to PDF on-demand using filename.
    Only works with DOCX files that the user has access to.
    """
    try:
        # Find the source by filename that the user has access to
        source = session.exec(
            select(Source)
            .where(Source.name == filename)
            .where(Source.owner_id == current_user.id)
        ).first()

        if not source and not current_user.is_superuser:
            # Check if they have access through knowledge base
            source = session.exec(
                select(Source)
                .join(KnowledgeBase, KnowledgeBase.id == Source.knowledge_base_id)
                .where(Source.name == filename)
                .where(KnowledgeBase.owner_id == current_user.id)
            ).first()

        if not source:
            raise HTTPException(
                status_code=404, detail="Source file not found or access denied"
            )

        # Check if it's a DOCX file
        if not filename.lower().endswith(".docx"):
            raise HTTPException(status_code=400, detail="File is not a DOCX document")

        # Get the source data
        source_data = session.get(SourceData, source.source_data_id)
        if not source_data:
            raise HTTPException(status_code=404, detail="Source data not found")

        # DOCX files are already ZIP files internally, so we don't need to extract from another ZIP
        # Write the source data directly to a temporary DOCX file
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_docx:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                try:
                    # Write the source data directly as DOCX content
                    temp_docx.write(source_data.data)
                    temp_docx.flush()

                    print(f"Converting DOCX to PDF by filename: {filename}")

                    # Convert DOCX to HTML using mammoth
                    with open(temp_docx.name, "rb") as docx_file:
                        result = mammoth.convert_to_html(docx_file)
                        html_content = result.value

                    print(f"Converting HTML to PDF for filename: {filename}")

                    # Convert HTML to PDF using ReportLab
                    html_to_pdf_with_reportlab(html_content, temp_pdf.name)

                    # Read the generated PDF
                    with open(temp_pdf.name, "rb") as pdf_file:
                        pdf_content = pdf_file.read()

                    # Generate PDF filename
                    pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"

                    print(
                        f"Successfully converted {filename} to PDF ({len(pdf_content)} bytes)"
                    )

                    # Return the PDF
                    return Response(
                        content=pdf_content,
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": f'inline; filename="{pdf_filename}"'
                        },
                    )

                finally:
                    # Clean up temp files
                    try:
                        os.unlink(temp_docx.name)
                        os.unlink(temp_pdf.name)
                    except Exception as cleanup_error:
                        print(
                            f"Warning: Failed to clean up temp files: {cleanup_error}"
                        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")


@router.get("/source/{source_id}/rtf-pdf")
async def convert_rtf_to_pdf(
    source_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    """
    Convert an RTF source file to PDF on-demand.
    Only works with RTF files that the user has access to.
    """
    try:
        # Find the source data
        source_data = session.get(SourceData, source_id)

        if not source_data:
            raise HTTPException(status_code=404, detail="Source file not found")

        # Check if current user has access to this file (same logic as get_source_content)
        source = session.exec(
            select(Source)
            .where(Source.source_data_id == source_id)
            .where(Source.owner_id == current_user.id)
        ).first()

        if not source and not current_user.is_superuser:
            kb_access = session.exec(
                select(KnowledgeBase)
                .join(Source, KnowledgeBase.id == Source.knowledge_base_id)
                .where(Source.source_data_id == source_id)
                .where(KnowledgeBase.owner_id == current_user.id)
            ).first()

            if not kb_access:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to access this file",
                )

        # Get source name for validation
        file_source = session.exec(
            select(Source).where(Source.source_data_id == source_id)
        ).first()
        file_name = file_source.name if file_source else f"file-{source_id}.rtf"

        # Check if it's an RTF file
        if not file_name.lower().endswith(".rtf"):
            raise HTTPException(status_code=400, detail="File is not an RTF document")

        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(suffix=".rtf", delete=False) as temp_rtf:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                try:
                    # Write the source data to temporary RTF file
                    temp_rtf.write(source_data.data)
                    temp_rtf.flush()

                    print(f"Converting RTF to PDF: {file_name}")

                    # Read RTF content and convert to text
                    with open(
                        temp_rtf.name, "r", encoding="utf-8", errors="ignore"
                    ) as rtf_file:
                        rtf_content = rtf_file.read()

                    # Convert RTF to plain text
                    text_content = rtf_to_text(rtf_content)

                    print(f"Converting text to PDF for: {file_name}")

                    # Convert text to PDF using ReportLab
                    text_to_pdf_with_reportlab(text_content, temp_pdf.name, file_name)

                    # Read the generated PDF
                    with open(temp_pdf.name, "rb") as pdf_file:
                        pdf_content = pdf_file.read()

                    # Generate PDF filename
                    pdf_filename = f"{os.path.splitext(file_name)[0]}.pdf"

                    print(
                        f"Successfully converted {file_name} to PDF ({len(pdf_content)} bytes)"
                    )

                    # Return the PDF
                    return Response(
                        content=pdf_content,
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": f'inline; filename="{pdf_filename}"'
                        },
                    )

                finally:
                    # Clean up temp files
                    try:
                        os.unlink(temp_rtf.name)
                        os.unlink(temp_pdf.name)
                    except Exception as cleanup_error:
                        print(
                            f"Warning: Failed to clean up temp files: {cleanup_error}"
                        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"RTF PDF conversion failed: {str(e)}"
        )


@router.get("/source/by-filename/{filename}/rtf-pdf")
async def convert_rtf_to_pdf_by_filename(
    filename: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Response:
    """
    Convert an RTF source file to PDF on-demand using filename.
    Only works with RTF files that the user has access to.
    """
    try:
        # Find the source by filename that the user has access to
        source = session.exec(
            select(Source)
            .where(Source.name == filename)
            .where(Source.owner_id == current_user.id)
        ).first()

        if not source and not current_user.is_superuser:
            # Check if they have access through knowledge base
            source = session.exec(
                select(Source)
                .join(KnowledgeBase, KnowledgeBase.id == Source.knowledge_base_id)
                .where(Source.name == filename)
                .where(KnowledgeBase.owner_id == current_user.id)
            ).first()

        if not source:
            raise HTTPException(
                status_code=404, detail="Source file not found or access denied"
            )

        # Check if it's an RTF file
        if not filename.lower().endswith(".rtf"):
            raise HTTPException(status_code=400, detail="File is not an RTF document")

        # Get the source data
        source_data = session.get(SourceData, source.source_data_id)
        if not source_data:
            raise HTTPException(status_code=404, detail="Source data not found")

        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(suffix=".rtf", delete=False) as temp_rtf:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                try:
                    # Write the source data to temporary RTF file
                    temp_rtf.write(source_data.data)
                    temp_rtf.flush()

                    print(f"Converting RTF to PDF by filename: {filename}")

                    # Read RTF content and convert to text
                    with open(
                        temp_rtf.name, "r", encoding="utf-8", errors="ignore"
                    ) as rtf_file:
                        rtf_content = rtf_file.read()

                    # Convert RTF to plain text
                    text_content = rtf_to_text(rtf_content)

                    print(f"Converting text to PDF for filename: {filename}")

                    # Convert text to PDF using ReportLab
                    text_to_pdf_with_reportlab(text_content, temp_pdf.name, filename)

                    # Read the generated PDF
                    with open(temp_pdf.name, "rb") as pdf_file:
                        pdf_content = pdf_file.read()

                    # Generate PDF filename
                    pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"

                    print(
                        f"Successfully converted {filename} to PDF ({len(pdf_content)} bytes)"
                    )

                    # Return the PDF
                    return Response(
                        content=pdf_content,
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": f'inline; filename="{pdf_filename}"'
                        },
                    )

                finally:
                    # Clean up temp files
                    try:
                        os.unlink(temp_rtf.name)
                        os.unlink(temp_pdf.name)
                    except Exception as cleanup_error:
                        print(
                            f"Warning: Failed to clean up temp files: {cleanup_error}"
                        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"RTF PDF conversion failed: {str(e)}"
        )


@router.get("/source/by-filename/{filename}", response_model=SourceContentResponse)
async def get_source_content_by_filename(
    filename: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> SourceContentResponse:
    """
    Retrieve a source file by filename.
    Only returns files that the user has access to (either owns or has permissions for).
    """
    try:
        # Find the source by filename that the user has access to
        source = session.exec(
            select(Source)
            .where(Source.name == filename)
            .where(Source.owner_id == current_user.id)
        ).first()

        if not source and not current_user.is_superuser:
            # Check if they have access through knowledge base
            source = session.exec(
                select(Source)
                .join(KnowledgeBase, KnowledgeBase.id == Source.knowledge_base_id)
                .where(Source.name == filename)
                .where(KnowledgeBase.owner_id == current_user.id)
            ).first()

        if not source:
            raise HTTPException(
                status_code=404, detail="Source file not found or access denied"
            )

        # Get the source data
        source_data = session.get(SourceData, source.source_data_id)
        if not source_data:
            raise HTTPException(status_code=404, detail="Source data not found")

        # Extract the file content from the ZIP
        zip_data = BytesIO(source_data.data)
        with zipfile.ZipFile(zip_data, "r") as zip_file:
            # Get the first file in the archive
            file_info = zip_file.infolist()[0]
            file_content = zip_file.read(file_info.filename)

            # Determine content type
            content_type = (
                mimetypes.guess_type(filename)[0] or "application/octet-stream"
            )

            # Base64 encode for transmission
            content_base64 = base64.b64encode(file_content).decode("utf-8")

            return {
                "id": str(source.source_data_id),
                "name": filename,
                "data_base64": content_base64,
                "content_type": content_type,
            }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")
