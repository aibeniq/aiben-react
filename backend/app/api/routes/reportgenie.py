import uuid
from app.models import (
    ReportGenieRequest,
    ReportGenieResponse,
    ReportGenieOutline,
    ReportGenieDetailResponse,
    Source,
    KnowledgeBase,
    EmbeddingModel,
    DocxRequest,
    LlmInteraction,
    Message,
    GenerateOutlineRequest,
    GenerateOutlineResponse,
    OptimizeOutlineRequest,
    OutlineSuggestion,
    OptimizedOutlineResponse,
)
from pathlib import Path
import re
import tempfile
import zipfile
import json
import traceback
import csv
from io import BytesIO, StringIO
from datetime import datetime
from fastapi.responses import StreamingResponse
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import markdown
from bs4 import BeautifulSoup

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.services.knowledgebases import get_embedding_model
from app.services.embeddings import load_embeddings_model
from app.services.llms import get_default_llm, invoke_llm, record_llm_interaction
from app.services.retrievers import (
    create_ensemble_retriever,
)  # Import the ensemble retriever
from app.services.text_processing import chunk_text, estimate_tokens

from sqlmodel import select
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Request as FastAPIRequest,
)
from typing import List, Dict, Any, Optional
import asyncio

from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import os

router = APIRouter(prefix="/reportgenie", tags=["reportgenie"])


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from various file formats."""
    try:
        # Determine file type from extension
        file_ext = Path(filename).suffix.lower()

        if file_ext == ".pdf":
            # Handle PDF files
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                loader = PyPDFLoader(temp_file_path)
                documents = loader.load()
                text = "\n\n".join([doc.page_content for doc in documents])
                return text
            finally:
                os.unlink(temp_file_path)

        elif file_ext in [".docx", ".doc"]:
            # Handle Word documents
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=file_ext
            ) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            try:
                if file_ext == ".docx":
                    doc = Document(temp_file_path)
                    text_parts = []
                    for paragraph in doc.paragraphs:
                        if paragraph.text.strip():
                            text_parts.append(paragraph.text)

                    # Also extract text from tables
                    for table in doc.tables:
                        for row in table.rows:
                            for cell in row.cells:
                                if cell.text.strip():
                                    text_parts.append(cell.text)

                    return "\n\n".join(text_parts)
                else:
                    # For .doc files, fall back to textloader
                    loader = TextLoader(temp_file_path)
                    documents = loader.load()
                    return "\n\n".join([doc.page_content for doc in documents])
            finally:
                os.unlink(temp_file_path)

        elif file_ext == ".txt":
            # Handle text files
            return file_content.decode("utf-8", errors="ignore")

        else:
            # For other formats, try to decode as text
            return file_content.decode("utf-8", errors="ignore")

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error extracting text from {filename}: {str(e)}"
        )


@router.post("/generate", response_model=ReportGenieResponse)
async def generate_report(
    session: SessionDep,
    current_user: CurrentUser,
    request: ReportGenieRequest = Depends(),
):
    """
    Generate a report based on sections outline and knowledge base search results.
    """
    try:
        # 1. Retrieve knowledge base from database
        kb = session.get(KnowledgeBase, request.knowledge_base_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        if kb.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You don't have access to this knowledge base"
            )

        # Initialize the LLM
        llm = get_default_llm(session, current_user)

        # Parse sections
        try:
            sections_data = json.loads(request.sections)
            if isinstance(sections_data, list) and all(
                isinstance(item, dict) and "text" in item and "consultDocuments" in item
                for item in sections_data
            ):
                section_items = sections_data
            else:
                raise ValueError("Invalid sections format")
        except (json.JSONDecodeError, TypeError, ValueError):
            section_list = request.sections.strip().split("\n")
            section_items = [
                {"text": section.strip(), "consultDocuments": True}
                for section in section_list
                if section.strip()
            ]

        # Process each section
        sections = []
        draft_report = ""

        for section_item in section_items:
            section_description = section_item["text"]
            consult_documents = section_item.get("consultDocuments", True)
            search_type = section_item.get("searchType", "vector")  # Default to vector

            if not section_description:
                continue

            if consult_documents:
                if search_type == "full_text":
                    # Full Text Scan Logic
                    print(f"Performing Full Text Scan for: {section_description}")
                    all_source_text = ""
                    sources = session.exec(
                        select(Source).where(Source.knowledge_base_id == kb.id)
                    ).all()
                    for source in sources:
                        all_source_text += (
                            f"\n\n--- Source: {source.name} ---\n\n{source.content}"
                        )

                    text_chunks = chunk_text(
                        all_source_text,
                        max_tokens=settings.DOCUMENT_CHUNK_SIZE,
                    )
                    chunk_analyses = []
                    for chunk in text_chunks:
                        analysis = invoke_llm(
                            llm,
                            settings.CHATBOT_FULL_TEXT_CHUNK_PROMPT_TEMPLATE,
                            {"chunk": chunk, "question": section_description},
                        )
                        chunk_analyses.append(analysis)

                    # Synthesize the chunk analyses
                    synthesized_answer = invoke_llm(
                        llm,
                        settings.CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE,
                        {
                            "chunk_analyses": "\n\n".join(chunk_analyses),
                            "question": section_description,
                        },
                    )

                    sections.append(
                        {
                            "title": section_description,
                            "content": synthesized_answer,
                            "consult_documents": True,
                        }
                    )
                else:
                    # Vector Search Logic
                    print(f"Performing Vector Search for: {section_description}")
                    retriever = create_ensemble_retriever(kb, session, current_user)
                    search_results = retriever.retrieve(
                        section_description, k=settings.RAG_NUM_CHUNKS
                    )

                    synthesized_answer = invoke_llm(
                        llm,
                        settings.REPORT_GENIE_SYNTHESIS_PROMPT_TEMPLATE,
                        {"context": search_results, "question": section_description},
                    )

                    sections.append(
                        {
                            "title": section_description,
                            "content": synthesized_answer,
                            "consult_documents": True,
                        }
                    )
            else:
                # Use raw text directly without consulting knowledge base
                section_content = section_description
                source_citations = []

            section_title = section_description

            # Store the section with its content and sources
            sections.append(
                {
                    "title": section_title,
                    "content": section_content,
                    "source_citations": source_citations,
                    "consult_documents": consult_documents,
                }
            )
            draft_report += f"\n\n## {section_title}\n\n{section_content}"

        # 7. Compile the final report
        full_report = "\n\n---\n\n".join(
            [section["content"].strip() for section in sections]
        )

        result = {"full_report": full_report, "sections": sections}

        # Get outline name if outline_id is provided
        outline_name = None
        if hasattr(request, "outline_id") and request.outline_id:
            try:
                outline = session.get(ReportGenieOutline, request.outline_id)
                if outline:
                    outline_name = outline.name
            except Exception as e:
                print(f"Warning: Error retrieving outline name: {e}")

        # If no outline_id but we have sections, use first line or "Custom Outline"
        if not outline_name and request.sections:
            first_line = request.sections.strip().split("\n")[0]
            if first_line:
                # Extract a name from the first section (limited to 30 chars)
                outline_name = first_line[:30] + ("..." if len(first_line) > 30 else "")
            else:
                outline_name = "Custom Outline"

        # Store the full report and sections data in extra_data for retrieval later
        detailed_extra_data = {
            "kb_name": kb.title,
            "full_report": full_report,
            "sections": sections,  # This includes section content and sources
            "outline_name": outline_name,  # Add the outline name here
        }

        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="reportgenie",
            input_data={
                "sections": request.sections,
                "kb_id": request.knowledge_base_id,
                "outline_id": (
                    request.outline_id if hasattr(request, "outline_id") else None
                ),
            },
            output_data={
                "section_count": len(sections),
                "total_length": len(full_report),
            },
            metadata=detailed_extra_data,
        )

        return ReportGenieResponse(results=result)

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating report: {str(e)}"
        )


# Functions related to Outlines
@router.post("/outlines", response_model=ReportGenieOutline)
def create_outline(
    outline: ReportGenieOutline, session: SessionDep, current_user: CurrentUser
):
    """
    Save a new outline to the database.
    """
    existing_outline = session.exec(
        select(ReportGenieOutline).where(ReportGenieOutline.name == outline.name)
    ).first()
    if existing_outline:
        raise HTTPException(
            status_code=400, detail="An outline with this name already exists."
        )

    outline.owner_id = current_user.id
    session.add(outline)
    session.commit()
    session.refresh(outline)
    return outline


@router.get("/outlines", response_model=List[ReportGenieOutline])
def get_outlines(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve all outlines from the database for this user.
    """
    print(f"Retrieving outlines for user {current_user.id}")
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    try:
        outlines = session.exec(
            select(ReportGenieOutline).where(
                ReportGenieOutline.owner_id == current_user.id
            )
        ).all()

        # Print the retrieved outlines for debugging
        print(f"Found {len(outlines)} outlines for user {current_user.id}:")
        for i, outline in enumerate(outlines):
            try:
                section_count = (
                    len(outline.sections.split("\n")) if outline.sections else 0
                )
                print(
                    f"  {i+1}. ID: {outline.id}, Name: {outline.name}, Sections: {section_count} sections"
                )
            except Exception as e:
                print(f"  {i+1}. ID: {outline.id}, Error processing outline: {str(e)}")

        return outlines
    except Exception as e:
        print(f"Error retrieving outlines: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving outlines: {str(e)}"
        )


