import uuid
import difflib
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import traceback
import tempfile
import os
import docx
import io
from io import BytesIO
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import markdown
from bs4 import BeautifulSoup
import tiktoken

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
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
    GenerateTopicsRequest,
    GenerateTopicsResponse,
    KnowledgeBase,
    EmbeddingModel,
)
from app.core.config import settings
from app.services.llms import get_default_llm, invoke_llm, record_llm_interaction
from app.services.knowledgebases import get_embedding_model
from app.services.embeddings import load_embeddings_model
from app.services.retrievers import create_ensemble_retriever
from app.services.pdf_utils import load_pdf_with_pypdf

# from langchain_community.document_loaders import PyPDFLoader  # Removed - using pypdf instead
import mimetypes
import logging

# Configure logging for TwinCheck
logger = logging.getLogger(__name__)

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
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail=f"Uploaded file {file.filename} appears to be empty",
            )
        temp_file.write(file_content)
        temp_file_path = temp_file.name
    # File is now closed and ready to be read by other processes

    # Debug: Check file size
    file_size = os.path.getsize(temp_file_path)
    print(f"Temporary file created: {temp_file_path}, size: {file_size} bytes")

    try:
        # Process based on file type
        if content_type == "application/pdf" or file.filename.lower().endswith(".pdf"):
            print("Loading PDF with PyPDF...")
            pages = load_pdf_with_pypdf(temp_file_path, file.filename)
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


# Estimate the number of tokens in a text string.
# Uses tiktoken for accurate token counting.
def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    try:
        # Try to get the encoding for the specific model
        if "gpt-4" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-4")
        elif "gpt-3.5" in model.lower():
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        else:
            # Default to cl100k_base encoding used by most modern models
            encoding = tiktoken.get_encoding("cl100k_base")

        return len(encoding.encode(text))
    except Exception as e:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        print(f"Token estimation error: {e}, using fallback method")
        return len(text) // 4


