import uuid
import json
from app.models import (
    VeraDocResponse,
    VeraDocChecklist,
    RagChecklistRequest,
    EmbeddingModel,
    Source,
    KnowledgeBase,
    LlmInteraction,
    DocxRequest,
    VeraDocDetailResponse,
    Message,
    User,
    OptimizeChecklistRequest,
    ChecklistSuggestion,
    OptimizedChecklistResponse,
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
)

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.services.knowledgebases import get_embedding_model
from app.services.embeddings import load_embeddings_model
from app.services.llms import get_default_llm, invoke_llm, record_llm_interaction
from app.services.retrievers import (
    create_ensemble_retriever,
)  # Import the ensemble retriever

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
import re
from pathlib import Path
import csv
import zipfile
import traceback
from io import BytesIO, StringIO

from datetime import datetime
from starlette.requests import Request
import tempfile
import traceback
import markdown
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from docx import Document  # For .docx file handling
from docx.enum.text import WD_ALIGN_PARAGRAPH
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

        elif file_ext in [".txt", ".md"]:
            # Handle text files
            try:
                return file_content.decode("utf-8")
            except UnicodeDecodeError:
                return file_content.decode("latin-1")

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


router = APIRouter(prefix="/veradoc", tags=["veradoc"])

# Initialize the LLM
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)


def generate_template(questions: List[str]) -> Dict[str, str]:
    """
    Generate a JSON template from a list of questions.
    Each field will have a blank value.
    """
    return {field: "" for field in questions}


def parse_optimization_response(
    llm_response: str, original_qa: dict
) -> ChecklistSuggestion:
    """Parse the LLM optimization response into a structured suggestion."""
    try:
        lines = llm_response.strip().split("\n")
        revised_question = original_qa["question"]  # Default to original
        reason = "No changes suggested"
        needs_revision = False

        for line in lines:
            line = line.strip()
            if line.startswith("REVISED_QUESTION:"):
                revised_question = line.replace("REVISED_QUESTION:", "").strip()
            elif line.startswith("REASON:"):
                reason = line.replace("REASON:", "").strip()
            elif line.startswith("NEEDS_REVISION:"):
                needs_revision_str = line.replace("NEEDS_REVISION:", "").strip().lower()
                needs_revision = needs_revision_str in ["yes", "true", "1"]

        return ChecklistSuggestion(
            original_question=original_qa["question"],
            suggested_question=revised_question,
            reason=reason,
            current_answer=original_qa["answer"],
            needs_revision=needs_revision,
        )
    except Exception as e:
        print(f"Error parsing optimization response: {e}")
        return ChecklistSuggestion(
            original_question=original_qa["question"],
            suggested_question=original_qa["question"],
            reason=f"Error parsing suggestion: {str(e)}",
            current_answer=original_qa["answer"],
            needs_revision=False,
        )


def needs_optimization(answer: str) -> bool:
    """Determine if a checklist question needs optimization based on the answer."""
    answer_lower = answer.lower()
    negative_indicators = [
        "no",
        "not",
        "insufficient",
        "missing",
        "absent",
        "lacks",
        "does not",
        "doesn't",
        "cannot",
        "can't",
        "unable",
        "fails",
        "inadequate",
        "incomplete",
        "unclear",
        "vague",
        "poorly",
    ]

    # Check if any negative indicators are present
    for indicator in negative_indicators:
        if indicator in answer_lower:
            return True

    return False