@router.get("/outlines/{outline_id}", response_model=ReportGenieOutline)
def get_outline(outline_id: uuid.UUID, session: SessionDep):
    """
    Retrieve a specific outline by ID.
    """
    outline = session.get(ReportGenieOutline, outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found.")
    return outline


@router.put("/outlines/{outline_id}", response_model=ReportGenieOutline)
def update_outline(
    outline_id: uuid.UUID,
    updated_outline: ReportGenieOutline,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Update an existing outline.
    """
    outline = session.get(ReportGenieOutline, outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found.")

    # Ensure the current user is the owner of the outline
    if outline.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this outline."
        )

    outline.name = updated_outline.name
    outline.description = updated_outline.description
    outline.sections = updated_outline.sections
    outline.date_modified = datetime.utcnow()

    session.add(outline)
    session.commit()
    session.refresh(outline)
    return outline


@router.delete("/outlines/{outline_id}", response_model=Message)
def delete_outline(
    outline_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
):
    """
    Delete an outline by ID.
    """
    outline = session.get(ReportGenieOutline, outline_id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found.")

    # Ensure the current user is the owner of the outline
    if outline.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this outline."
        )

    session.delete(outline)
    session.commit()
    return Message(message="Outline deleted successfully.")


@router.post("/generate-outline", response_model=GenerateOutlineResponse)
def generate_outline(
    request_data: GenerateOutlineRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Generate outline sections based on a description using LLM.
    """
    try:
        # Get the default LLM
        llm = get_default_llm(session, current_user)

        # Prepare variables for the prompt
        prompt_variables = {
            "description": request_data.description,
            "report_type": request_data.report_type,
        }

        # Generate outline sections using the LLM
        outline_response = invoke_llm(
            llm,
            settings.REPORTGENIE_GENERATE_OUTLINE_PROMPT_TEMPLATE,
            prompt_variables,
        )

        # Parse the response to extract sections and analysis
        sections = []
        analysis = ""

        lines = outline_response.strip().split("\n")
        in_sections_section = False
        in_analysis_section = False

        for line in lines:
            line = line.strip()
            if line.startswith("SECTIONS:"):
                in_sections_section = True
                in_analysis_section = False
                continue
            elif line.startswith("ANALYSIS:"):
                in_sections_section = False
                in_analysis_section = True
                continue

            if in_sections_section:
                # Extract sections (numbered list)
                if re.match(r"^\d+\.\s+", line):
                    section = re.sub(r"^\d+\.\s+", "", line)
                    if section.strip():
                        sections.append(section.strip())
            elif in_analysis_section:
                if line:
                    if analysis:
                        analysis += " " + line
                    else:
                        analysis = line

        # If parsing failed, try simpler approach
        if not sections:
            # Split by lines and look for numbered items
            for line in lines:
                line = line.strip()
                if re.match(r"^\d+\.\s+", line):
                    section = re.sub(r"^\d+\.\s+", "", line)
                    if section.strip():
                        sections.append(section.strip())

        # Ensure we have some sections
        if not sections:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate sections from the description. Please try with a more detailed description.",
            )

        # Apply user-specified limit if provided, otherwise use all generated sections
        if request_data.num_sections:
            sections = sections[: request_data.num_sections]

        if not analysis:
            analysis = f"Generated {len(sections)} sections based on the provided description to ensure comprehensive report structure coverage."

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="generate_outline_sections",
            input_data={
                "description": request_data.description,
                "requested_sections": request_data.num_sections,
                "report_type": request_data.report_type,
            },
            output_data={
                "sections_count": len(sections),
                "analysis": analysis,
            },
            metadata={},
        )

        return GenerateOutlineResponse(sections=sections, description_analysis=analysis)

    except Exception as e:
        print(f"Error generating outline: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating outline: {str(e)}"
        )