def chunk_diff_text(diff_text: str, max_tokens: int = None) -> List[str]:
    """
    Split diff text into chunks that don't exceed the token limit.
    Tries to preserve diff context by splitting at natural boundaries.
    """
    if max_tokens is None:
        max_tokens = settings.TWINCHECK_MAX_TOKENS_PER_CHUNK

    if estimate_tokens(diff_text) <= max_tokens:
        return [diff_text]

    chunks = []
    lines = diff_text.split("\n")
    current_chunk = []
    current_tokens = 0

    # Reserve tokens for prompt template and overhead
    chunk_token_limit = max_tokens - settings.TWINCHECK_PROMPT_RESERVE_TOKENS

    for line in lines:
        line_tokens = estimate_tokens(line + "\n")

        # If adding this line would exceed the limit, start a new chunk
        if current_tokens + line_tokens > chunk_token_limit and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_tokens = 0

        current_chunk.append(line)
        current_tokens += line_tokens

    # Add the last chunk if it has content
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def create_synthesis_prompt(
    chunk_results: List[Dict[str, Any]], doc1_name: str, doc2_name: str, topics: str
) -> str:
    """
    Create a prompt for synthesizing multiple chunk analysis results.
    """
    return f"""
    You are synthesizing analysis results from multiple chunks of a document comparison.

    Documents compared:
    - Document 1: {doc1_name}
    - Document 2: {doc2_name}

    Topics of interest: {topics}

    Below are the analysis results from each chunk:

    {"=" * 50}

    {chr(10).join(
        [f"CHUNK {i+1} ANALYSIS:{chr(10)}{result['analysis']}{chr(10)}{chr(10)}"
         for i, result in enumerate(chunk_results)]
    )}

    {"=" * 50}

    Please provide a comprehensive synthesis that:
    1. Combines all the chunk analyses into a coherent overview
    2. Identifies patterns and themes across all chunks
    3. Highlights the most significant differences between the documents
    4. Removes any redundancy or overlap between chunk analyses
    5. Provides clear, actionable insights about the document differences

    Your synthesis should be well-structured and comprehensive while avoiding repetition.
    """


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

        print(f"Generated diff text with {estimate_tokens(diff_text)} estimated tokens")

        # Load the LLM model
        llm = get_default_llm(session, current_user)

        # Parse comparison topics
        topic_list = request.comparison_topics.strip().split("\n")
        topic_analysis = []

        # Check if we need to chunk the diff text
        diff_chunks = chunk_diff_text(diff_text)
        is_chunked = len(diff_chunks) > 1

        print(f"Split diff into {len(diff_chunks)} chunks")

        # Process each topic with the LLM
        for topic in topic_list:
            if not topic.strip():
                continue

            print(f"Processing topic: {topic}")

            if is_chunked:
                # Process each chunk for this topic
                chunk_results = []

                for i, chunk in enumerate(diff_chunks):
                    print(
                        f"  Processing chunk {i+1}/{len(diff_chunks)} for topic: {topic}"
                    )

                    try:
                        chunk_result = invoke_llm(
                            llm,
                            settings.TWINCHECK_ANALYSIS_PROMPT_TEMPLATE,
                            {
                                "diff_text": chunk,
                                "topic": topic,
                                "doc1_name": document1.filename,
                                "doc2_name": document2.filename,
                            },
                        )

                        chunk_results.append(
                            {"chunk_index": i + 1, "analysis": chunk_result}
                        )

                    except Exception as e:
                        chunk_results.append(
                            {
                                "chunk_index": i + 1,
                                "analysis": f"Error analyzing chunk {i+1}: {str(e)}",
                            }
                        )

                # Synthesize the chunk results for this topic
                try:
                    synthesis_prompt = create_synthesis_prompt(
                        chunk_results, document1.filename, document2.filename, topic
                    )

                    print(
                        f"  Synthesizing {len(chunk_results)} chunk results for topic: {topic}"
                    )

                    synthesized_result = invoke_llm(llm, synthesis_prompt, {})

                    topic_analysis.append(
                        {
                            "topic": topic,
                            "analysis": synthesized_result,
                            "chunk_count": len(diff_chunks),
                        }
                    )

                except Exception as e:
                    # Fallback: combine chunk results manually
                    combined_analysis = (
                        f"Analysis from {len(chunk_results)} chunks:\n\n"
                    )
                    for result in chunk_results:
                        combined_analysis += (
                            f"Chunk {result['chunk_index']}:\n{result['analysis']}\n\n"
                        )

                    topic_analysis.append(
                        {
                            "topic": topic,
                            "analysis": combined_analysis,
                            "chunk_count": len(diff_chunks),
                            "synthesis_error": str(e),
                        }
                    )
            else:
                # Single chunk processing (original behavior)
                try:
                    topic_result = invoke_llm(
                        llm,
                        settings.TWINCHECK_ANALYSIS_PROMPT_TEMPLATE,
                        {
                            "diff_text": diff_text,
                            "topic": topic,
                            "doc1_name": document1.filename,
                            "doc2_name": document2.filename,
                        },
                    )

                    topic_analysis.append({"topic": topic, "analysis": topic_result})

                except Exception as e:
                    topic_analysis.append(
                        {
                            "topic": topic,
                            "analysis": f"Error analyzing this topic: {str(e)}",
                        }
                    )

        # Create a comprehensive summary
        if is_chunked:
            # For chunked processing, create summary from topic analyses
            print("Creating summary from topic analyses (chunked mode)")

            topic_summaries = "\n\n".join(
                [f"Topic: {ta['topic']}\n{ta['analysis']}" for ta in topic_analysis]
            )

            summary_prompt = f"""
            You are creating a comprehensive summary of a document comparison that was processed in chunks due to size.
            
            Documents compared:
            - Document 1: {document1.filename}
            - Document 2: {document2.filename}
            
            The comparison was processed in {len(diff_chunks)} chunks and analyzed across the following topics:
            {request.comparison_topics}
            
            Below are the detailed topic analyses:
            
            {topic_summaries}
            
            Please provide a comprehensive executive summary that:
            1. Highlights the most significant overall differences between the documents
            2. Synthesizes patterns across all topic analyses
            3. Provides clear, actionable insights about the document comparison
            4. Is well-structured and avoids repetition
            
            Focus on the big picture and most important differences.
            """

            try:
                summary = invoke_llm(llm, summary_prompt, {})
            except Exception as e:
                summary = f"Summary generation error: {str(e)}\n\nPlease refer to the individual topic analyses below for detailed insights."
        else:
            # Single chunk processing (original behavior)
            print("Creating summary from diff text (single chunk mode)")
            summary = invoke_llm(
                llm,
                settings.TWINCHECK_SUMMARY_PROMPT_TEMPLATE,
                {
                    "diff_text": diff_text,
                    "doc1_name": document1.filename,
                    "doc2_name": document2.filename,
                    "topics": request.comparison_topics,
                },
            )

        # Record this interaction for history
        interaction_id = record_llm_interaction(
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
                    "total_tokens": estimate_tokens(diff_text),
                    "chunk_count": len(diff_chunks),
                    "was_chunked": is_chunked,
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
            "processing_info": {
                "was_chunked": is_chunked,
                "chunk_count": len(diff_chunks),
                "estimated_tokens": estimate_tokens(diff_text),
            },
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


@router.post("/generate-topics", response_model=GenerateTopicsResponse)
def generate_topics(
    session: SessionDep,
    current_user: CurrentUser,
    description: str = Form(...),
    comparison_type: str = Form("general"),
    num_topics: Optional[int] = Form(None),
    search_mode: str = "vector",
    files: List[UploadFile] = File(default=[]),
):
    """
    Generate comparison topics based on a description using LLM, with optional example document.
    """
    print("generate_topics function invoked!")
    print(f"Received search_mode: {search_mode}")
    print(f"Request data: description={description[:50]}...")

    # Validate search mode
    if search_mode not in ["vector", "full_scan"]:
        print(f"Warning: Invalid search mode '{search_mode}', defaulting to 'vector'")
        search_mode = "vector"

    try:
        # Get the default LLM
        llm = get_default_llm(session, current_user)

        # Extract text from example document if provided
        example_document = ""
        example_instruction = ""
        example_analysis_instruction = ""

        if files and len(files) > 0:
            file = files[0]
            if file.size > 0:
                # Reset file pointer to beginning before processing
                file.file.seek(0)
                example_document = extract_text_from_file(file)
                example_instruction = f" and use the uploaded example document ({file.filename}) as a reference for the appropriate scope and depth of comparison topics"
                example_analysis_instruction = f" and explain how they align with the scope shown in the example document ({file.filename})"

        # Prepare variables for the prompt
        prompt_variables = {
            "description": description,
            "comparison_type": comparison_type,
            "example_document": (
                f"EXAMPLE DOCUMENT: {file.filename}\n{example_document}\n"
                if example_document
                else ""
            ),
            "example_instruction": example_instruction,
            "example_analysis_instruction": example_analysis_instruction,
            "knowledge_base_content": "",
            "knowledge_base_instruction": "",
        }

        # Generate topics using the LLM
        topics_response = invoke_llm(
            llm,
            settings.TWINCHECK_GENERATE_TOPICS_PROMPT_TEMPLATE,
            prompt_variables,
        )

        # Parse the response to extract topics and analysis
        topics = []
        analysis = ""

        lines = topics_response.strip().split("\n")
        in_topics_section = False
        in_analysis_section = False

        for line in lines:
            line = line.strip()
            if line.startswith("TOPICS:"):
                in_topics_section = True
                in_analysis_section = False
                continue
            elif line.startswith("ANALYSIS:"):
                in_topics_section = False
                in_analysis_section = True
                continue

            if in_topics_section:
                # Extract topics (numbered list)
                if re.match(r"^\d+\.\s+", line):
                    topic = re.sub(r"^\d+\.\s+", "", line)
                    if topic.strip():
                        topics.append(topic.strip())
            elif in_analysis_section:
                if line:
                    if analysis:
                        analysis += " " + line
                    else:
                        analysis = line

        # If parsing failed, try simpler approach
        if not topics:
            # Split by lines and look for numbered items
            for line in lines:
                line = line.strip()
                if re.match(r"^\d+\.\s+", line):
                    topic = re.sub(r"^\d+\.\s+", "", line)
                    if topic.strip():
                        topics.append(topic.strip())

        # Ensure we have some topics
        if not topics:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate topics from the description. Please try with a more detailed description.",
            )

        # Apply user-specified limit if provided, otherwise use all generated topics
        if num_topics:
            topics = topics[:num_topics]

        if not analysis:
            analysis = f"Generated {len(topics)} comparison topics based on the provided description to ensure comprehensive document comparison coverage."

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="generate_comparison_topics",
            input_data={
                "description": description,
                "requested_topics": num_topics,
                "comparison_type": comparison_type,
                "has_example_document": len(files) > 0 and files[0].size > 0,
                "search_mode": search_mode,
            },
            output_data={
                "topics_count": len(topics),
                "analysis": analysis,
            },
            metadata={},
        )

        return GenerateTopicsResponse(topics=topics, description_analysis=analysis)

    except Exception as e:
        print(f"Error generating topics: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating topics: {str(e)}"
        )