# Add the new endpoint
@router.post("/process-rag", response_model=VeraDocResponse)
async def process_rag_checklist(
    session: SessionDep,
    current_user: CurrentUser,
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

            # 3. Load the vector database with the SAME model used to create the knowledge base
            # Use the knowledge base's specific embedding model if available
            if kb.embedding_model_id:
                embedding_model = session.get(EmbeddingModel, kb.embedding_model_id)
                if embedding_model:
                    # Use the KB's original model
                    model_id = embedding_model.model_id
                    provider = embedding_model.provider
                    print(
                        f"Using knowledge base's original embedding model: {model_id}"
                    )
                else:
                    # Fallback if the model was deleted from the database
                    embedding_info = get_embedding_model(session, current_user)
                    model_id = embedding_info["model_id"]
                    provider = embedding_info["provider"]
                    print(
                        f"Original embedding model not found, using current default: {model_id}"
                    )
            else:
                # For knowledge bases created before tracking embedding models
                embedding_info = get_embedding_model(session, current_user)
                model_id = embedding_info["model_id"]
                provider = embedding_info["provider"]
                print(
                    f"Knowledge base has no embedding model record, using current default: {embedding_info}"
                )

            print(f"Initializing embedding model: {model_id} ({provider})")
            embeddings = load_embeddings_model(provider=provider, model_id=model_id)
            chroma_db = Chroma(
                persist_directory=temp_dir, embedding_function=embeddings
            )

            # Print all metadata in the vectorstore
            print("======= CHROMA VECTORDB METADATA CONTENTS =======")
            # Get all documents with their metadata
            all_docs = chroma_db.get()
            if all_docs and "metadatas" in all_docs and False:
                for i, metadata in enumerate(all_docs["metadatas"]):
                    print(f"Document {i+1} Metadata: {metadata}")
                    # If you want to see document content as well
                    if "documents" in all_docs and i < len(all_docs["documents"]):
                        doc_preview = (
                            all_docs["documents"][i][:200] + "..."
                            if len(all_docs["documents"][i]) > 100
                            else all_docs["documents"][i]
                        )
                        print(f"Content preview: {doc_preview}")
                    print("-" * 50)
            else:
                print("No documents or metadata found in the vectorstore")
            print("================================================")

            # Create a hybrid retriever that combines vector-based and keyword-based retrieval
            retriever = create_ensemble_retriever(
                chroma_db=chroma_db,
                vector_weight=0.7,  # Weight for vector-based retrieval
                keyword_weight=0.3,  # Weight for keyword-based retrieval
                search_kwargs={"k": settings.RAG_NUM_CHUNKS},  # Use config value
            )

            # 4. Initialize the LLM
            # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
            print("Now loading default LLM for session with following info:")
            print("Session:", session)
            llm = get_default_llm(session, current_user)
            print("LLM successfully loaded.")

            # 5. Define the prompts for the different stages
            context_prompt_template = settings.VERADOC_CONTEXT_PROMPT_TEMPLATE
            qa_prompt_template = settings.VERADOC_QA_PROMPT_TEMPLATE
            final_prompt_template = settings.VERADOC_FINAL_PROMPT_TEMPLATE

            # 6. Process each uploaded file
            qa_pairs = []

            # Parse questions - support both legacy string format and new structured format
            try:
                # Try to parse as structured JSON format
                questions_data = json.loads(request_data.questions)
                if isinstance(questions_data, list) and all(
                    isinstance(item, dict)
                    and "text" in item
                    and "consultDocuments" in item
                    for item in questions_data
                ):
                    # New structured format
                    question_list = questions_data
                else:
                    raise ValueError("Not structured format")
            except (json.JSONDecodeError, ValueError):
                # Fallback to legacy string format
                question_texts = request_data.questions.strip().split("\n")
                question_list = [
                    {"text": q.strip(), "consultDocuments": True}
                    for q in question_texts
                    if q.strip()
                ]

            # Get file content
            file = files[0]  # Process the first file for now
            content = await file.read()

            # Extract text using the new extraction function
            document_text = extract_text_from_file(content, file.filename)
            print(f"Extracted {len(document_text)} characters from {file.filename}")

            # Reset file position
            await file.seek(0)

            # 7. Process each question using the RAG approach
            for question_item in question_list:
                if cancellation_requested:
                    print(
                        "Operation cancelled by client disconnect, stopping processing"
                    )
                    return VeraDocResponse(
                        results={
                            "status": "cancelled",
                            "message": "Operation cancelled by user",
                        }
                    )

                question_text = question_item.get("text", "").strip()
                consult_documents = question_item.get("consultDocuments", True)

                if not question_text:
                    continue

                print(
                    f"Processing question: {question_text[:50]}... (consult documents: {consult_documents})"
                )

                if consult_documents:
                    # Standard process: retrieve context from knowledge base
                    # Step 1: Retrieve relevant context from the knowledge base
                    docs = retriever.get_relevant_documents(question_text)
                    context = "\n\n".join([doc.page_content for doc in docs])

                    # Store source documents for citation
                    source_citations = []
                    for doc in docs:
                        # Ensure source_data_id is included in metadata if available
                        metadata = (
                            doc.metadata.copy()
                        )  # Copy to avoid modifying the original

                        # If the metadata contains a source path that matches a pattern from a KB
                        if "source" in metadata and isinstance(metadata["source"], str):
                            # Try to find the corresponding source_data_id
                            source_path = metadata["source"]
                            # Extract just the filename
                            raw_filename = Path(source_path).name

                            # Extract the real filename after the underscore using regex
                            # This looks for any characters followed by an underscore, then captures everything after
                            match = re.search(r"^[^_]*_(.+)$", raw_filename)
                            if match:
                                # Use the captured group (everything after the underscore)
                                filename = match.group(1)
                            else:
                                # Fallback to the original filename if no underscore found
                                filename = raw_filename

                            # Debug info
                            print(f"Raw filename: {raw_filename}")
                            print(f"Extracted filename: {filename}")

                            # Try to find the source by the extracted name
                            source_entry = session.exec(
                                select(Source).where(Source.name == filename)
                            ).first()

                            if source_entry:
                                metadata["source_data_id"] = str(
                                    source_entry.source_data_id
                                )

                        source = {"content": doc.page_content, "metadata": metadata}
                        source_citations.append(source)

                    if cancellation_requested:
                        print(
                            "Operation cancelled by client disconnect, stopping processing"
                        )
                        return VeraDocResponse(
                            results={
                                "status": "cancelled",
                                "message": "Operation cancelled by user",
                            }
                        )

                    # Step 2: Get the relevant policy context for this question
                    print("Generating context for question...")
                    question_context = invoke_llm(
                        llm,
                        context_prompt_template,
                        {"context": context, "question": question_text},
                    )
                    print(f"Got context: {question_context[:100]}...")
                else:
                    # Skip knowledge base consultation - use empty context and citations
                    question_context = (
                        "No policy context consultation requested for this question."
                    )
                    source_citations = []
                    print(
                        f"Skipping document consultation for question: {question_text[:50]}..."
                    )

                if cancellation_requested:
                    print(
                        "Operation cancelled by client disconnect, stopping processing"
                    )
                    return VeraDocResponse(
                        results={
                            "status": "cancelled",
                            "message": "Operation cancelled by user",
                        }
                    )

                # Step 3: Answer the question based on the uploaded document and policy context
                print("Generating answer based on document and context...")

                # Prepare custom instructions section
                custom_instructions_section = ""
                if (
                    hasattr(request_data, "custom_instructions")
                    and request_data.custom_instructions
                ):
                    custom_instructions_section = f"\nADDITIONAL INSTRUCTIONS:\n{request_data.custom_instructions.strip()}\n"

                # DEBUG: Print the full prompt sent to the LLM
                try:
                    rendered_prompt = qa_prompt_template.format(
                        document_text=document_text,
                        question=question_text,
                        question_context=question_context,
                        custom_instructions_section=custom_instructions_section,
                    )
                except Exception as e:
                    rendered_prompt = f"[ERROR rendering prompt: {e}]"
                print("\n===== VERADOC_QA_PROMPT_TEMPLATE PROMPT SENT TO LLM =====\n")
                print(rendered_prompt)
                print("\n========================================================\n")
                answer = invoke_llm(
                    llm,
                    qa_prompt_template,
                    {
                        "document_text": document_text,
                        "question": question_text,
                        "question_context": question_context,
                        "custom_instructions_section": custom_instructions_section,
                    },
                )
                print(f"Got answer: {answer[:100]}...")

                print("Source citations for question:", question_text)
                # for source in source_citations:
                # print(f"Source: {source['metadata'].get('source', 'Unknown')}, Content: {source['content']}")

                # Store the question-answer pair with context
                qa_pairs.append(
                    {
                        "question": question_text,
                        "answer": answer,
                        "context": question_context,
                        "source_citations": source_citations,
                    }
                )

            # 8. Generate the final evaluation
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
            final_evaluation = invoke_llm(
                llm, final_prompt_template, {"qa_pairs": qa_pairs_text}
            )
            print(f"Got final evaluation: {final_evaluation[:100]}...")

            interaction_id = record_llm_interaction(
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

            # 9. Compile the results
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
    # Temporarily truncate description to fit current database constraint
    # TODO: Remove this after running migration to increase description length
    if checklist.description and len(checklist.description) > 255:
        checklist.description = checklist.description[:252] + "..."
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
    # Temporarily truncate description to fit current database constraint
    # TODO: Remove this after running migration to increase description length
    description = updated_checklist.description
    if description and len(description) > 255:
        description = description[:252] + "..."
    checklist.description = description

    # Debug logging to see what questions data is being received
    print(
        f"Updating checklist {checklist_id} with questions: {updated_checklist.questions}"
    )

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


@router.post("/optimize-checklist", response_model=OptimizedChecklistResponse)
async def optimize_checklist(
    session: SessionDep,
    current_user: CurrentUser,
    request_data: OptimizeChecklistRequest = Depends(),
    files: List[UploadFile] = File(...),
    request: FastAPIRequest = None,
):
    """
    Optimize checklist questions by testing them against a document that should meet all requirements.
    Suggests revisions for questions that resulted in negative answers.
    """
    print("optimize_checklist function invoked!")
    cancellation_requested = False

    try:
        print("Setting up disconnect monitor for checklist optimization...")
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

        print("Starting checklist optimization...")

        # 1. Retrieve knowledge base
        kb = session.get(KnowledgeBase, request_data.knowledge_base_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        if kb.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="You don't have access to this knowledge base"
            )

        # 2. Set up the same infrastructure as process_rag_checklist
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

            # 3. Process the test document
            file = files[0]
            content = await file.read()
            document_text = extract_text_from_file(content, file.filename)
            print(
                f"Processing test document: {file.filename} ({len(document_text)} characters)"
            )

            # 4. Run the review process with current questions
            question_list = request_data.questions.strip().split("\n")
            qa_results = []

            context_prompt_template = settings.VERADOC_CONTEXT_PROMPT_TEMPLATE
            qa_prompt_template = settings.VERADOC_QA_PROMPT_TEMPLATE
            optimize_prompt_template = settings.VERADOC_OPTIMIZE_PROMPT_TEMPLATE

            print(f"Evaluating {len(question_list)} questions...")

            for question in question_list:
                if cancellation_requested:
                    print("Operation cancelled by client disconnect")
                    raise HTTPException(
                        status_code=408, detail="Operation cancelled by user"
                    )

                question = question.strip()
                if not question:
                    continue

                # Get relevant context
                docs = retriever.get_relevant_documents(question)
                context = "\n\n".join([doc.page_content for doc in docs])

                # Generate policy context
                question_context = invoke_llm(
                    llm,
                    context_prompt_template,
                    {"context": context, "question": question},
                )

                # Prepare custom instructions section if provided
                custom_instructions_section = ""
                if (
                    request_data.custom_instructions
                    and request_data.custom_instructions.strip()
                ):
                    custom_instructions_section = f"\nADDITIONAL INSTRUCTIONS:\n{request_data.custom_instructions.strip()}\n"

                # Generate answer
                answer = invoke_llm(
                    llm,
                    qa_prompt_template,
                    {
                        "document_text": document_text[:10000],
                        "question": question,
                        "question_context": question_context,
                        "custom_instructions_section": custom_instructions_section,
                    },
                )

                qa_results.append(
                    {
                        "question": question,
                        "answer": answer,
                        "context": question_context,
                    }
                )

                print(
                    f"Question: {question[:50]}... -> {'NEEDS OPTIMIZATION' if needs_optimization(answer) else 'OK'}"
                )

            # 5. Generate optimization suggestions
            suggestions = []
            optimization_count = 0

            for qa in qa_results:
                if cancellation_requested:
                    print("Operation cancelled by client disconnect")
                    raise HTTPException(
                        status_code=408, detail="Operation cancelled by user"
                    )

                if needs_optimization(qa["answer"]):
                    optimization_count += 1
                    print(
                        f"Generating suggestion for question: {qa['question'][:50]}..."
                    )

                    # Generate optimization suggestion
                    suggestion_response = invoke_llm(
                        llm,
                        optimize_prompt_template,
                        {
                            "original_question": qa["question"],
                            "generated_answer": qa["answer"],
                            "document_context": qa["context"],
                        },
                    )

                    suggestion = parse_optimization_response(suggestion_response, qa)
                    suggestions.append(suggestion)
                else:
                    # Question is already working well
                    suggestions.append(
                        ChecklistSuggestion(
                            original_question=qa["question"],
                            suggested_question=qa["question"],
                            reason="Question already generates positive responses",
                            current_answer=qa["answer"],
                            needs_revision=False,
                        )
                    )

            # 6. Compile results
            original_questions = [qa["question"] for qa in qa_results]
            optimized_questions = [s.suggested_question for s in suggestions]

            analysis_summary = f"""
Checklist Optimization Analysis:
- Total questions evaluated: {len(original_questions)}
- Questions needing optimization: {optimization_count}
- Questions working well: {len(original_questions) - optimization_count}
- Test document: {file.filename}

The optimization process identified questions that resulted in negative responses when evaluating a document that should meet all requirements. Suggested revisions aim to make requirements more achievable while maintaining their intent.
            """.strip()

            print(
                f"Optimization complete: {optimization_count}/{len(original_questions)} questions optimized"
            )

            return OptimizedChecklistResponse(
                original_questions=original_questions,
                suggestions=suggestions,
                optimized_questions=optimized_questions,
                analysis_summary=analysis_summary,
            )

    except Exception as e:
        print("Error in checklist optimization:")
        print(str(e))
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error optimizing checklist: {str(e)}"
        )
    finally:
        if disconnect_monitor:
            disconnect_monitor.cancel()


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


@router.post("/generate/csv", response_class=StreamingResponse)
async def generate_csv(
    session: SessionDep, current_user: CurrentUser, request: DocxRequest
):
    """
    Generate a CSV file from VeraDoc review results with columns for:
    Checklist Question, Policy Context, Citations, Answer, and Final Evaluation.
    """
    print("Now generating CSV of VeraDoc review...")
    try:
        # Get the content from the request - this should be the full review JSON
        if not request.content:
            raise HTTPException(status_code=400, detail="Review content is required")

        # Create CSV content
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)

        # Write header with VeraDoc-specific columns
        csv_writer.writerow(
            [
                "Checklist Question",
                "Policy Context",
                "Citations",
                "Answer",
                "Final Evaluation",
            ]
        )

        try:
            # Parse the content as JSON (review data)
            data = json.loads(request.content)

            # Extract QA pairs and final evaluation
            qa_pairs = data.get("qa_pairs", [])
            final_evaluation = data.get(
                "final_evaluation", "No final evaluation provided"
            )

            # Process each QA pair
            for qa in qa_pairs:
                question = qa.get("question", "")
                answer = qa.get("answer", "")
                context = qa.get("context", "")

                # Extract citations
                citations = []
                if "source_citations" in qa:
                    for citation in qa["source_citations"]:
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

                # Clean up text fields
                question_clean = question.replace("\n", " ").replace("\r", " ")
                answer_clean = answer.replace("\n", " ").replace("\r", " ")
                context_clean = context.replace("\n", " ").replace("\r", " ")

                # For the final evaluation, we'll include it for each row
                # (since it's a summary of all QA pairs)
                final_eval_clean = final_evaluation.replace("\n", " ").replace(
                    "\r", " "
                )

                # Write row
                csv_writer.writerow(
                    [
                        question_clean,
                        context_clean,
                        citations_text,
                        answer_clean,
                        final_eval_clean,
                    ]
                )

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid content format. Expected JSON with VeraDoc review data.",
            )

        # Get CSV content
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        # Create BytesIO object for the response
        csv_bytes = BytesIO(csv_content.encode("utf-8"))
        csv_bytes.seek(0)

        print("VeraDoc CSV file generated successfully.")

        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"veradoc_review_{timestamp}.csv"

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