@router.post("/generate/docx", response_class=StreamingResponse)
async def generate_docx(
    session: SessionDep, current_user: CurrentUser, request: DocxRequest
):
    """
    Generate a DOCX file from the report content.
    """
    print("Now generating DOCX of report...")
    try:
        # Get the markdown content from the request
        if not request.content:
            raise HTTPException(
                status_code=400, detail="No content provided for DOCX generation."
            )

        # Convert markdown to HTML for parsing
        html_content = markdown.markdown(
            request.content, extensions=["tables", "fenced_code"]
        )
        soup = BeautifulSoup(html_content, "html.parser")

        print("Markdown content converted to HTML successfully.")
        # Create a new Document
        doc = Document()

        print("Adding title and date to the document...")
        # Add a title
        doc.add_heading("Generated Report", level=0).alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        # Add date
        date_paragraph = doc.add_paragraph()
        date_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        date_run = date_paragraph.add_run(
            f"Generated on: {datetime.now().strftime('%B %d, %Y')}"
        )
        date_run.italic = True
        doc.add_paragraph()  # Add a space after the date

        # Process each element from the parsed HTML
        for element in soup.find_all(True, recursive=False):
            if element.name.startswith("h") and element.name[1:].isdigit():
                level = int(element.name[1:])
                doc.add_heading(element.get_text(strip=True), level=level)
            elif element.name == "p":
                if element.get_text(strip=True):  # Avoid empty paragraphs
                    doc.add_paragraph(element.get_text())
            elif element.name == "hr":
                doc.add_paragraph("---")  # Visual separator
            elif element.name == "table":
                headers = [th.get_text(strip=True) for th in element.find_all("th")]
                if not headers:
                    continue

                table = doc.add_table(rows=1, cols=len(headers))
                table.style = "Table Grid"
                hdr_cells = table.rows[0].cells
                for i, h in enumerate(headers):
                    hdr_cells[i].text = h

                for row in element.find("tbody").find_all("tr"):
                    row_cells = table.add_row().cells
                    for i, td in enumerate(row.find_all("td")):
                        row_cells[i].text = td.get_text(strip=True)
            elif element.name in ["ul", "ol"]:
                for li in element.find_all("li"):
                    doc.add_paragraph(li.get_text(strip=True), style="List Bullet")

        # Save the document to a memory stream
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)

        print("DOCX file generated and ready for streaming.")
        # Return as a streaming response
        return StreamingResponse(
            file_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=generated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
            },
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating DOCX file: {str(e)}"
        )


