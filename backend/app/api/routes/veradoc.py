import uuid
from app.models import (
    VeraDocResponse,
    VeraDocChecklist,
    RagChecklistRequest,
    KnowledgeBase,
    LlmInteraction,
    DocxRequest,
    VeraDocDetailResponse,
    Message,
    User,
)

from app.api.deps import CurrentUser, SessionDep, VectorDBDep
from app.core.config import settings
from app.services.llms.main import LlmService

from sqlmodel import select
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Depends,
    Request as FastAPIRequest,
)
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
import asyncio
from dotenv import load_dotenv
import json
import os

from datetime import datetime
import traceback
from io import BytesIO
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import markdown
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv(dotenv_path="c:/miniconda/aibeniq-react/.env", override=False)

# Retrieve the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize a flag to track API key status
is_openai_configured = False

if openai_api_key:
    # Set up OpenAI API key if available
    os.environ["OPENAI_API_KEY"] = openai_api_key
    is_openai_configured = True
    print("OpenAI API key configured successfully")
else:
    print(
        "WARNING: OPENAI_API_KEY is not set in environment variables. Some FormConnect features will be limited."
    )

router = APIRouter(prefix="/veradoc", tags=["veradoc"])

# Initialize the LLM
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)


def generate_template(questions: List[str]) -> Dict[str, str]:
    """
    Generate a JSON template from a list of questions.
    Each field will have a blank value.
    """
    return {field: "" for field in questions}


