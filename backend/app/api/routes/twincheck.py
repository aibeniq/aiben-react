import uuid
import difflib
from typing import List, Dict, Any
from datetime import datetime
import json
import traceback
import tempfile
import os
import docx
import io
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import markdown
from bs4 import BeautifulSoup

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    TwinCheckRequest,
    TwinCheckResponse,
    TwinCheckTopicList,
    TwinCheckDetailResponse,
    LlmInteraction,
    DocxRequest,
    Message,
)
from app.core.config import settings
from app.services.llms import LlmService
from langchain_community.document_loaders import PyPDFLoader
import mimetypes

router = APIRouter(prefix="/twincheck", tags=["twincheck"])


def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from uploaded files based on their type.
    Supports PDF, DOCX, and plain text files.
    """
    content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
    print(f"Processing file: {file.filename} with content type: {content_type}")

    # Create a temporary file to store the content
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=f"_{file.filename}"
    ) as temp_file:
        # Read the file content and write to temp file
        file_content = file.file.read()
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    try:
        # Process based on file type
        if content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
            print("Loading PDF with PyPDFLoader...")
            loader = PyPDFLoader(temp_file_path)
            pages = loader.load()
            # Combine all page contents
            text = "\n\n".join([page.page_content for page in pages])

        elif (
            content_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            or file.filename.lower().endswith(".docx")
        ):
            print("Loading DOCX with python-docx library...")
            doc = docx.Document(temp_file_path)

            # Extract text from paragraphs
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]

            # Extract text from tables
            tables_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        tables_text.append(" | ".join(row_text))

            # Combine all text
            text = "\n\n".join(paragraphs + tables_text)

        else:
            # Assume it's a text file
            print("Loading as text file...")
            # Try with different encodings
            try:
                with open(temp_file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(temp_file_path, "r", encoding="latin-1") as f:
                    text = f.read()

        return text

    except Exception as e:
        print(f"Error processing file {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Error processing file {file.filename}: {str(e)}"
        )
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


# Process documents for comparison
@router.post("/compare", response_model=TwinCheckResponse)
async def compare_documents(
    session: SessionDep,
    current_user: CurrentUser,
    request: TwinCheckRequest = Depends(),
    document1: UploadFile = File(...),
    document2: UploadFile = File(...),
):
    """
    Compare two documents based on the provided comparison topics.
    Supports PDF, DOCX, and plain text files.
    """
    try:
        # Reset file pointers (in case they were read elsewhere)
        document1.file.seek(0)
        document2.file.seek(0)

        # Extract text from both documents
        doc1_text = extract_text_from_file(document1)

        # Reset file pointer for document2
        document2.file.seek(0)
        doc2_text = extract_text_from_file(document2)

        # Split files into lines for diffing
        doc1_lines = doc1_text.splitlines()
        doc2_lines = doc2_text.splitlines()

        # Generate diff using difflib
        differ = difflib.Differ()
        diff_result = list(differ.compare(doc1_lines, doc2_lines))
        diff_text = "\n".join(diff_result)

        # Load the LLM model
        llm_info = LlmService.get_user_default_model(session, current_user.id)
        llm = LlmService.get_model(llm_info.id)

        # Parse comparison topics
        topic_list = request.comparison_topics.strip().split("\n")
        topic_analysis = []

        # Process each topic with the LLM
        for topic in topic_list:
            if not topic.strip():
                continue

            # Define prompt template for topic analysis
            prompt_template = settings.TWINCHECK_ANALYSIS_PROMPT_TEMPLATE

            # Generate analysis for this topic
            try:
                topic_result = llm.invoke(
                    prompt_template,
                    {
                        "diff_text": diff_text,
                        "topic": topic,
                        "doc1_name": document1.filename,
                        "doc2_name": document2.filename,
                    },
                )

                # Add to results
                topic_analysis.append({"topic": topic, "analysis": topic_result})

            except Exception as e:
                topic_analysis.append(
                    {
                        "topic": topic,
                        "analysis": f"Error analyzing this topic: {str(e)}",
                    }
                )

        # Create a comprehensive summary
        summary_prompt_template = settings.TWINCHECK_SUMMARY_PROMPT_TEMPLATE
        summary = llm.invoke(
            summary_prompt_template,
            {
                "diff_text": diff_text,
                "doc1_name": document1.filename,
                "doc2_name": document2.filename,
                "topics": request.comparison_topics,
            },
        )

        # Record this interaction for history
        interaction_id = LlmService.record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="twincheck",
            input_data={
                "comparison_topics": request.comparison_topics,
                "document1_name": document1.filename,
                "document2_name": document2.filename,
            },
            output_data={"summary": summary, "topic_count": len(topic_analysis)},
            metadata={
                "topic_analysis": topic_analysis,  # Store detailed analysis for retrieval
                "diff_stats": {
                    "additions": diff_text.count("\n+ "),
                    "deletions": diff_text.count("\n- "),
                    "changes": diff_text.count("\n? "),
                },
            },
        )

        # Return the results
        result = {
            "summary": summary,
            "topic_analysis": topic_analysis,
            "interaction_id": str(interaction_id) if interaction_id else None,
        }

        return TwinCheckResponse(results=result)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error comparing documents: {str(e)}"
        )


# Get history of comparison operations
@router.get("/history", response_model=List[Dict[str, Any]])
async def get_comparison_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
    show_all: bool = False,
):
    """Retrieve past document comparison history for the current user or all users."""
    print("Retrieving TwinCheck history. Show all:", show_all)

    try:
        # Start with base query
        query = select(LlmInteraction).where(
            LlmInteraction.functionality == "twincheck"
        )

        # Only filter by user if not showing all users
        if not show_all:
            query = query.where(LlmInteraction.user_id == current_user.id)

        # Add ordering and pagination
        comparisons = session.exec(
            query.order_by(LlmInteraction.date_created.desc()).offset(skip).limit(limit)
        ).all()

        result = []
        for comparison in comparisons:
            try:
                input_data = (
                    json.loads(comparison.input_data) if comparison.input_data else {}
                )
                output_data = (
                    json.loads(comparison.output_data) if comparison.output_data else {}
                )

                # Create result item
                result_item = {
                    "id": str(comparison.id),
                    "date_created": comparison.date_created,
                    "document1_name": input_data.get(
                        "document1_name", "Unknown Document 1"
                    ),
                    "document2_name": input_data.get(
                        "document2_name", "Unknown Document 2"
                    ),
                    "comparison_topics": input_data.get("comparison_topics", ""),
                    "topic_count": output_data.get("topic_count", 0),
                    "has_feedback": comparison.feedback is not None,
                }

                # Add feedback information if exists
                if comparison.feedback:
                    result_item["feedback"] = {
                        "feedback": comparison.feedback,
                        "feedbackText": comparison.feedback_text,
                    }

                # Add user info for all-users view
                if show_all:
                    from app.models import User  # Import here to avoid circular imports

                    user = session.get(User, comparison.user_id)
                    user_name = (
                        f"{user.full_name or 'User'} ({user.email})"
                        if user
                        else "Unknown User"
                    )
                    result_item["user_name"] = user_name

                result.append(result_item)
            except json.JSONDecodeError:
                # If JSON parsing fails, use minimal information
                # Create result item with minimal info
                result_item = {
                    "id": str(comparison.id),
                    "date_created": comparison.date_created,
                    "document1_name": "Unknown Document 1",
                    "document2_name": "Unknown Document 2",
                    "topic_count": 0,
                    "has_feedback": comparison.feedback is not None,
                }

                # Add feedback information if exists
                if comparison.feedback:
                    result_item["feedback"] = {
                        "feedback": comparison.feedback,
                        "feedbackText": comparison.feedback_text,
                    }

                # Add user info for all-users view
                if show_all:
                    from app.models import User  # Import here to avoid circular imports

                    user = session.get(User, comparison.user_id)
                    user_name = (
                        f"{user.full_name or 'User'} ({user.email})"
                        if user
                        else "Unknown User"
                    )
                    result_item["user_name"] = user_name

                result.append(result_item)

        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving comparison history: {str(e)}"
        )


# Get details of a specific comparison
@router.get("/history/{comparison_id}", response_model=TwinCheckDetailResponse)
async def get_comparison_detail(
    comparison_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Retrieve a specific comparison's full content by ID."""
    try:
        comparison = session.get(LlmInteraction, comparison_id)
        if not comparison:
            raise HTTPException(status_code=404, detail="Comparison not found")

        # No longer need to check this since we now allow viewing others' outputs
        # if comparison.user_id != current_user.id:
        #    raise HTTPException(
        #        status_code=403, detail="You don't have access to this comparison"
        #    )

        if comparison.functionality != "twincheck":
            raise HTTPException(
                status_code=400, detail="This is not a TwinCheck comparison"
            )

        try:
            input_data = (
                json.loads(comparison.input_data) if comparison.input_data else {}
            )
            output_data = (
                json.loads(comparison.output_data) if comparison.output_data else {}
            )
            extra_data = comparison.extra_data or {}

            # Create a response that matches the structure expected by the frontend
            result = {
                "id": str(comparison.id),
                "date_created": comparison.date_created,
                "document1_name": input_data.get(
                    "document1_name", "Unknown Document 1"
                ),
                "document2_name": input_data.get(
                    "document2_name", "Unknown Document 2"
                ),
                "comparison_topics": input_data.get("comparison_topics", ""),
                "results": {
                    "summary": output_data.get("summary", ""),
                    "topic_analysis": extra_data.get("topic_analysis", []),
                    "interaction_id": str(comparison.id),
                },
                # Add feedback information
                "feedback": {
                    "feedback": comparison.feedback,
                    "feedbackText": comparison.feedback_text,
                    "feedbackDate": (
                        comparison.feedback_date.isoformat()
                        if comparison.feedback_date
                        else None
                    ),
                },
            }

            return result

        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "id": str(comparison.id),
                "date_created": comparison.date_created,
                "document1_name": "Unknown Document 1",
                "document2_name": "Unknown Document 2",
                "results": {
                    "summary": "Unable to reconstruct comparison from this record. This might be due to an older format or incomplete data.",
                    "topic_analysis": [],
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
            status_code=500, detail=f"Error retrieving comparison details: {str(e)}"
        )


