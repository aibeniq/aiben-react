import uuid
from app.models import (
    ReportGenieRequest,
    ReportGenieResponse,
    ReportGenieOutline,
    ReportGenieDetailResponse,
    KnowledgeBase,
    DocxRequest,
    ToolInteraction,
    Message,
)
import json
import traceback
import uuid
from datetime import datetime
from io import BytesIO
from datetime import datetime
from io import BytesIO
from typing import Any

import markdown
from bs4 import BeautifulSoup
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.prompts import PromptTemplate
from sqlmodel import desc, select

from app.api.deps import CurrentUser, SessionDep, VectorDBDep
from app.core.config import settings
from app.models import (
    DocxRequest,
    KnowledgeBase,
    ToolInteraction,
    Tool,
    Message,
    ReportGenieDetailFeedback,
    ReportGenieDetailResponse,
    ReportGenieDetailResults,
    ReportGenieOutline,
    ReportGenieRequest,
    ReportGenieResponse,
    ReportGenieResults,
    ReportGenieSection,
    ReportGenieSourceCitation,
    ReportGenieSourceMetadata,
)
from app.services.embeddings import EmbeddingService
from app.services.llms.main import LlmService
from app.services.vectordb.types import VectorDBError

from sqlmodel import select
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

router = APIRouter(prefix="/reportgenie", tags=["reportgenie"])


@router.post("/generate", response_model=ReportGenieResponse)
async def generate_report(
    session: SessionDep,
    current_user: CurrentUser,
    vectordb_service: VectorDBDep,
    request: ReportGenieRequest = Depends(),
) -> ReportGenieResponse:
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

        # get embedding model info for the knowledge base
        if kb.embedding_model_id:
            if EmbeddingService.is_valid_model_id(kb.embedding_model_id):
                embedding_model = EmbeddingService.get_model_spec(kb.embedding_model_id)
                if not embedding_model:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Knowledge base has an invalid embedding model {kb.embedding_model_id}",
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Knowledge base has an invalid embedding model {kb.embedding_model_id}",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Knowledge base has no embedding model",
            )

        # 4. Initialize the LLM
        llm_info = LlmService.get_user_default_model_spec(session, current_user.id)
        llm = LlmService.get_model(llm_info.id)

        # 5. Parse the sections outline
        section_list = request.sections.strip().split("\n")

        # 6. Process each section
        sections: list[ReportGenieSection] = []

        for section_description in section_list:
            section_description = section_description.strip()
            if not section_description:
                continue

            # search for relevant chunks
            try:
                search_result = vectordb_service.search_hybrid(
                    query=section_description,
                    embedding_model_id=embedding_model.id,
                    knowledge_base_id=str(kb.id),
                    limit=5,
                    output_fields=["content", "source_id", "title", "author", "url"],
                    alpha=0.7,
                )
            except VectorDBError as e:
                print(f"Search failed for section '{section_description}': {str(e)}")
                continue

            chunks = search_result.hits
            context = "\n\n".join([chunk.entity.content for chunk in chunks])

            # process source documents for citation
            source_citations: list[ReportGenieSourceCitation] = []
            for chunk in chunks:
                metadata = ReportGenieSourceMetadata(
                    source_id=chunk.entity.source_id,
                    url=chunk.entity.url,
                    title=chunk.entity.title,
                    author=chunk.entity.author,
                )

                source_citation = ReportGenieSourceCitation(
                    content=chunk.entity.content, metadata=metadata
                )
                source_citations.append(source_citation)

            # use the template from config
            prompt_template = PromptTemplate.from_template(
                settings.REPORT_GENIE_PROMPT_TEMPLATE
            )
            variables = {"context": context, "question": section_description}
            prompt = prompt_template.invoke(variables)
            section = llm.invoke(prompt)
            print(f"Got response: {section.content[:50]}...")

            # store the section with its content and sources
            if isinstance(section.content, str):
                sections.append(
                    ReportGenieSection(
                        title=section_description,
                        content=section.content,
                        source_citations=source_citations,
                    )
                )
            else:
                print(f"Warning: Section content is not a string: {section.content}")
                continue

        # 7. Compile the final report
        full_report = "\n\n---\n\n".join(
            [section.content.strip() for section in sections]
        )

        result = ReportGenieResults(full_report=full_report, sections=sections)

        # get outline name if outline_id is provided
        outline_name = None
        if hasattr(request, "outline_id") and request.outline_id:
            try:
                outline = session.get(ReportGenieOutline, request.outline_id)
                if outline:
                    outline_name = outline.name
            except Exception as e:
                print(f"Warning: Error retrieving outline name: {e}")

        # if no outline_id but we have sections, use first line or "Custom Outline"
        if not outline_name and request.sections:
            first_line = request.sections.strip().split("\n")[0]
            if first_line:
                # extract a name from the first section (limited to 30 chars)
                outline_name = first_line[:30] + ("..." if len(first_line) > 30 else "")
            else:
                outline_name = "Custom Outline"

        # store the full report and sections data in extra_data for retrieval later
        detailed_extra_data = {
            "kb_name": kb.title,
            "full_report": full_report,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "source_citations": [
                        {
                            "content": citation.content,
                            "metadata": citation.metadata.model_dump(),
                        }
                        for citation in section.source_citations
                    ],
                }
                for section in sections
            ],
            "outline_name": outline_name,  # add the outline name here
        }

        LlmService.record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality=Tool.REPORTGENIE,
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
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating report: {str(e)}"
        )


