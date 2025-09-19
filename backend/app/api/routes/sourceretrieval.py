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
