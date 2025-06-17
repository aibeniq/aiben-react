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
)
from pathlib import Path
import re
import tempfile
import zipfile
import json
import traceback
from io import BytesIO
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

from sqlmodel import select
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from langchain_community.vectorstores import Chroma

router = APIRouter(prefix="/reportgenie", tags=["reportgenie"])


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

        # 2. Create a temporary directory for ChromaDB
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zipped ChromaDB into the temp directory
            if kb.data:
                with zipfile.ZipFile(BytesIO(kb.data), "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            else:
                raise HTTPException(
                    status_code=400, detail="Knowledge base has no vector database data"
                )

            # 3. Load the vector database with the same model used to create the KB
            if kb.embedding_model_id:
                embedding_model = session.get(EmbeddingModel, kb.embedding_model_id)
                if embedding_model:
                    model_id = embedding_model.model_id
                    provider = embedding_model.provider
                    print(
                        f"Using knowledge base's original embedding model: {model_id}"
                    )
                else:
                    embedding_info = get_embedding_model(session, current_user)
                    model_id = embedding_info["model_id"]
                    provider = embedding_info["provider"]
            else:
                embedding_info = get_embedding_model(session, current_user)
                model_id = embedding_info["model_id"]
                provider = embedding_info["provider"]

            print(f"Initializing embedding model: {model_id} ({provider})")
            embeddings = load_embeddings_model(provider=provider, model_id=model_id)
            chroma_db = Chroma(
                persist_directory=temp_dir, embedding_function=embeddings
            )
            retriever = chroma_db.as_retriever(search_kwargs={"k": 5})

            # 4. Initialize the LLM
            llm = get_default_llm(session, current_user)

            # 5. Parse the sections outline
            section_list = request.sections.strip().split("\n")

            # 6. Process each section
            sections = []

            for section_description in section_list:
                section_description = section_description.strip()
                if not section_description:
                    continue

                # Retrieve relevant context from the knowledge base
                docs = retriever.get_relevant_documents(section_description)
                context = "\n\n".join([doc.page_content for doc in docs])

                # Store source documents for citation
                source_citations = []
                for doc in docs:
                    metadata = doc.metadata.copy()

                    if "source" in metadata and isinstance(metadata["source"], str):
                        source_path = metadata["source"]
                        raw_filename = Path(source_path).name

                        # Extract the real filename after the underscore using regex
                        match = re.search(r"^[^_]*_(.+)$", raw_filename)
                        if match:
                            filename = match.group(1)
                        else:
                            filename = raw_filename

                        source_entry = session.exec(
                            select(Source).where(Source.name == filename)
                        ).first()

                        if source_entry:
                            metadata["source_data_id"] = str(
                                source_entry.source_data_id
                            )

                    source = {"content": doc.page_content, "metadata": metadata}
                    source_citations.append(source)

                # Use the template from config
                prompt_template = settings.REPORT_GENIE_PROMPT_TEMPLATE

                section_content = invoke_llm(
                    llm,
                    prompt_template,
                    {"context": context, "question": section_description},
                )

                # Store the section with its content and sources
                sections.append(
                    {
                        "title": section_description,
                        "content": section_content,
                        "source_citations": source_citations,
                    }
                )

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
                    outline_name = first_line[:30] + (
                        "..." if len(first_line) > 30 else ""
                    )
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
            raise HTTPException(status_code=400, detail="Report content is required")

        # Convert markdown to HTML for parsing
        html_content = markdown.markdown(request.content, extensions=["tables"])
        soup = BeautifulSoup(html_content, "html.parser")

        print("Markdown content converted to HTML successfully.")
        # Create a new Document
        doc = Document()

        print("Adding title and date to the document...")
        # Add a title
        title = doc.add_heading("Generated Report", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add date
        date_paragraph = doc.add_paragraph()
        date_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        date_run = date_paragraph.add_run(
            f"Generated on: {datetime.now().strftime('%B %d, %Y')}"
        )
        date_run.italic = True

        # Add a separator
        doc.add_paragraph("─" * 50)

        print("Adding headers, paragraphs, lists, and tables...")
        # Process all headers and paragraphs in the HTML
        for element in soup.find_all(
            ["h1", "h2", "h3", "h4", "p", "ul", "ol", "li", "table"]
        ):
            if element.name == "h1":
                doc.add_heading(element.text, level=1)
            elif element.name == "h2":
                doc.add_heading(element.text, level=2)
            elif element.name == "h3":
                doc.add_heading(element.text, level=3)
            elif element.name == "p":
                doc.add_paragraph(element.text)
            elif element.name == "ul":
                for li in element.find_all("li"):
                    paragraph = doc.add_paragraph(li.text)
                    paragraph.style = "List Bullet"
            elif element.name == "ol":
                for li in element.find_all("li"):
                    paragraph = doc.add_paragraph(li.text)
                    paragraph.style = "List Number"
            elif element.name == "table":
                table_rows = element.find_all("tr")
                if table_rows:
                    # Count the number of columns in the first row
                    first_row = table_rows[0]
                    columns = len(first_row.find_all(["th", "td"]))

                    # Create the table
                    table = doc.add_table(rows=0, cols=columns)
                    table.style = "Table Grid"

                    # Process header row
                    header_cells = first_row.find_all(["th", "td"])
                    if header_cells:
                        header_row = table.add_row().cells
                        for i, cell in enumerate(header_cells):
                            if i < len(header_row):
                                header_row[i].text = cell.text
                                run = header_row[i].paragraphs[0].runs[0]
                                run.bold = True

                    # Process data rows
                    for row in table_rows[1:]:
                        cells = row.find_all("td")
                        if cells:
                            row_cells = table.add_row().cells
                            for i, cell in enumerate(cells):
                                if i < len(row_cells):
                                    row_cells[i].text = cell.text

        # Save the document to a BytesIO object
        print("Saving the document to a BytesIO object...")
        docx_bytes = BytesIO()
        doc.save(docx_bytes)
        docx_bytes.seek(0)

        # --- CORRUPTION CHECKS ---
        # 1. Check file size
        size = docx_bytes.getbuffer().nbytes
        print(f"DOCX file size: {size} bytes")
        if size < 1000:
            print("Warning: DOCX file is very small and may be empty or corrupted.")

        # 2. Try to reload the DOCX to ensure it's readable
        try:
            docx_bytes.seek(0)
            _ = Document(docx_bytes)
            print("DOCX file passed integrity check (can be opened by python-docx).")
        except Exception as e:
            print(
                f"Integrity check failed: generated DOCX cannot be opened. Error: {e}"
            )
            raise HTTPException(
                status_code=500, detail="Generated DOCX file is corrupted."
            )

        docx_bytes.seek(0)

        print(
            "Document saved successfully. Preparing to return as a downloadable file."
        )

        # Create a filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.docx"

        # Return the document as a downloadable file
        return StreamingResponse(
            docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating DOCX: {str(e)}")


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