# Add the new endpoint
@router.post("/process-rag", response_model=VeraDocResponse)
async def process_rag_checklist(
    session: SessionDep,
    current_user: CurrentUser,
    vectordb_service: VectorDBDep,
    request_data: RagChecklistRequest = Depends(),
    files: List[UploadFile] = File(...),
    handwritten_files: List[UploadFile] = File(None),
    request: FastAPIRequest = None,
):
    """
    Process the uploaded files using RAG with a knowledge base.
    """
    print("process_rag_checklist function invoked!")
    # Create a cancellation flag
    cancellation_requested = False

    try:
        print("Setting up disconnect monitor for VeraDoc RAG processing...")
        # Create a monitor task but don't wait for it
        disconnect_monitor = None
        if request:

            async def monitor_client_disconnect():
                nonlocal cancellation_requested
                try:
                    # Don't create a separate task - just await directly
                    # This is fine because this whole function runs as a background task
                    await request.is_disconnected()

                    # This only executes after client disconnects
                    print("Client disconnected, canceling operation...")
                    cancellation_requested = True
                except asyncio.CancelledError:
                    print("Disconnect monitor cancelled because main task completed")
                except Exception as e:
                    print(f"Error in disconnect monitoring: {str(e)}")

            # Start monitoring in background without blocking
            disconnect_monitor = asyncio.create_task(monitor_client_disconnect())

        print("Processing RAG checklist...")

        # 1. Retrieve knowledge base from database
        kb = session.get(KnowledgeBase, request_data.knowledge_base_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        if kb.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You don't have access to this knowledge base"
            )

        # 2. Get embedding model info for the knowledge base
        if kb.embedding_model_id:
            from app.services.embeddings import EmbeddingService

            if EmbeddingService.is_valid_model_id(kb.embedding_model_id):
                embedding_model = EmbeddingService.get_model_spec(kb.embedding_model_id)
                print(f"Using embedding model: {kb.embedding_model_id}")
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Knowledge base has an invalid embedding model",
                )
        else:
            # For knowledge bases created before tracking embedding models
            raise HTTPException(
                status_code=400,
                detail="Knowledge base has no embedding model",
            )

        # 3. Initialize the LLM
        llm = LlmService.get_user_default_model(session, current_user.id)
        print("LLM successfully loaded")

        # 4. Define the prompts for the different stages
        context_prompt_template = settings.VERADOC_CONTEXT_PROMPT_TEMPLATE
        qa_prompt_template = settings.VERADOC_QA_PROMPT_TEMPLATE
        final_prompt_template = settings.VERADOC_FINAL_PROMPT_TEMPLATE

        # 5. Process each uploaded file
        qa_pairs = []
        question_list = request_data.questions.strip().split("\n")

        # Get file content
        file = files[0]  # Process the first file for now
        content = await file.read()
        try:
            document_text = content.decode("utf-8")
        except UnicodeDecodeError:
            # If it's not UTF-8 encoded, it's likely a binary file
            # For PDFs, you could use PyPDF2 or other libraries to extract text
            document_text = f"Failed to extract text from {file.filename}"

        # Reset file position
        await file.seek(0)

        # 6. Process each question using the RAG approach
        for question in question_list:
            if cancellation_requested:
                print("Operation cancelled by client disconnect, stopping processing")
                return VeraDocResponse(
                    results={
                        "status": "cancelled",
                        "message": "Operation cancelled by user",
                    }
                )

            question = question.strip()
            if not question:
                continue

            # Step 1: Retrieve relevant context from the knowledge base using vectordb service
            search_result = vectordb_service.search_hybrid(
                query=question,
                embedding_model_id=embedding_model.id,
                knowledge_base_id=str(kb.id),
                limit=5,
                output_fields=["content", "source_id", "title", "author", "url"],
                alpha=0.7,
            )

            if not search_result["success"]:
                print(
                    f"Search failed for question '{question}': {search_result.get('error', 'Unknown error')}"
                )
                continue

            chunks = search_result["results"]
            context = "\n\n".join([chunk["entity"]["content"] for chunk in chunks])

            # store source documents for citation
            source_citations = []
            for chunk in chunks:
                entity = chunk["entity"]

                # Create metadata similar to the old format
                metadata = {
                    "source_id": entity.get("source_id", ""),
                    "title": entity.get("title", ""),
                    "author": entity.get("author", ""),
                    "url": entity.get("url", ""),
                }

                # Try to get source data id from the source table
                if entity.get("source_id"):
                    metadata["source_id"] = str(entity["source_id"])
                    if entity.get("url"):
                        metadata["source"] = entity["url"]

                source = {"content": entity["content"], "metadata": metadata}
                source_citations.append(source)

            if cancellation_requested:
                print("Operation cancelled by client disconnect, stopping processing")
                return VeraDocResponse(
                    results={
                        "status": "cancelled",
                        "message": "Operation cancelled by user",
                    }
                )

            # Step 2: Get the relevant policy context for this question
            print("Generating context for question...")
            question_context = llm.invoke(
                context_prompt_template,
                {"context": context, "question": question},
            )
            print(f"Got context: {question_context[:100]}...")

            if cancellation_requested:
                print("Operation cancelled by client disconnect, stopping processing")
                return VeraDocResponse(
                    results={
                        "status": "cancelled",
                        "message": "Operation cancelled by user",
                    }
                )

            # Step 3: Answer the question based on the uploaded document and policy context
            print("Generating answer based on document and context...")
            answer = llm.invoke(
                qa_prompt_template,
                {
                    "document_text": document_text[
                        :10000
                    ],  # Limit length to avoid token issues
                    "question": question,
                    "question_context": question_context,
                },
            )
            print(f"Got answer: {answer[:100]}...")

            print("Source citations for question:", question)
            # for source in source_citations:
            # print(f"Source: {source['metadata'].get('source', 'Unknown')}, Content: {source['content']}")

            # Store the question-answer pair with context
            qa_pairs.append(
                {
                    "question": question,
                    "answer": answer,
                    "context": question_context,
                    "source_citations": source_citations,
                }
            )

        # 7. Generate the final evaluation
        if cancellation_requested:
            print("Operation cancelled by client disconnect, stopping processing")
            return VeraDocResponse(
                results={
                    "status": "cancelled",
                    "message": "Operation cancelled by user",
                }
            )

        qa_pairs_text = ""
        for i, qa in enumerate(qa_pairs):
            qa_pairs_text += (
                f"Question {i+1}: {qa['question']}\nAnswer: {qa['answer']}\n\n"
            )

        # Final evaluation
        print("Generating final evaluation...")
        final_evaluation = llm.invoke(
            final_prompt_template, {"qa_pairs": qa_pairs_text}
        )
        print(f"Got final evaluation: {final_evaluation[:100]}...")

        interaction_id = LlmService.record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="veradoc",
            input_data={
                "questions": request_data.questions,
                "document_name": file.filename,
                "kb_id": request_data.knowledge_base_id,
            },
            output_data={
                "final_evaluation": final_evaluation,
                "qa_count": len(qa_pairs),
            },
            metadata={
                "qa_pairs": qa_pairs  # Store the full QA pairs with sources for retrieval
            },
        )

        # 8. Compile the results
        result = {
            "final_evaluation": final_evaluation,
            "qa_pairs": qa_pairs,
            "interaction_id": str(interaction_id),
        }

        return VeraDocResponse(results=result)

    except Exception as e:
        print("Error processing RAG checklist:")
        print(str(e))

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing RAG checklist: {str(e)}"
        )
    finally:
        # Clean up the disconnect monitor if it exists
        if disconnect_monitor:
            disconnect_monitor.cancel()