@router.post("/optimization/csv", response_class=StreamingResponse)
async def generate_optimization_csv(
    session: SessionDep, current_user: CurrentUser, request: DocxRequest
):
    """
    Generate a CSV file from checklist optimization results with columns for:
    Question Number, Original Question, Suggested Question, Needs Revision, Reason, Current Answer.
    """
    print("Now generating CSV of checklist optimization results...")
    try:
        # Get the content from the request - this should be the optimization results JSON
        if not request.content:
            raise HTTPException(
                status_code=400, detail="Optimization content is required"
            )

        # Create CSV content
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)

        # Write header with optimization-specific columns
        csv_writer.writerow(
            [
                "Question Number",
                "Original Question",
                "Suggested Question",
                "Needs Revision",
                "Reason",
                "Current Answer",
                "Analysis Summary",
            ]
        )

        try:
            # Parse the content as JSON (optimization results data)
            data = json.loads(request.content)

            # Extract suggestions and analysis summary
            suggestions = data.get("suggestions", [])
            analysis_summary = data.get(
                "analysis_summary", "No analysis summary provided"
            )

            # Process each suggestion
            for index, suggestion in enumerate(suggestions, 1):
                original_question = suggestion.get("original_question", "")
                suggested_question = suggestion.get("suggested_question", "")
                needs_revision = suggestion.get("needs_revision", False)
                reason = suggestion.get("reason", "")
                current_answer = suggestion.get("current_answer", "")

                # Clean up text fields (remove newlines and carriage returns for CSV)
                original_question_clean = original_question.replace("\n", " ").replace(
                    "\r", " "
                )
                suggested_question_clean = suggested_question.replace(
                    "\n", " "
                ).replace("\r", " ")
                reason_clean = reason.replace("\n", " ").replace("\r", " ")
                current_answer_clean = current_answer.replace("\n", " ").replace(
                    "\r", " "
                )
                analysis_summary_clean = analysis_summary.replace("\n", " ").replace(
                    "\r", " "
                )

                # Write row
                csv_writer.writerow(
                    [
                        index,
                        original_question_clean,
                        suggested_question_clean,
                        "Yes" if needs_revision else "No",
                        reason_clean,
                        current_answer_clean,
                        analysis_summary_clean,
                    ]
                )

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid content format. Expected JSON with checklist optimization data.",
            )

        # Get CSV content
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        # Create BytesIO object for the response
        csv_bytes = BytesIO(csv_content.encode("utf-8"))
        csv_bytes.seek(0)

        print("Checklist optimization CSV file generated successfully.")

        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"checklist_optimization_{timestamp}.csv"

        # Return the CSV as a downloadable file
        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating optimization CSV: {str(e)}"
        )