@router.post("/generate/csv", response_class=StreamingResponse)
async def generate_csv(
    session: SessionDep, current_user: CurrentUser, request: DocxRequest
):
    """
    Generate a CSV file from the report content with sections, content, and citations.
    """
    print("Now generating CSV of report...")
    try:
        # Get the content from the request - this should be the full report JSON or the report ID
        if not request.content:
            raise HTTPException(status_code=400, detail="Report content is required")

        # For CSV generation, we need the structured sections data, not just the markdown text
        # The request.content should contain either the report ID or the full sections data

        # Create CSV content
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)

        # Write header
        csv_writer.writerow(["Prompt", "Content", "Citations"])

        try:
            # Try to parse the content as JSON (sections data)
            data = json.loads(request.content)

            if "sections" in data:
                sections = data["sections"]
            else:
                # If it's just a list of sections
                sections = data if isinstance(data, list) else []

        except json.JSONDecodeError:
            # If it's not JSON, try to extract from a report ID or return error
            raise HTTPException(
                status_code=400,
                detail="Invalid content format. Expected JSON with sections data.",
            )

        # Process each section
        for section in sections:
            prompt = section.get("title", "")
            content = section.get("content", "").replace("\n", " ").replace("\r", " ")

            # Extract citations
            citations = []
            if "source_citations" in section:
                for citation in section["source_citations"]:
                    source_name = "Unknown"
                    if citation.get("metadata", {}).get("source"):
                        source_path = citation["metadata"]["source"]
                        # Extract filename from path
                        source_name = source_path.split("/")[-1].split("\\")[-1]
                        # Remove UUID prefix if present
                        if "_" in source_name:
                            source_name = source_name.split("_", 1)[1]

                    citation_text = (
                        citation.get("content", "")
                        .replace("\n", " ")
                        .replace("\r", " ")
                    )
                    citations.append(f"{source_name}: {citation_text}")

            citations_text = " | ".join(citations) if citations else "No citations"

            # Write row
            csv_writer.writerow([prompt, content, citations_text])

        # Get CSV content
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        # Create BytesIO object for the response
        csv_bytes = BytesIO(csv_content.encode("utf-8"))
        csv_bytes.seek(0)

        print("CSV file generated successfully.")

        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.csv"

        # Return the CSV as a downloadable file
        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating CSV: {str(e)}")


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_report_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
    show_all: bool = False,
):
    """Retrieve past report generation history for the current user or all users."""
    print("Retrieving report history. Show all:", show_all)

    try:
        # Start with base query
        query = select(LlmInteraction).where(
            LlmInteraction.functionality == "reportgenie"
        )

        # Only filter by user if not showing all users
        if not show_all:
            query = query.where(LlmInteraction.user_id == current_user.id)

        # Add ordering and pagination
        reports = session.exec(
            query.order_by(LlmInteraction.date_created.desc()).offset(skip).limit(limit)
        ).all()

        print("Found {} reports for user {}:".format(len(reports), current_user.id))

        result = []
        for report in reports:
            # Parse the input_data and output_data from string to dict if possible
            try:
                input_data = json.loads(report.input_data) if report.input_data else {}
                output_data = (
                    json.loads(report.output_data) if report.output_data else {}
                )
                extra_data = report.extra_data or {}

                # Create a user-friendly title
                kb_name = extra_data.get("kb_name", "Unknown Knowledge Base")
                title = f"Report on {kb_name}"
                date = report.date_created.strftime("%Y-%m-%d %H:%M")

                # Create the result item
                result_item = {
                    "id": str(report.id),
                    "date_created": report.date_created,
                    "title": title,
                    "sections": input_data.get("sections", ""),
                    "kb_id": input_data.get("kb_id", ""),
                    "section_count": output_data.get("section_count", 0),
                    "kb_name": kb_name,
                    "outline_name": extra_data.get("outline_name", ""),
                    "has_feedback": report.feedback is not None,
                }

                # Add feedback information if exists
                if report.feedback:
                    result_item["feedback"] = {
                        "feedback": report.feedback,
                        "feedbackText": report.feedback_text,
                    }

                # Add user info for all-users view
                if show_all:
                    from app.models import User  # Import here to avoid circular imports

                    user = session.get(User, report.user_id)
                    user_name = (
                        f"{user.full_name or 'User'} ({user.email})"
                        if user
                        else "Unknown User"
                    )
                    result_item["user_name"] = user_name

                result.append(result_item)
            except json.JSONDecodeError:
                # If JSON parsing fails, use raw data
                result_item = {
                    "id": str(report.id),
                    "date_created": report.date_created,
                    "title": f"Report from {report.date_created.strftime('%Y-%m-%d')}",
                    "sections": "",
                    "kb_id": "",
                    "section_count": 0,
                    "kb_name": "Unknown Knowledge Base",
                    "outline_name": "",
                    "has_feedback": report.feedback is not None,
                }

                # Add feedback information if exists
                if report.feedback:
                    result_item["feedback"] = {
                        "feedback": report.feedback,
                        "feedbackText": report.feedback_text,
                    }

                # Add user info for all-users view
                if show_all:
                    from app.models import User  # Import here to avoid circular imports

                    user = session.get(User, report.user_id)
                    user_name = (
                        f"{user.full_name or 'User'} ({user.email})"
                        if user
                        else "Unknown User"
                    )
                    result_item["user_name"] = user_name

                result.append(result_item)

        return result
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving report history: {str(e)}"
        )


@router.get("/history/{report_id}", response_model=ReportGenieDetailResponse)
async def get_report_detail(
    report_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Retrieve a specific report's full content by ID."""
    try:
        report = session.get(LlmInteraction, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Because we now allow viewing others' outputs, no longer need to ensure this
        # if report.user_id != current_user.id:
        #    raise HTTPException(
        #        status_code=403, detail="You don't have access to this report"
        #    )

        if report.functionality != "reportgenie":
            raise HTTPException(
                status_code=400, detail="This is not a ReportGenie report"
            )

        # Try to reconstruct the original report structure
        try:
            input_data = json.loads(report.input_data) if report.input_data else {}
            output_data = json.loads(report.output_data) if report.output_data else {}
            extra_data = report.extra_data or {}

            # If we don't have the full report content in extra_data, we need to generate a response
            # that's compatible with the normal report format
            kb_name = extra_data.get("kb_name", "Unknown Knowledge Base")

            # Try to get any saved full report content
            full_report = extra_data.get("full_report", "")

            # Create a response that matches the structure expected by the frontend
            result = {
                "id": str(report.id),
                "date_created": report.date_created,
                "kb_name": kb_name,
                "kb_id": input_data.get("kb_id", ""),
                "sections": input_data.get("sections", ""),
                "results": {
                    "full_report": full_report,
                    "sections": extra_data.get("sections", []),
                },
                # Add feedback information
                "feedback": {
                    "feedback": report.feedback,
                    "feedbackText": report.feedback_text,
                    "feedbackDate": (
                        report.feedback_date.isoformat()
                        if report.feedback_date
                        else None
                    ),
                },
            }

            return result

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "id": str(report.id),
                "date_created": report.date_created,
                "results": {
                    "full_report": f"Unable to reconstruct report from {report.date_created}.\n\n"
                    f"This might be due to an older format or incomplete data.",
                    "sections": [],
                },
                # Add empty feedback object for consistency
                "feedback": {
                    "feedback": None,
                    "feedbackText": None,
                    "feedbackDate": None,
                },
            }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving report details: {str(e)}"
        )