# Functions related to Checklists
@router.post("/checklists", response_model=VeraDocChecklist)
def create_checklist(
    checklist: VeraDocChecklist,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Save a new checklist to the database.
    """
    existing_checklist = session.exec(
        select(VeraDocChecklist).where(VeraDocChecklist.name == checklist.name)
    ).first()
    if existing_checklist:
        raise HTTPException(
            status_code=400, detail="A checklist with this name already exists."
        )

    checklist.owner_id = current_user.id
    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist


@router.get("/checklists", response_model=List[VeraDocChecklist])
def get_checklists(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve all checklists from the database for this user.
    """
    return session.exec(
        select(VeraDocChecklist).where(VeraDocChecklist.owner_id == current_user.id)
    ).all()


@router.get("/checklists/{checklist_id}", response_model=VeraDocChecklist)
def get_checklist(checklist_id: uuid.UUID, session: SessionDep):
    """
    Retrieve a specific checklist by ID.
    """
    checklist = session.get(VeraDocChecklist, checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found.")
    return checklist


@router.put("/checklists/{checklist_id}", response_model=VeraDocChecklist)
def update_checklist(
    checklist_id: uuid.UUID,
    updated_checklist: VeraDocChecklist,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Update an existing checklist.
    """
    checklist = session.get(VeraDocChecklist, checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found.")

    # Ensure the current user is the owner of the checklist
    if checklist.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this checklist."
        )

    checklist.name = updated_checklist.name
    checklist.description = updated_checklist.description
    checklist.questions = updated_checklist.questions
    checklist.date_modified = datetime.utcnow()

    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist


@router.delete("/checklists/{checklist_id}", response_model=Message)
def delete_checklist(
    checklist_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
):
    """
    Delete a checklist by ID.
    """
    checklist = session.get(VeraDocChecklist, checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found.")

    # Ensure the current user is the owner of the checklist
    if checklist.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this checklist."
        )

    session.delete(checklist)
    session.commit()
    return Message(message="Checklist deleted successfully.")


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_veradoc_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
    show_all: bool = False,
):
    """Retrieve past VeraDoc evaluation history for the current user or all users."""
    print("Retrieving VeraDoc history. Show all:", show_all)

    try:
        # Start with base query
        query = select(LlmInteraction).where(LlmInteraction.functionality == "veradoc")

        # Only filter by user if not showing all users
        if not show_all:
            query = query.where(LlmInteraction.user_id == current_user.id)

        # Add ordering and pagination
        reports = session.exec(
            query.order_by(LlmInteraction.date_created.desc()).offset(skip).limit(limit)
        ).all()

        print(f"Found {len(reports)} VeraDoc evaluations for user {current_user.id}")

        result = []
        for report in reports:
            # Initialize variables outside the try block
            input_data = {}
            output_data = {}
            extra_data = {}
            kb_name = "Unknown Knowledge Base"

            try:
                # Parse the input_data and output_data from string to dict
                input_data = json.loads(report.input_data) if report.input_data else {}
                output_data = (
                    json.loads(report.output_data) if report.output_data else {}
                )
                extra_data = report.extra_data or {}

                # Get KB name from input_data
                if input_data.get("kb_id"):
                    kb = session.get(KnowledgeBase, input_data.get("kb_id"))
                    kb_name = kb.title if kb else "Unknown Knowledge Base"

                # Create a user-friendly title
                document_name = input_data.get("document_name", "Unnamed Document")
                title = f"Evaluation of {document_name}"

                # Create result item
                result_item = {
                    "id": str(report.id),
                    "date_created": report.date_created,
                    "title": title,
                    "document_name": document_name,
                    "kb_name": kb_name,
                    "kb_id": input_data.get("kb_id", ""),
                    "questions": input_data.get("questions", ""),
                    "qa_count": output_data.get("qa_count", 0),
                    "final_evaluation": output_data.get("final_evaluation", ""),
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
                    user = session.get(User, report.user_id)
                    user_name = (
                        f"{user.full_name or 'User'} ({user.email})"
                        if user
                        else "Unknown User"
                    )
                    result_item["user_name"] = user_name

                result.append(result_item)
            except Exception as e:
                # If parsing fails, add a minimal entry
                print(f"Error processing report {report.id}: {e}")
                result.append(
                    {
                        "id": str(report.id),
                        "date_created": report.date_created,
                        "title": f"Evaluation from {report.date_created.strftime('%Y-%m-%d')}",
                    }
                )

        return result
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving VeraDoc history: {str(e)}"
        )


@router.get("/history/{report_id}", response_model=VeraDocDetailResponse)
async def get_veradoc_detail(
    report_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Retrieve a specific VeraDoc evaluation's full content by ID."""
    try:
        report = session.get(LlmInteraction, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # No longer need to check this as we may now view others' outputs
        # if report.user_id != current_user.id:
        #    raise HTTPException(
        #        status_code=403, detail="You don't have access to this report"
        #    )

        if report.functionality != "veradoc":
            raise HTTPException(
                status_code=400, detail="This is not a VeraDoc evaluation"
            )

        try:
            input_data = json.loads(report.input_data) if report.input_data else {}
            output_data = json.loads(report.output_data) if report.output_data else {}
            extra_data = report.extra_data or {}

            # For backward compatibility, try to reconstruct full results
            document_name = input_data.get("document_name", "Unknown Document")
            kb_name = "Unknown Knowledge Base"

            # Try to get KB name
            kb_id = input_data.get("kb_id")
            if kb_id:
                kb = session.get(KnowledgeBase, kb_id)
                kb_name = kb.title if kb else "Unknown Knowledge Base"

            # Create a response that matches the structure expected by the frontend
            result = {
                "id": str(report.id),
                "date_created": report.date_created,
                "document_name": document_name,
                "kb_name": kb_name,
                "kb_id": kb_id,
                "questions": input_data.get("questions", ""),
                "results": {
                    "final_evaluation": output_data.get("final_evaluation", ""),
                    "qa_pairs": extra_data.get("qa_pairs", []),
                    "interaction_id": str(report.id),
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

        except Exception as e:
            # Fallback if parsing fails
            return {
                "id": str(report.id),
                "date_created": report.date_created,
                "results": {
                    "final_evaluation": f"Unable to reconstruct evaluation from {report.date_created}.\n\n"
                    f"This might be due to an older format or incomplete data.",
                    "qa_pairs": [],
                },
            }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error retrieving evaluation details: {str(e)}"
        )


@router.post("/generate/docx", response_class=StreamingResponse)
async def generate_docx(
    session: SessionDep, current_user: CurrentUser, request: DocxRequest
):
    """
    Generate a DOCX file from the evaluation content.
    """
    print("Now generating DOCX of evaluation...")
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
            else "Document Evaluation"
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
        filename = f"evaluation_{timestamp}.docx"

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