@router.post("/generate-questions", response_model=GenerateQuestionsResponse)
def generate_questions(
    request_data: GenerateQuestionsRequest,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Generate checklist questions based on a description using LLM.
    """
    try:
        # Get the default LLM
        llm = get_default_llm(session, current_user)

        # Prepare variables for the prompt
        prompt_variables = {
            "description": request_data.description,
            "checklist_type": request_data.checklist_type,
        }

        # Generate questions using the LLM
        questions_response = invoke_llm(
            llm,
            settings.VERADOC_GENERATE_QUESTIONS_PROMPT_TEMPLATE,
            prompt_variables,
        )

        # Parse the response to extract questions and analysis
        questions = []
        analysis = ""

        lines = questions_response.strip().split("\n")
        in_questions_section = False
        in_analysis_section = False

        for line in lines:
            line = line.strip()
            if line.startswith("QUESTIONS:"):
                in_questions_section = True
                in_analysis_section = False
                continue
            elif line.startswith("ANALYSIS:"):
                in_questions_section = False
                in_analysis_section = True
                continue

            if in_questions_section:
                # Extract questions (numbered list)
                if re.match(r"^\d+\.\s+", line):
                    question = re.sub(r"^\d+\.\s+", "", line)
                    if question.strip():
                        questions.append(question.strip())
            elif in_analysis_section:
                if line:
                    if analysis:
                        analysis += " " + line
                    else:
                        analysis = line

        # If parsing failed, try simpler approach
        if not questions:
            # Split by lines and look for numbered items
            for line in lines:
                line = line.strip()
                if re.match(r"^\d+\.\s+", line):
                    question = re.sub(r"^\d+\.\s+", "", line)
                    if question.strip():
                        questions.append(question.strip())

        # Ensure we have some questions
        if not questions:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate questions from the description. Please try with a more detailed description.",
            )

        # Apply user-specified limit if provided, otherwise use all generated questions
        if request_data.num_questions:
            questions = questions[: request_data.num_questions]

        if not analysis:
            analysis = f"Generated {len(questions)} questions based on the provided description to ensure comprehensive evaluation coverage."

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="generate_checklist_questions",
            input_data={
                "description": request_data.description,
                "requested_questions": request_data.num_questions,
                "checklist_type": request_data.checklist_type,
            },
            output_data={
                "questions_count": len(questions),
                "analysis": analysis,
            },
            metadata={},
        )

        return GenerateQuestionsResponse(
            questions=questions, description_analysis=analysis
        )

    except Exception as e:
        print(f"Error generating questions: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating questions: {str(e)}"
        )