@router.post("/optimize-outline", response_model=OptimizedOutlineResponse)
async def optimize_outline(
    session: SessionDep,
    current_user: CurrentUser,
    request_data: OptimizeOutlineRequest = Depends(),
    files: List[UploadFile] = File(...),
    request: FastAPIRequest = None,
):
    """
    Optimize outline sections by testing them against a ground-truth document.
    Generates a report with current outline and compares it to the ground-truth to suggest improvements.
    """
    print("optimize_outline function invoked!")
    cancellation_requested = False

    try:
        print("Setting up disconnect monitor for outline optimization...")
        disconnect_monitor = None
        if request:

            async def monitor_client_disconnect():
                nonlocal cancellation_requested
                try:
                    await request.is_disconnected()
                    print("Client disconnected, canceling optimization...")
                    cancellation_requested = True
                except asyncio.CancelledError:
                    print("Disconnect monitor cancelled because main task completed")
                except Exception as e:
                    print(f"Error in disconnect monitoring: {str(e)}")

            disconnect_monitor = asyncio.create_task(monitor_client_disconnect())

        print("Starting outline optimization...")

        # 1. Retrieve knowledge base
        kb = session.get(KnowledgeBase, request_data.knowledge_base_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        if kb.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You don't have access to this knowledge base"
            )

        # 2. Set up the same infrastructure as generate_report
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract ChromaDB
            if kb.data:
                with zipfile.ZipFile(BytesIO(kb.data), "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            else:
                raise HTTPException(
                    status_code=400, detail="Knowledge base has no vector database data"
                )

            # Load embeddings and vector database
            if kb.embedding_model_id:
                embedding_model = session.get(EmbeddingModel, kb.embedding_model_id)
                if embedding_model:
                    model_id = embedding_model.model_id
                    provider = embedding_model.provider
                else:
                    embedding_info = get_embedding_model(session, current_user)
                    model_id = embedding_info["model_id"]
                    provider = embedding_info["provider"]
            else:
                embedding_info = get_embedding_model(session, current_user)
                model_id = embedding_info["model_id"]
                provider = embedding_info["provider"]

            embeddings = load_embeddings_model(provider=provider, model_id=model_id)
            chroma_db = Chroma(
                persist_directory=temp_dir, embedding_function=embeddings
            )

            # Create retriever
            retriever = create_ensemble_retriever(
                chroma_db=chroma_db,
                vector_weight=0.7,
                keyword_weight=0.3,
                search_kwargs={"k": settings.RAG_NUM_CHUNKS},
            )

            # Initialize LLM
            llm = get_default_llm(session, current_user)

            # 3. Process the ground-truth document
            file = files[0]
            content = await file.read()
            ground_truth_text = extract_text_from_file(content, file.filename)
            print(
                f"Processing ground-truth document: {file.filename} ({len(ground_truth_text)} characters)"
            )

            # 4. Parse current outline sections
            current_sections = json.loads(request_data.sections)
            print(f"Optimizing {len(current_sections)} outline sections...")

            # 5. Generate report content for each section using current outline
            generated_sections = {}

            for section in current_sections:
                if cancellation_requested:
                    print("Operation cancelled by client disconnect")
                    raise HTTPException(
                        status_code=408, detail="Operation cancelled by user"
                    )

                section_description = section["text"].strip()
                consult_documents = section.get("consultDocuments", True)

                if not section_description:
                    continue

                print(f"Generating content for section: {section_description[:50]}...")

                if consult_documents:
                    # Get relevant context for this section from knowledge base
                    docs = retriever.get_relevant_documents(section_description)
                    context = "\n\n".join([doc.page_content for doc in docs])

                    # Build the report draft so far (all previous sections)
                    report_draft = ""
                    for prev_section, prev_content in generated_sections.items():
                        if prev_content:
                            report_draft += f"\n\n## {prev_section}\n\n{prev_content}"

                    # Generate content for this section using LLM
                    generated_content = invoke_llm(
                        llm,
                        settings.REPORT_GENIE_PROMPT_TEMPLATE,
                        {
                            "report_draft": report_draft,
                            "context": context,
                            "question": section_description,
                        },
                    )
                    print(
                        f"Generated {len(generated_content)} characters for section using knowledge base"
                    )
                else:
                    # Use the section description directly as content (no document consultation)
                    generated_content = section_description
                    print(
                        f"Using section description directly as content (no document consultation)"
                    )

                generated_sections[section_description] = generated_content

            # 6. Map ground-truth document to outline sections sequentially with large chunks
            print(
                "Mapping ground-truth document to outline sections using large-chunk strategy..."
            )

            # Split ground-truth into large chunks (up to 100,000 characters)
            max_chunk_size = 100000  # 100,000 characters per chunk
            ground_truth_chunks = []

            # Split by paragraphs first to avoid breaking sentences/paragraphs
            paragraphs = ground_truth_text.split("\n\n")
            current_chunk = ""

            for paragraph in paragraphs:
                # If adding this paragraph would exceed the limit, start a new chunk
                if (
                    current_chunk
                    and len(current_chunk) + len(paragraph) + 2 > max_chunk_size
                ):
                    if current_chunk.strip():
                        ground_truth_chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph

            # Add the last chunk if it has content
            if current_chunk.strip():
                ground_truth_chunks.append(current_chunk.strip())

            print(
                f"Split ground-truth into {len(ground_truth_chunks)} large chunks (avg {len(ground_truth_text)//len(ground_truth_chunks) if ground_truth_chunks else 0} chars per chunk)"
            )

            # Get list of section descriptions in order
            section_descriptions = list(generated_sections.keys())

            # Map each chunk to the most appropriate section
            section_to_chunks = {section: [] for section in section_descriptions}

            # Track previous mapping decisions for context (enhanced tracking)
            previous_mappings = []
            chunk_mapping_stats = {
                "total": 0,
                "high_confidence": 0,
                "medium_confidence": 0,
                "low_confidence": 0,
            }

            for chunk_idx, chunk in enumerate(ground_truth_chunks):
                if cancellation_requested:
                    print("Operation cancelled by client disconnect")
                    raise HTTPException(
                        status_code=408, detail="Operation cancelled by user"
                    )

                print(
                    f"Mapping large chunk {chunk_idx + 1}/{len(ground_truth_chunks)} ({len(chunk)} chars)..."
                )

                # Build enhanced context from previous mappings
                context_info = ""
                if previous_mappings:
                    # Show the last 3 mappings and their outcomes
                    recent_mappings = previous_mappings[-3:]
                    context_summary = []

                    for pm in recent_mappings:
                        section_names = [
                            section_descriptions[i - 1]
                            for i in pm["assigned_sections"]
                            if 1 <= i <= len(section_descriptions)
                        ]
                        context_summary.append(
                            f"Chunk {pm['chunk_idx']}: Mapped to sections {pm['assigned_sections']} ({', '.join(section_names[:2])}{'...' if len(section_names) > 2 else ''}) - {pm['confidence']} confidence"
                        )

                    context_info = f"""
PREVIOUS MAPPING DECISIONS (Last {len(recent_mappings)} chunks):
{chr(10).join(context_summary)}

MAPPING PROGRESS: {len(previous_mappings)}/{len(ground_truth_chunks)} chunks processed
CONFIDENCE DISTRIBUTION: {chunk_mapping_stats['high_confidence']} High, {chunk_mapping_stats['medium_confidence']} Medium, {chunk_mapping_stats['low_confidence']} Low

This context shows how the document has been mapped so far. Consider:
- Sequential flow: Later chunks typically map to later sections
- Content continuity: Related content often spans adjacent chunks
- Previous patterns: Maintain consistency with established mapping logic
"""

                # Pre-calculate values for the prompt to avoid f-string issues
                chunk_size = len(chunk)
                chunk_preview = chunk[:6000] if chunk_size > 6000 else chunk
                truncation_note = (
                    f"...[CONTENT TRUNCATED - showing first 6000 chars of {chunk_size} total]"
                    if chunk_size > 6000
                    else ""
                )
                document_position_percent = (chunk_idx + 1) / len(ground_truth_chunks)
                mapping_context_note = (
                    "- Mapping context: Previous chunks have established patterns - maintain logical consistency"
                    if previous_mappings
                    else "- First chunk: Set the mapping foundation for subsequent chunks"
                )

                # Use enhanced LLM prompt with context for chunks after the first
                mapping_prompt = f"""
TASK: Map this ground-truth document chunk to the most appropriate outline section(s).

OUTLINE SECTIONS (in order):
{chr(10).join([f"{i+1}. {section}" for i, section in enumerate(section_descriptions)])}

{context_info}

GROUND-TRUTH CHUNK ({chunk_idx + 1} of {len(ground_truth_chunks)}, {chunk_size} characters):
{chunk_preview}
{truncation_note}

DOCUMENT CONTEXT:
- This is chunk {chunk_idx + 1} out of {len(ground_truth_chunks)} sequential chunks from a ground-truth document
- Chunk size: {chunk_size:,} characters (max {max_chunk_size:,} per chunk)
- Document position: {document_position_percent:.1%} through the document
- Sequential order: Chunks are in document order, so position matters for mapping
- Content coherence: Large chunks preserve paragraph boundaries and logical flow
{mapping_context_note}

ENHANCED MAPPING INSTRUCTIONS:
1. Analyze the chunk's main topics, themes, concepts, and structural elements
2. Consider the chunk's position in the document sequence (early/middle/late content)
3. Match content to outline sections that would naturally include this information
4. For document progression: early chunks → early sections, later chunks → later sections
5. Large chunks often contain complete subsections - consider section boundaries
6. You can assign to multiple sections if content clearly spans topics, but prefer focused assignments
7. Use previous mapping context to maintain consistency and avoid conflicts
8. Consider both content similarity AND logical document structure

RESPONSE FORMAT (be precise and detailed):
SECTIONS: [comma-separated list of section numbers, e.g., "1" or "2,3"]
REASONING: [detailed explanation: what content themes were found, why they map to these sections, how this fits with document progression and any context from previous mappings]
CONFIDENCE: [High/Medium/Low - High: very clear match, Medium: reasonable match with some uncertainty, Low: best guess or positional mapping]
"""

                mapping_response = invoke_llm(llm, mapping_prompt, {})

                # Parse the mapping response with enhanced error handling
                assigned_sections = []
                confidence = "Medium"
                reasoning = "No reasoning provided"

                if "SECTIONS:" in mapping_response:
                    try:
                        sections_line = (
                            mapping_response.split("SECTIONS:")[1]
                            .split("REASONING:")[0]
                            .strip()
                        )
                        # Extract section numbers, handling various formats
                        section_numbers = []
                        for part in (
                            sections_line.replace("[", "")
                            .replace("]", "")
                            .replace('"', "")
                            .replace("'", "")
                            .split(",")
                        ):
                            part = part.strip()
                            if part.isdigit():
                                section_numbers.append(int(part))
                            elif "-" in part and all(
                                x.isdigit() for x in part.split("-")
                            ):
                                # Handle ranges like "2-4"
                                start, end = map(int, part.split("-"))
                                section_numbers.extend(range(start, end + 1))

                        for section_num in section_numbers:
                            if 1 <= section_num <= len(section_descriptions):
                                section_desc = section_descriptions[section_num - 1]
                                if section_desc not in assigned_sections:
                                    assigned_sections.append(section_desc)

                        # Extract reasoning if available
                        if "REASONING:" in mapping_response:
                            reasoning_part = mapping_response.split("REASONING:")[1]
                            if "CONFIDENCE:" in reasoning_part:
                                reasoning = reasoning_part.split("CONFIDENCE:")[
                                    0
                                ].strip()
                            else:
                                reasoning = reasoning_part.strip()

                        # Extract confidence if available
                        if "CONFIDENCE:" in mapping_response:
                            confidence_part = mapping_response.split("CONFIDENCE:")[
                                1
                            ].strip()
                            # Normalize confidence values
                            confidence_lower = confidence_part.lower()
                            if "high" in confidence_lower:
                                confidence = "High"
                            elif "low" in confidence_lower:
                                confidence = "Low"
                            else:
                                confidence = "Medium"

                    except Exception as e:
                        print(
                            f"Warning: Could not parse section mapping for chunk {chunk_idx + 1}: {e}"
                        )
                        print(f"Raw response: {mapping_response[:200]}...")

                # Enhanced fallback logic for large chunks with better positioning
                if not assigned_sections:
                    print(
                        f"No sections assigned by LLM for chunk {chunk_idx + 1}, using enhanced fallback..."
                    )

                    # Calculate chunk position and use content analysis for better fallback
                    chunk_position = chunk_idx / len(ground_truth_chunks)

                    # Analyze chunk content for keywords to help with mapping
                    chunk_lower = chunk[
                        :2000
                    ].lower()  # Analyze first 2000 chars for keywords

                    # Try to match chunk content to section keywords
                    section_scores = []
                    for i, section_desc in enumerate(section_descriptions):
                        section_words = set(section_desc.lower().split())
                        chunk_words = set(chunk_lower.split())
                        overlap = len(section_words.intersection(chunk_words))
                        section_scores.append((i, overlap))

                    # Sort by overlap score
                    section_scores.sort(key=lambda x: x[1], reverse=True)
                    best_content_match = section_scores[0] if section_scores else (0, 0)

                    # Combine position and content analysis for better fallback
                    if best_content_match[1] > 0:  # If there's content overlap
                        assigned_sections = [
                            section_descriptions[best_content_match[0]]
                        ]
                        reasoning = f"Fallback: Content analysis found {best_content_match[1]} keyword matches with section {best_content_match[0] + 1}"
                    else:
                        # Use positional fallback with improved logic
                        if chunk_idx == 0:
                            # First chunk: likely maps to first section(s)
                            assigned_sections = [section_descriptions[0]]
                            reasoning = "Fallback: First chunk mapped to first section"
                        elif chunk_idx == len(ground_truth_chunks) - 1:
                            # Last chunk: likely maps to last section(s)
                            assigned_sections = [section_descriptions[-1]]
                            reasoning = "Fallback: Last chunk mapped to last section"
                        else:
                            # Middle chunks: proportional mapping with adjacent section consideration
                            primary_section_index = min(
                                int(chunk_position * len(section_descriptions)),
                                len(section_descriptions) - 1,
                            )
                            assigned_sections = [
                                section_descriptions[primary_section_index]
                            ]

                            # For large chunks in middle, consider adjacent sections
                            if len(chunk) > 50000 and len(section_descriptions) > 2:
                                if primary_section_index > 0:
                                    assigned_sections.insert(
                                        0,
                                        section_descriptions[primary_section_index - 1],
                                    )
                                elif (
                                    primary_section_index
                                    < len(section_descriptions) - 1
                                ):
                                    assigned_sections.append(
                                        section_descriptions[primary_section_index + 1]
                                    )

                            reasoning = f"Fallback: Positional mapping for chunk at {chunk_position:.1%} position (size {len(chunk):,} chars)"

                    confidence = "Low"
                    print(
                        f"Fallback mapping: Assigned chunk {chunk_idx + 1} to {[section_descriptions.index(s) + 1 for s in assigned_sections]} - {reasoning}"
                    )
                else:
                    print(
                        f"LLM mapping: Chunk {chunk_idx + 1} → sections {[section_descriptions.index(s) + 1 for s in assigned_sections]} ({confidence} confidence)"
                    )

                # Update mapping statistics
                chunk_mapping_stats["total"] += 1
                if confidence == "High":
                    chunk_mapping_stats["high_confidence"] += 1
                elif confidence == "Medium":
                    chunk_mapping_stats["medium_confidence"] += 1
                else:
                    chunk_mapping_stats["low_confidence"] += 1

                # Record this mapping decision for future context (enhanced tracking)
                mapping_decision = {
                    "chunk_idx": chunk_idx + 1,
                    "assigned_sections": [
                        section_descriptions.index(s) + 1 for s in assigned_sections
                    ],
                    "confidence": confidence,
                    "reasoning": (
                        reasoning[:150] + "..." if len(reasoning) > 150 else reasoning
                    ),
                    "chunk_size": len(chunk),
                    "document_position": chunk_idx / len(ground_truth_chunks),
                    "fallback_used": "Fallback" in reasoning,
                }
                previous_mappings.append(mapping_decision)

                # Add chunk to assigned sections with comprehensive metadata
                for section in assigned_sections:
                    chunk_metadata = {
                        "content": chunk,
                        "chunk_index": chunk_idx,
                        "chunk_size": len(chunk),
                        "confidence": confidence,
                        "reasoning": reasoning,
                        "mapping_context": len(previous_mappings)
                        > 1,  # Whether context was available
                        "document_position": chunk_idx / len(ground_truth_chunks),
                        "fallback_used": "Fallback" in reasoning,
                        "section_assignment_count": len(
                            assigned_sections
                        ),  # How many sections this chunk maps to
                        "content_preview": (
                            chunk[:200] + "..." if len(chunk) > 200 else chunk
                        ),  # For debugging
                    }
                    section_to_chunks[section].append(chunk_metadata)

            print(
                "Ground-truth mapping complete. Generating optimization suggestions..."
            )

            # 7. Compare each section's generated content to its mapped ground-truth chunks
            suggestions = []
            optimization_count = 0

            for section_description, generated_content in generated_sections.items():
                if cancellation_requested:
                    print("Operation cancelled by client disconnect")
                    raise HTTPException(
                        status_code=408, detail="Operation cancelled by user"
                    )

                print(f"Analyzing section: {section_description[:50]}...")

                # Get the mapped ground-truth content for this section
                mapped_chunks = section_to_chunks.get(section_description, [])
                ground_truth_context = "\n\n".join(
                    [
                        chunk["content"] if isinstance(chunk, dict) else chunk
                        for chunk in mapped_chunks
                    ]
                )

                # Create an enhanced summary of the mapping for debugging and analysis
                mapping_summary = ""
                if mapped_chunks:
                    chunk_count = len(mapped_chunks)
                    high_confidence = sum(
                        1
                        for chunk in mapped_chunks
                        if isinstance(chunk, dict) and chunk.get("confidence") == "High"
                    )
                    medium_confidence = sum(
                        1
                        for chunk in mapped_chunks
                        if isinstance(chunk, dict)
                        and chunk.get("confidence") == "Medium"
                    )
                    low_confidence = sum(
                        1
                        for chunk in mapped_chunks
                        if isinstance(chunk, dict) and chunk.get("confidence") == "Low"
                    )
                    fallback_count = sum(
                        1
                        for chunk in mapped_chunks
                        if isinstance(chunk, dict) and chunk.get("fallback_used", False)
                    )

                    total_content_size = sum(
                        (
                            chunk.get("chunk_size", 0)
                            if isinstance(chunk, dict)
                            else len(chunk)
                        )
                        for chunk in mapped_chunks
                    )

                    mapping_summary = f" (mapped {chunk_count} chunks: {high_confidence}H/{medium_confidence}M/{low_confidence}L confidence, {fallback_count} fallback, {total_content_size:,} chars total)"

                # If no chunks were mapped to this section, use a fallback
                if not ground_truth_context.strip():
                    ground_truth_context = "No specific content was mapped to this section from the ground-truth document."
                    print(
                        f"Warning: No ground-truth content mapped to section: {section_description[:30]}..."
                    )
                else:
                    print(
                        f"Mapped content to section: {section_description[:30]}...{mapping_summary}"
                    )

                # Generate optimization suggestion
                suggestion_response = invoke_llm(
                    llm,
                    settings.REPORTGENIE_OPTIMIZE_OUTLINE_PROMPT_TEMPLATE,
                    {
                        "original_section": section_description,
                        "generated_content": generated_content[
                            :2000
                        ],  # Limit to avoid token limits
                        "ground_truth_content": ground_truth_context[
                            :2000
                        ],  # Limit to avoid token limits
                    },
                )

                # Parse the response
                needs_revision = "NEEDS_REVISION: Yes" in suggestion_response

                # Extract suggested section
                suggested_section = section_description  # Default to original
                if "SUGGESTED_SECTION:" in suggestion_response:
                    lines = suggestion_response.split("\n")
                    for line in lines:
                        if line.startswith("SUGGESTED_SECTION:"):
                            suggested_section = line.replace(
                                "SUGGESTED_SECTION:", ""
                            ).strip()
                            break

                # Extract reason
                reason = "No specific reason provided"
                if "REASON:" in suggestion_response:
                    lines = suggestion_response.split("\n")
                    for line in lines:
                        if line.startswith("REASON:"):
                            reason = line.replace("REASON:", "").strip()
                            break

                if needs_revision:
                    optimization_count += 1

                suggestions.append(
                    OutlineSuggestion(
                        original_section=section_description,
                        suggested_section=suggested_section,
                        reason=reason,
                        current_output=generated_content[
                            :1000
                        ],  # Show first 1000 chars
                        ground_truth_content=ground_truth_context[
                            :1000
                        ],  # Show first 1000 chars
                        needs_revision=needs_revision,
                    )
                )

                print(
                    f"Section analysis complete: {'NEEDS OPTIMIZATION' if needs_revision else 'OK'}"
                )

            # 7. Compile results
            original_sections = list(generated_sections.keys())
            optimized_sections = [s.suggested_section for s in suggestions]

            # Calculate enhanced mapping statistics
            total_chunks = len(ground_truth_chunks)
            mapped_chunk_instances = sum(
                len(chunks) for chunks in section_to_chunks.values()
            )
            unique_chunks_mapped = len(
                set(
                    chunk.get("chunk_index", -1) if isinstance(chunk, dict) else -1
                    for chunks in section_to_chunks.values()
                    for chunk in chunks
                )
            )

            # Confidence distribution
            confidence_distribution = {
                "high": chunk_mapping_stats["high_confidence"],
                "medium": chunk_mapping_stats["medium_confidence"],
                "low": chunk_mapping_stats["low_confidence"],
            }

            # Calculate coverage metrics
            coverage_percentage = (
                (unique_chunks_mapped / total_chunks * 100) if total_chunks > 0 else 0
            )

            analysis_summary = f"""
Enhanced Sequential Mapping Analysis:
- Total sections evaluated: {len(original_sections)}
- Sections needing optimization: {optimization_count}
- Sections working well: {len(original_sections) - optimization_count}

Ground-truth Processing:
- Document: {file.filename}
- Total chunks processed: {total_chunks}
- Unique chunks mapped: {unique_chunks_mapped}
- Chunk instances mapped: {mapped_chunk_instances} (chunks can map to multiple sections)
- Coverage: {coverage_percentage:.1f}% of document mapped

Mapping Quality:
- High confidence mappings: {confidence_distribution['high']} ({confidence_distribution['high']/total_chunks*100:.1f}%)
- Medium confidence mappings: {confidence_distribution['medium']} ({confidence_distribution['medium']/total_chunks*100:.1f}%)
- Low confidence mappings: {confidence_distribution['low']} ({confidence_distribution['low']/total_chunks*100:.1f}%)

Method: Advanced sequential chunking with context-aware mapping. Each large chunk (up to 100K chars) is intelligently mapped to outline sections using AI analysis with context from previous mapping decisions. This provides structured, flow-aware optimization suggestions based on the actual organization and progression of the reference document.
            """.strip()

            print(
                f"Optimization complete: {optimization_count}/{len(original_sections)} sections optimized"
            )

            return OptimizedOutlineResponse(
                original_sections=original_sections,
                suggestions=suggestions,
                optimized_sections=optimized_sections,
                analysis_summary=analysis_summary,
            )

    except Exception as e:
        print("Error in outline optimization:")
        print(str(e))
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error optimizing outline: {str(e)}"
        )
    finally:
        if disconnect_monitor:
            disconnect_monitor.cancel()