# Functions related to Outlines
@router.post("/outlines", response_model=ReportGenieOutline)
def create_outline(
    outline: ReportGenieOutline, session: SessionDep, current_user: CurrentUser
) -> ReportGenieOutline:
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


@router.get("/outlines", response_model=list[ReportGenieOutline])
def get_outlines(
    session: SessionDep, current_user: CurrentUser
) -> list[ReportGenieOutline]:
    """
    Retrieve all outlines from the database for this user.
    """
    print(f"Retrieving outlines for user {current_user.id}")

    try:
        outlines = list(
            session.exec(
                select(ReportGenieOutline).where(
                    ReportGenieOutline.owner_id == current_user.id
                )
            )
        )

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
def get_outline(outline_id: uuid.UUID, session: SessionDep) -> ReportGenieOutline:
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
) -> ReportGenieOutline:
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
) -> Message:
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
async def generate_docx(request: DocxRequest) -> StreamingResponse:
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


@router.get("/history", response_model=list[dict[str, Any]])
async def get_report_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
    show_all: bool = False,
) -> list[dict[str, Any]]:
    """Retrieve past report generation history for the current user or all users."""
    print("Retrieving report history. Show all:", show_all)

    try:
        # Start with base query
        query = select(ToolInteraction).where(
            ToolInteraction.functionality == Tool.REPORTGENIE
        )

        # Only filter by user if not showing all users
        if not show_all:
            query = query.where(ToolInteraction.user_id == current_user.id)

        # Add ordering and pagination
        reports = session.exec(
            query.order_by(ToolInteraction.date_created.desc())
            .offset(skip)
            .limit(limit)
        ).all()

        print(f"Found {len(reports)} reports for user {current_user.id}:")

        result = []
        for report in reports:
            # Parse the input_data and output_data from string to dict if possible
            try:
                input_data = json.loads(report.input_data) if report.input_data else {}
                output_data = (
                    json.loads(report.output_data) if report.output_data else {}
                )

                # Use validation method for better type safety
                if report.is_valid_reportgenie_data():
                    # Get typed extra data
                    _, typed_extra_data = report.validate_reportgenie_data()
                    if typed_extra_data:
                        kb_name = typed_extra_data.kb_name or "Unknown Knowledge Base"
                        outline_name = typed_extra_data.outline_name or ""
                    else:
                        kb_name = "Unknown Knowledge Base"
                        outline_name = ""
                else:
                    # Fallback to raw data if validation fails
                    extra_data = report.extra_data or {}
                    kb_name = extra_data.get("kb_name", "Unknown Knowledge Base")
                    outline_name = extra_data.get("outline_name", "")

                # Create a user-friendly title
                title = f"Report on {kb_name}"

                # Create the result item
                result_item = {
                    "id": str(report.id),
                    "date_created": report.date_created,
                    "title": title,
                    "sections": input_data.get("sections", ""),
                    "kb_id": input_data.get("kb_id", ""),
                    "section_count": output_data.get("section_count", 0),
                    "kb_name": kb_name,
                    "outline_name": outline_name,
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
) -> ReportGenieDetailResponse:
    """Retrieve a specific report's full content by ID."""
    try:
        tool_interaction = session.get(ToolInteraction, report_id)
        if not tool_interaction:
            raise HTTPException(status_code=404, detail="Report not found")

        # Because we now allow viewing others' outputs, no longer need to ensure this
        # if report.user_id != current_user.id:
        #    raise HTTPException(
        #        status_code=403, detail="You don't have access to this report"
        #    )

        if tool_interaction.functionality != Tool.REPORTGENIE:
            raise HTTPException(
                status_code=400, detail="This is not a ReportGenie report"
            )

        # Validate ReportGenie extra data using new validation methods
        is_valid, typed_extra_data = tool_interaction.validate_reportgenie_data()

        if not is_valid or not typed_extra_data:
            # Fallback if validation fails
            return ReportGenieDetailResponse(
                id=str(tool_interaction.id),
                date_created=tool_interaction.date_created,
                kb_name="Unknown Knowledge Base",
                kb_id="",
                sections="",
                results=ReportGenieDetailResults(
                    full_report=f"Unable to reconstruct report from {tool_interaction.date_created}.\n\n"
                    f"This might be due to corrupted or incomplete data.",
                    sections=[],
                ),
                feedback=ReportGenieDetailFeedback(
                    feedback=tool_interaction.feedback,
                    feedbackText=tool_interaction.feedback_text,
                    feedbackDate=(
                        tool_interaction.feedback_date.isoformat()
                        if tool_interaction.feedback_date
                        else None
                    ),
                ),
            )

        # Try to reconstruct the original report structure
        try:
            input_data = (
                json.loads(tool_interaction.input_data)
                if tool_interaction.input_data
                else {}
            )

            # Use validated typed data instead of raw extra_data
            kb_name = typed_extra_data.kb_name or "Unknown Knowledge Base"
            full_report = typed_extra_data.full_report or ""

            # Reconstruct sections with proper typing
            sections_data = (
                json.loads(typed_extra_data.sections)
                if typed_extra_data.sections
                else []
            )
            reconstructed_sections = []
            for section_data in sections_data:
                source_citations = []
                for citation_data in section_data.get("source_citations", []):
                    metadata_data = citation_data.get("metadata", {})
                    metadata = ReportGenieSourceMetadata(
                        source_id=metadata_data.get("source_id", ""),
                        title=metadata_data.get("title", ""),
                        author=metadata_data.get("author", ""),
                        url=metadata_data.get("url", ""),
                    )
                    citation = ReportGenieSourceCitation(
                        content=citation_data.get("content", ""),
                        metadata=metadata,
                    )
                    source_citations.append(citation)

                section = ReportGenieSection(
                    title=section_data.get("title", ""),
                    content=section_data.get("content", ""),
                    source_citations=source_citations,
                )
                reconstructed_sections.append(section)

            # Create a response that matches the structure expected by the frontend
            result = ReportGenieDetailResponse(
                id=str(tool_interaction.id),
                date_created=tool_interaction.date_created,
                kb_name=kb_name,
                kb_id=typed_extra_data.kb_id or input_data.get("kb_id", ""),
                sections=input_data.get("sections", ""),
                results=ReportGenieDetailResults(
                    full_report=full_report,
                    sections=reconstructed_sections,
                ),
                # Add feedback information
                feedback=ReportGenieDetailFeedback(
                    feedback=tool_interaction.feedback,
                    feedbackText=tool_interaction.feedback_text,
                    feedbackDate=(
                        tool_interaction.feedback_date.isoformat()
                        if tool_interaction.feedback_date
                        else None
                    ),
                ),
            )

            return result

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return ReportGenieDetailResponse(
                id=str(tool_interaction.id),
                date_created=tool_interaction.date_created,
                kb_name=typed_extra_data.kb_name or "Unknown Knowledge Base",
                kb_id=typed_extra_data.kb_id or "",
                sections="",
                results=ReportGenieDetailResults(
                    full_report=f"Unable to reconstruct report from {tool_interaction.date_created}.\n\n"
                    f"This might be due to an older format or incomplete data.",
                    sections=[],
                ),
                # Add feedback object for consistency
                feedback=ReportGenieDetailFeedback(
                    feedback=tool_interaction.feedback,
                    feedbackText=tool_interaction.feedback_text,
                    feedbackDate=(
                        tool_interaction.feedback_date.isoformat()
                        if tool_interaction.feedback_date
                        else None
                    ),
                ),
            )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving report details: {str(e)}"
        )