@router.post("/generate-topics-json", response_model=GenerateTopicsResponse)
async def generate_topics_json(
    session: SessionDep, current_user: CurrentUser, request: GenerateTopicsRequest
):
    """
    Generate comparison topics based on a description using LLM, with optional knowledge base reference (JSON version).
    """
    try:
        # Get the default LLM
        llm = get_default_llm(session, current_user)

        # Prepare variables for the prompt
        prompt_variables = {
            "description": request.description,
            "comparison_type": request.comparison_type or "general",
            "example_document": "",
            "example_instruction": "",
            "example_analysis_instruction": "",
            "knowledge_base_instruction": "",
            "knowledge_base_content": "",
        }

        # If knowledge base is specified, retrieve content using selected search mode
        if request.knowledge_base_id:
            try:
                from app.services.content_retrieval import (
                    retrieve_knowledge_base_content,
                )

                content, instruction = await retrieve_knowledge_base_content(
                    session=session,
                    current_user=current_user,
                    knowledge_base_id=request.knowledge_base_id,
                    search_mode=request.search_mode,
                    query=request.description,
                )

                if content:
                    prompt_variables["knowledge_base_content"] = (
                        f"REFERENCE DOCUMENTS FROM KNOWLEDGE BASE:\n{content}"
                    )
                    prompt_variables["knowledge_base_instruction"] = (
                        f"\n12. {instruction} Use them as inspiration for the type of comparison topics and scope, "
                        f"adapting the topics to match the specific requirements in the description. "
                        f"Search mode used: {request.search_mode}"
                    )
                    prompt_variables["example_analysis_instruction"] = (
                        f". Briefly mention how the knowledge base content (using {request.search_mode}) influenced the topic selection"
                    )

            except Exception as e:
                logger.warning(f"Error retrieving from knowledge base: {str(e)}")
                # Continue without knowledge base content rather than failing
                pass

        # Generate topics using the LLM
        topics_response = invoke_llm(
            llm,
            settings.TWINCHECK_GENERATE_TOPICS_PROMPT_TEMPLATE,
            prompt_variables,
        )

        # Parse the response to extract topics and analysis
        topics = []
        analysis = ""

        lines = topics_response.strip().split("\n")
        in_topics_section = False
        in_analysis_section = False

        for line in lines:
            line = line.strip()
            if line.startswith("TOPICS:"):
                in_topics_section = True
                in_analysis_section = False
                continue
            elif line.startswith("ANALYSIS:"):
                in_topics_section = False
                in_analysis_section = True
                continue

            if in_topics_section:
                # Extract topics (numbered list)
                if re.match(r"^\d+\.\s+", line):
                    topic = re.sub(r"^\d+\.\s+", "", line)
                    if topic.strip():
                        topics.append(topic.strip())
            elif in_analysis_section:
                if line:
                    if analysis:
                        analysis += " " + line
                    else:
                        analysis = line

        # If parsing failed, try simpler approach
        if not topics:
            # Split by lines and look for numbered items
            for line in lines:
                line = line.strip()
                if re.match(r"^\d+\.\s+", line):
                    topic = re.sub(r"^\d+\.\s+", "", line)
                    if topic.strip():
                        topics.append(topic.strip())

        # Ensure we have some topics
        if not topics:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate topics from the description. Please try with a more detailed description.",
            )

        # Apply user-specified limit if provided, otherwise use all generated topics
        if request.num_topics:
            topics = topics[: request.num_topics]

        if not analysis:
            search_method = (
                "vector search"
                if request.search_mode == "vector"
                else "full document scan"
            )
            analysis = f"Generated {len(topics)} comparison topics based on the provided description using {search_method}"
            if request.knowledge_base_id:
                analysis += " with knowledge base reference."

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="generate_topics",
            input_data={
                "description": request.description,
                "comparison_type": request.comparison_type,
                "requested_topics": request.num_topics,
                "knowledge_base_id": request.knowledge_base_id,
                "search_mode": request.search_mode,
            },
            output_data={
                "topics_count": len(topics),
                "analysis": analysis,
            },
            metadata={},
        )

        return GenerateTopicsResponse(topics=topics, description_analysis=analysis)

    except Exception as e:
        logger.error(f"Error generating topics: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating topics: {str(e)}"
        )