# Functions related to Comparisons (saved comparison topics)
@router.post("/comparisons", response_model=TwinCheckTopicList)
def create_comparison(
    comparison: TwinCheckTopicList, session: SessionDep, current_user: CurrentUser
):
    """
    Save a new comparison topic set to the database.
    """
    existing_comparison = session.exec(
        select(TwinCheckTopicList).where(TwinCheckTopicList.name == comparison.name)
    ).first()

    if existing_comparison:
        raise HTTPException(
            status_code=400, detail="A comparison with this name already exists."
        )

    comparison.owner_id = current_user.id
    session.add(comparison)
    session.commit()
    session.refresh(comparison)
    return comparison


@router.get("/comparisons", response_model=List[TwinCheckTopicList])
def get_comparisons(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve all saved comparison topic sets from the database for this user.
    """
    return session.exec(
        select(TwinCheckTopicList).where(TwinCheckTopicList.owner_id == current_user.id)
    ).all()


@router.get("/comparisons/{comparison_id}", response_model=TwinCheckTopicList)
def get_comparison(comparison_id: uuid.UUID, session: SessionDep):
    """
    Retrieve a specific comparison topic set by ID.
    """
    comparison = session.get(TwinCheckTopicList, comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found.")
    return comparison


@router.put("/comparisons/{comparison_id}", response_model=TwinCheckTopicList)
def update_comparison(
    comparison_id: uuid.UUID,
    updated_comparison: TwinCheckTopicList,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Update an existing comparison topic set.
    """
    comparison = session.get(TwinCheckTopicList, comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found.")

    # Ensure the current user is the owner of the comparison
    if comparison.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this comparison."
        )

    comparison.name = updated_comparison.name
    comparison.description = updated_comparison.description
    comparison.topics = updated_comparison.topics
    comparison.date_modified = datetime.utcnow()

    session.add(comparison)
    session.commit()
    session.refresh(comparison)
    return comparison


@router.delete("/comparisons/{comparison_id}", response_model=Message)
def delete_comparison(
    comparison_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
):
    """
    Delete a comparison topic set by ID.
    """
    comparison = session.get(TwinCheckTopicList, comparison_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found.")

    # Ensure the current user is the owner of the comparison
    if comparison.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this comparison."
        )

    session.delete(comparison)
    session.commit()
    return Message(message="Comparison deleted successfully.")


@router.post("/generate/docx", response_class=StreamingResponse)
async def generate_docx(
    session: SessionDep, current_user: CurrentUser, request: DocxRequest
):
    """
    Generate a DOCX file from the comparison content.
    """
    print("Now generating DOCX of comparison...")
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
        title_text = (
            request.title
            if hasattr(request, "title") and request.title
            else "Document Comparison"
        )
        title = doc.add_heading(title_text, level=0)
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
        filename = f"comparison_{timestamp}.docx"

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
