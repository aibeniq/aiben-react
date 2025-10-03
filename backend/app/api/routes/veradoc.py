import uuid
import json
import traceback
import re  # Add missing import for regex operations
import tempfile
import zipfile
import os
from pathlib import Path
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
from app.services.translation import translate_text_if_needed
from app.services.retrievers import (
    create_ensemble_retriever,
)  # Import the ensemble retriever
from app.services.enhanced_retrieval import SmartRetrieverFactory

from sqlmodel import select
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
    Request as FastAPIRequest,
)
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
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
import markdown
from langchain_community.vectorstores import Chroma

# from langchain_community.document_loaders import PyPDFLoader, TextLoader  # Removed - using pypdf instead
from langchain_community.document_loaders import TextLoader
from app.services.pdf_utils import load_pdf_with_pypdf
from langchain_core.documents import Document as LangchainDocument
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


async def prefetch_knowledge_base_context(
    retriever,
    question_list: List[Dict],
    llm,
    context_prompt_template: str,
    session,
    current_user,
    request: FastAPIRequest = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Pre-fetch knowledge base context for all questions to avoid redundant retrieval.
    Returns a dictionary mapping question text to its context and source citations.
    """
    print(f"Pre-fetching knowledge base context for {len(question_list)} questions...")
    
    question_contexts = {}
    
    for i, question_item in enumerate(question_list):
        # Check for cancellation during context pre-fetching
        try:
            if request and await request.is_disconnected():
                print(f"❌ CLIENT DISCONNECTED - Stopping context prefetch at question {i + 1}")
                raise HTTPException(
                    status_code=408,
                    detail="Request cancelled - client disconnected during context prefetch"
                )
        except Exception as e:
            print(f"Warning: Could not check disconnect status during prefetch: {e}")
        
        question_text = question_item.get("text", "").strip()
        consult_documents = question_item.get("consultDocuments", True)
        
        if not question_text:
            continue
            
        print(f"Pre-fetching context for question {i+1}/{len(question_list)}: {question_text[:50]}...")
        
        if consult_documents:
            try:
                # Step 1: Retrieve relevant context from the knowledge base
                docs = retriever.get_relevant_documents(question_text)
                
                if not docs:
                    print(f"No documents retrieved for question: {question_text[:50]}...")
                    context = "No relevant documents found in the knowledge base for this question."
                    source_citations = []
                else:
                    context = "\n\n".join([
                        doc.page_content for doc in docs if doc.page_content
                    ])
                    print(f"Retrieved {len(docs)} documents, context length: {len(context)} characters")
                    
                    # Store source documents for citation
                    source_citations = []
                    for doc in docs:
                        try:
                            # Process metadata and source citations
                            metadata = (
                                doc.metadata.copy()
                                if hasattr(doc, "metadata") and doc.metadata
                                else {}
                            )
                            
                            # Source lookup logic (same as original)
                            if "source" in metadata and isinstance(metadata["source"], str):
                                source_path = metadata["source"]
                                raw_filename = Path(source_path).name
                                
                                match = re.search(r"^[^_]*_(.+)$", raw_filename)
                                if match:
                                    filename = match.group(1)
                                else:
                                    filename = raw_filename
                                
                                try:
                                    source_entry = session.exec(
                                        select(Source).where(Source.name == filename)
                                    ).first()
                                    
                                    if not source_entry:
                                        source_entry = session.exec(
                                            select(Source).where(Source.name == raw_filename)
                                        ).first()
                                    
                                    if source_entry:
                                        metadata["source_data_id"] = str(source_entry.source_data_id)
                                except Exception as source_lookup_error:
                                    print(f"Error looking up source: {source_lookup_error}")
                            
                            source = {
                                "content": doc.page_content or "",
                                "metadata": metadata,
                            }
                            source_citations.append(source)
                        except Exception as citation_error:
                            print(f"Error processing citation: {citation_error}")
                            continue
                            
            except Exception as retrieval_error:
                print(f"Error retrieving documents for question '{question_text[:50]}...': {retrieval_error}")
                context = "Error occurred while retrieving relevant documents from the knowledge base."
                source_citations = []
            
            try:
                # Step 2: Get the relevant policy context for this question
                print("Generating context for question...")
                question_context = invoke_llm(
                    llm,
                    context_prompt_template,
                    {"context": context, "question": question_text},
                )
                print(f"Got context: {question_context[:100]}...")
                
                # Translate the question context if needed
                question_context = await translate_text_if_needed(
                    question_context, session, current_user, llm
                )
                
            except Exception as context_error:
                print(f"Error generating context for question: {context_error}")
                question_context = f"Error generating context: {str(context_error)}"
                # Translate the error message if needed
                question_context = await translate_text_if_needed(
                    question_context, session, current_user, llm
                )
        else:
            # Skip knowledge base consultation
            question_context = "No policy context consultation requested for this question."
            question_context = await translate_text_if_needed(
                question_context, session, current_user, llm
            )
            source_citations = []
            print(f"Skipping document consultation for question: {question_text[:50]}...")
        
        # Store the pre-fetched context and citations
        question_contexts[question_text] = {
            "context": question_context,
            "source_citations": source_citations,
            "consult_documents": consult_documents
        }
    
    print(f"✅ Pre-fetched context for {len(question_contexts)} questions")
    return question_contexts


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from various file formats using unified document processing."""
    from app.services.document_utils import extract_text_from_file_unified

    return extract_text_from_file_unified(file_content, filename)


async def extract_text_from_file_async(file_content: bytes, filename: str) -> str:
    """
    Async wrapper for text extraction to prevent blocking on large files.
    Uses ThreadPoolExecutor for CPU-intensive text extraction operations.
    """
    # Always use thread pool for DOCX files since they can be slow to process
    # regardless of size
    is_docx = filename.lower().endswith((".docx", ".doc"))

    # Define size threshold for async processing
    if is_docx:
        SIZE_THRESHOLD = 10 * 1024  # Very low threshold for DOCX files (10KB)
    else:
        SIZE_THRESHOLD = 50 * 1024  # 50KB for other files

    if len(file_content) > SIZE_THRESHOLD or is_docx:
        print(
            f"File requires thread pool processing ({len(file_content)} bytes, is_docx: {is_docx})"
        )

        # Process in thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=1) as executor:
            document_text = await loop.run_in_executor(
                executor, extract_text_from_file, file_content, filename
            )
        return document_text
    else:
        # For small non-DOCX files, process synchronously
        return extract_text_from_file(file_content, filename)


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
            policy_context=original_qa.get("context", ""),
        )
    except Exception as e:
        print(f"Error parsing optimization response: {e}")
        return ChecklistSuggestion(
            original_question=original_qa["question"],
            suggested_question=original_qa["question"],
            reason=f"Error parsing suggestion: {str(e)}",
            current_answer=original_qa["answer"],
            needs_revision=False,
            policy_context=original_qa.get("context", ""),
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
    files: List[UploadFile] = File(None),
    request: FastAPIRequest = None,
):
    """
    Process the uploaded files using RAG with a knowledge base.
    """
    print("process_rag_checklist function invoked!")
    print(f"Received search_mode: {request_data.search_mode}")
    print(
        f"Request data: knowledge_base_id={request_data.knowledge_base_id}, questions length={len(request_data.questions)}"
    )

    # Input validation
    if not request_data.knowledge_base_id:
        raise HTTPException(status_code=400, detail="Knowledge base ID is required")

    if not request_data.questions or not request_data.questions.strip():
        raise HTTPException(status_code=400, detail="Questions are required")

    # Check for at least one file
    total_files = len(files) if files else 0
    if total_files == 0:
        raise HTTPException(status_code=400, detail="At least one file is required")

    # Validate search mode
    if request_data.search_mode not in ["vector", "full_scan"]:
        print(
            f"Warning: Invalid search mode '{request_data.search_mode}', defaulting to 'vector'"
        )
        request_data.search_mode = "vector"

    try:
        print("Processing RAG checklist...")

        # 1. Retrieve knowledge base from database
        kb = session.get(KnowledgeBase, request_data.knowledge_base_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # 2. Create a temporary directory for ChromaDB
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zipped ChromaDB into the temp directory
            if kb.storage_type == "file" and kb.file_path:
                # File-based storage: extract from file path
                if os.path.exists(kb.file_path):
                    with zipfile.ZipFile(kb.file_path, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)
                else:
                    raise HTTPException(
                        status_code=400, detail="Knowledge base file not found on disk"
                    )
            elif kb.data:
                # Database storage: extract from data field
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

            # Create retriever based on search mode
            try:
                if request_data.search_mode == "full_scan":
                    # Full document scan: retrieve all documents from the knowledge base
                    print("Using full document scan mode")

                    # Test ChromaDB collection access first
                    try:
                        # Try multiple ways to get collection count
                        if hasattr(chroma_db, "_collection") and hasattr(
                            chroma_db._collection, "count"
                        ):
                            collection_count = chroma_db._collection.count()
                        else:
                            # Fallback: try to get a small sample to test access
                            test_data = chroma_db.get(limit=1)
                            collection_count = (
                                len(test_data.get("documents", [])) if test_data else 0
                            )

                        print(
                            f"Knowledge base collection has {collection_count} documents"
                        )

                        if collection_count == 0:
                            print(
                                f"Warning: Knowledge base '{request_data.knowledge_base_id}' appears to be empty"
                            )
                            # Don't raise error, let it proceed with empty results

                    except Exception as count_error:
                        print(f"Warning: Could not get collection count: {count_error}")
                        # Continue anyway - the get_relevant_documents method will handle empty collections

                    # Create a simple retriever that returns all documents
                    class FullScanRetriever:
                        def __init__(self, chroma_db):
                            self.chroma_db = chroma_db

                        def get_relevant_documents(self, query):
                            try:
                                print(
                                    f"FullScanRetriever: Processing query '{query[:50]}...'"
                                )

                                # Return all documents in the knowledge base with better error handling
                                try:
                                    all_data = self.chroma_db.get()
                                except Exception as get_error:
                                    print(
                                        f"Error getting documents from ChromaDB: {get_error}"
                                    )
                                    return []

                                # Convert to Document objects similar to vector search
                                documents = []

                                if (
                                    all_data
                                    and "documents" in all_data
                                    and all_data["documents"]
                                ):
                                    print(
                                        f"FullScanRetriever: Found {len(all_data['documents'])} total documents"
                                    )

                                    for i, doc_content in enumerate(
                                        all_data["documents"]
                                    ):
                                        try:
                                            # Safely get metadata
                                            metadata = {}
                                            if (
                                                "metadatas" in all_data
                                                and isinstance(
                                                    all_data["metadatas"], list
                                                )
                                                and i < len(all_data["metadatas"])
                                                and all_data["metadatas"][i] is not None
                                            ):

                                                raw_metadata = all_data["metadatas"][i]
                                                if isinstance(raw_metadata, dict):
                                                    metadata = raw_metadata
                                                else:
                                                    print(
                                                        f"Warning: Metadata at index {i} is not a dict: {type(raw_metadata)}"
                                                    )
                                                    metadata = {}

                                            # Ensure doc_content is a string
                                            content = (
                                                str(doc_content)
                                                if doc_content is not None
                                                else ""
                                            )

                                            if (
                                                content
                                            ):  # Only add documents with content
                                                documents.append(
                                                    LangchainDocument(
                                                        page_content=content,
                                                        metadata=metadata,
                                                    )
                                                )
                                        except Exception as doc_error:
                                            print(
                                                f"Error processing document {i}: {doc_error}"
                                            )
                                            # Continue processing other documents instead of failing
                                            continue
                                else:
                                    print(
                                        "FullScanRetriever: No documents found in knowledge base"
                                    )

                                print(
                                    f"FullScanRetriever: Returning {len(documents)} documents"
                                )
                                return documents

                            except Exception as e:
                                print(
                                    f"Error in FullScanRetriever.get_relevant_documents: {e}"
                                )
                                import traceback

                                traceback.print_exc()
                                # Return empty list instead of raising exception
                                return []

                    retriever = FullScanRetriever(chroma_db)
                else:
                    # Vector search mode (default) with enhanced content filtering
                    print("Using enhanced vector search mode with content filtering")
                    try:
                        retriever = (
                            SmartRetrieverFactory.create_academic_paper_retriever(
                                chroma_db=chroma_db,
                                search_kwargs={"k": settings.RAG_NUM_CHUNKS},
                            )
                        )
                        print(
                            "Enhanced academic retriever created successfully - will filter bibliography content"
                        )
                    except Exception as retriever_error:
                        print(f"Error creating enhanced retriever: {retriever_error}")
                        # Fallback to general document retriever with smart filtering
                        retriever = (
                            SmartRetrieverFactory.create_general_document_retriever(
                                chroma_db=chroma_db,
                                search_kwargs={"k": settings.RAG_NUM_CHUNKS},
                            )
                        )
                        print("Using fallback smart retriever with content filtering")

            except Exception as retriever_setup_error:
                print(f"Error setting up retriever: {retriever_setup_error}")
                traceback.print_exc()
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to set up document retriever: {str(retriever_setup_error)}",
                )

            # 4. Initialize the LLM
            # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
            print("Now loading default LLM for session with following info:")
            print("Session:", session)
            llm = get_default_llm(session, current_user)
            print("LLM successfully loaded.")

            # Check if LLM supports vision
            from app.services.vision_service import VisionService

            vision_enabled = VisionService.is_vision_enabled(llm)

            # 5. Define the prompts for the different stages
            context_prompt_template = settings.VERADOC_CONTEXT_PROMPT_TEMPLATE
            qa_prompt_template = settings.VERADOC_QA_PROMPT_TEMPLATE
            final_prompt_template = settings.VERADOC_FINAL_PROMPT_TEMPLATE

            # 6. Parse questions first - support both legacy string format and new structured format
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

            # 7. PRE-FETCH KNOWLEDGE BASE CONTEXT (OPTIMIZATION)
            # This step is the same regardless of which document is being reviewed
            print("🚀 OPTIMIZATION: Pre-fetching knowledge base context for all questions...")
            try:
                question_contexts = await prefetch_knowledge_base_context(
                    retriever=retriever,
                    question_list=question_list,
                    llm=llm,
                    context_prompt_template=context_prompt_template,
                    session=session,
                    current_user=current_user,
                    request=request
                )
                print(f"✅ Pre-fetched context for {len(question_contexts)} questions")
            except HTTPException:
                # Re-raise cancellation errors
                raise
            except Exception as prefetch_error:
                print(f"Error during context pre-fetch: {prefetch_error}")
                # Fall back to processing without pre-fetch
                question_contexts = {}

            # 8. Process each uploaded file using the pre-fetched context
            qa_pairs = []

            # 8. Process each uploaded file using the pre-fetched context
            all_files_results = []
            
            # Support multiple files - process each one
            for file_index, file in enumerate(files):
                if not file.filename:
                    print(f"Skipping file {file_index + 1}: No filename")
                    continue
                    
                print(f"Processing file {file_index + 1}/{len(files)}: {file.filename}")
                
                # Check for cancellation before processing each file
                try:
                    if request and await request.is_disconnected():
                        print(f"❌ CLIENT DISCONNECTED - Stopping at file {file_index + 1}")
                        return VeraDocResponse(
                            results={
                                "status": "cancelled",
                                "message": "Request cancelled - client disconnected"
                            }
                        )
                except Exception as e:
                    print(f"Warning: Could not check disconnect status: {e}")
                
                qa_pairs = []
                
                try:
                    content = await file.read()
                    if not content:
                        print(f"File {file.filename} appears to be empty, skipping")
                        continue

                    # Check if this is a potentially slow file to process
                    is_large_file = len(content) > 50000
                    is_docx_file = file.filename.lower().endswith((".docx", ".doc"))
                    needs_special_handling = is_large_file or is_docx_file

                    # Extract text using unified processing
                    print(f"Processing file with unified text extraction: {file.filename}")
                    document_text = await extract_text_from_file_async(
                        content, file.filename
                    )

                    # Extract images if vision is enabled
                    document_images = []
                    if vision_enabled:
                        try:
                            from app.services.document_utils import (
                                extract_documents_and_images_from_file_unified,
                            )

                            _, document_images = (
                                extract_documents_and_images_from_file_unified(
                                    content, file.filename
                                )
                            )
                            print(
                                f"Extracted {len(document_images)} images from {file.filename}"
                            )
                        except Exception as img_error:
                            print(
                                f"Warning: Could not extract images from {file.filename}: {img_error}"
                            )

                    # Handle case where no text was extracted
                    if not document_text or document_text.strip() == "":
                        if vision_enabled and document_images:
                            print(
                                f"No text extracted from {file.filename}, but {len(document_images)} images found. Using vision analysis as fallback."
                            )
                            document_text = f"This document ({file.filename}) contains images but no extractable text. Vision analysis will be used to answer questions about the visual content."
                        else:
                            print(f"Could not extract text from {file.filename}, skipping")
                            continue

                    print(f"Extracted {len(document_text)} characters from {file.filename}")
                    await file.seek(0)

                except Exception as file_error:
                    print(f"Error processing file {file.filename}: {file_error}")
                    # Add error result for this file and continue with next file
                    all_files_results.append({
                        "filename": file.filename,
                        "final_evaluation": f"Error processing file {file.filename}: {str(file_error)}",
                        "qa_pairs": [],
                        "interaction_id": None,
                    })
                    continue

                # 9. Process each question using the PRE-FETCHED context
                # 9. Process each question using the PRE-FETCHED context
                for i, question_item in enumerate(question_list):
                    try:
                        # Check if client has disconnected before processing each question
                        try:
                            if request and await request.is_disconnected():
                                print(f"❌ CLIENT DISCONNECTED - Stopping at question {i + 1} for file {file.filename}")
                                return VeraDocResponse(
                                    results={
                                        "status": "cancelled",
                                        "message": "Request cancelled - client disconnected"
                                    }
                                )
                        except Exception as e:
                            print(f"Warning: Could not check disconnect status: {e}")
                        
                        question_text = question_item.get("text", "").strip()
                        
                        if not question_text:
                            print(f"Skipping empty question at index {i}")
                            continue

                        print(
                            f"Processing question {i+1}/{len(question_list)} for {file.filename}: {question_text[:50]}..."
                        )

                        # 🚀 OPTIMIZATION: Use pre-fetched context instead of retrieving again
                        if question_text in question_contexts:
                            # Use pre-fetched context and citations
                            cached_context = question_contexts[question_text]
                            question_context = cached_context["context"]
                            source_citations = cached_context["source_citations"]
                            consult_documents = cached_context["consult_documents"]
                            print(f"✅ Using pre-fetched context for question: {question_text[:30]}...")
                        else:
                            # Fallback to original logic if pre-fetch failed for this question
                            print(f"⚠️ No pre-fetched context found for question: {question_text[:30]}..., using fallback")
                            consult_documents = question_item.get("consultDocuments", True)
                            
                            if consult_documents:
                                try:
                                    docs = retriever.get_relevant_documents(question_text)
                                    if not docs:
                                        context = "No relevant documents found in the knowledge base for this question."
                                        source_citations = []
                                    else:
                                        context = "\n\n".join([doc.page_content for doc in docs if doc.page_content])
                                        source_citations = [{"content": doc.page_content or "", "metadata": doc.metadata or {}} for doc in docs]
                                    
                                    question_context = invoke_llm(
                                        llm, context_prompt_template, {"context": context, "question": question_text}
                                    )
                                    question_context = await translate_text_if_needed(question_context, session, current_user, llm)
                                except Exception as fallback_error:
                                    print(f"Error in fallback context generation: {fallback_error}")
                                    question_context = f"Error generating context: {str(fallback_error)}"
                                    source_citations = []
                            else:
                                question_context = "No policy context consultation requested for this question."
                                question_context = await translate_text_if_needed(question_context, session, current_user, llm)
                                source_citations = []

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
                        print(
                            "\n===== VERADOC_QA_PROMPT_TEMPLATE PROMPT SENT TO LLM =====\n"
                        )
                        print(rendered_prompt)
                        print(
                            "\n========================================================\n"
                        )

                        try:
                            # Generate text-based answer
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
                            
                            print(f"Got text answer: {answer[:100]}...")

                            # Add vision analysis if images exist and LLM supports it
                            if vision_enabled and document_images:
                                print(
                                    f"Adding vision analysis for question: {question_text[:50]}..."
                                )

                                # Prepare images for processing
                                image_data_list = []
                                for idx, img_b64 in enumerate(document_images):
                                    image_data_list.append(
                                        {
                                            "image_data": img_b64,
                                            "source_file": file.filename,
                                            "image_index": idx,
                                            "metadata": {"extracted_from": file.filename},
                                        }
                                    )

                                try:
                                    vision_variables = {
                                        "question": question_text,
                                        "filename": file.filename,
                                        "custom_instructions": (
                                            request_data.custom_instructions
                                            if hasattr(request_data, "custom_instructions")
                                            else ""
                                        ),
                                    }

                                    vision_analysis = await VisionService.process_images_with_prompt(
                                        llm=llm,
                                        images=image_data_list,
                                        prompt_template=settings.VERADOC_VISION_PROMPT_TEMPLATE,
                                        variables=vision_variables,
                                    )

                                    # Translate vision analysis if needed
                                    vision_analysis = await translate_text_if_needed(
                                        vision_analysis, session, current_user, llm
                                    )

                                    # Combine text and vision analysis
                                    if (
                                        "contains images but no extractable text"
                                        in document_text
                                        and len(document_text) < 200
                                    ):
                                        # For image-only documents, use vision-primary combination
                                        combined_answer = f"## Visual Analysis\n{vision_analysis}\n\n## Document Note\nThis analysis is based on visual content as the document contains images but no extractable text."
                                    else:
                                        # Normal text + vision combination
                                        combined_answer = (
                                            VisionService.combine_text_and_vision_analysis(
                                                answer, vision_analysis, "comprehensive"
                                            )
                                        )

                                    answer = combined_answer
                                    print(
                                        f"Combined answer with vision analysis: {answer[:100]}..."
                                    )

                                except Exception as vision_error:
                                    print(
                                        f"Vision analysis error for question '{question_text[:50]}...': {vision_error}"
                                    )
                                    # Continue with text-only answer

                            # Translate the answer if needed
                            answer = await translate_text_if_needed(
                                answer, session, current_user, llm
                            )

                        except Exception as answer_error:
                            print(f"Error generating answer for question: {answer_error}")
                            answer = f"Error generating answer: {str(answer_error)}"

                        print("Source citations for question:", question_text)                        # Store the question-answer pair with context
                        qa_pairs.append(
                            {
                                "question": question_text,
                                "answer": answer,
                                "context": question_context,
                                "source_citations": source_citations,
                            }
                        )

                    except Exception as question_processing_error:
                        print(
                            f"Error processing question '{question_text[:50]}...': {question_processing_error}"
                        )
                        import traceback
                        traceback.print_exc()
                        # Add error result instead of failing completely
                        qa_pairs.append(
                            {
                                "question": question_text,
                                "answer": f"Error processing this question: {str(question_processing_error)}",
                                "context": "Error occurred during processing",
                                "source_citations": [],
                            }
                        )
                        continue                # Store file-specific QA pairs and final evaluation
                qa_pairs_text = ""
                for i, qa in enumerate(qa_pairs):
                    qa_pairs_text += (
                        f"Question {i+1}: {qa['question']}\nAnswer: {qa['answer']}\n\n"
                    )

                # Generate final evaluation for this file
                try:
                    print(f"Generating final evaluation for {file.filename}...")
                    final_evaluation = invoke_llm(
                        llm, final_prompt_template, {"qa_pairs": qa_pairs_text}
                    )
                    print(f"Got final evaluation: {final_evaluation[:100]}...")
                    final_evaluation = await translate_text_if_needed(
                        final_evaluation, session, current_user, llm
                    )
                except Exception as final_eval_error:
                    print(f"Error generating final evaluation for {file.filename}: {final_eval_error}")
                    final_evaluation = f"Error generating final evaluation: {str(final_eval_error)}"

                # Record interaction for this file
                try:
                    interaction_id = record_llm_interaction(
                        session=session,
                        user_id=current_user.id,
                        functionality="veradoc",
                        input_data={
                            "questions": request_data.questions,
                            "document_name": file.filename,
                            "kb_id": request_data.knowledge_base_id,
                            "search_mode": request_data.search_mode,
                            "multi_file_batch": len(files) > 1,
                            "file_index": file_index + 1,
                            "total_files": len(files),
                            "optimization_applied": True,
                        },
                        output_data={
                            "final_evaluation": final_evaluation,
                            "qa_count": len(qa_pairs),
                        },
                        metadata={
                            "qa_pairs": qa_pairs
                        },
                    )
                except Exception as interaction_error:
                    print(f"Error recording interaction for {file.filename}: {interaction_error}")
                    interaction_id = None

                # Store results for this file
                file_result = {
                    "filename": file.filename,
                    "final_evaluation": final_evaluation,
                    "qa_pairs": qa_pairs,
                    "interaction_id": str(interaction_id) if interaction_id else None,
                }
                all_files_results.append(file_result)

            # 10. Return results based on number of files processed
            if len(all_files_results) == 0:
                raise HTTPException(status_code=400, detail="No files were successfully processed")
            
            # Return optimized multi-file response
            if len(all_files_results) > 1:
                # Multiple files: return optimized format with all results
                return VeraDocResponse(
                    results={
                        "multi_file_results": all_files_results,
                        "total_files_processed": len(all_files_results),
                        "optimization_applied": True,
                        "context_prefetch_count": len(question_contexts),
                        "search_mode": request_data.search_mode,
                        # For backward compatibility, include first file's data at root level
                        "filename": all_files_results[0]["filename"],
                        "final_evaluation": all_files_results[0]["final_evaluation"],
                        "qa_pairs": all_files_results[0]["qa_pairs"],
                        "interaction_id": all_files_results[0]["interaction_id"],
                    }
                )
            else:
                # Single file: return traditional format for compatibility
                return VeraDocResponse(
                    results={
                        **all_files_results[0],
                        "optimization_applied": True,
                        "context_prefetch_count": len(question_contexts),
                        "search_mode": request_data.search_mode,
                    }
                )

    except Exception as e:
        print("Error processing RAG checklist:")
        print(str(e))

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing RAG checklist: {str(e)}"
        )


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


@router.delete("/evaluations/{evaluation_id}", response_model=Message)
def delete_evaluation(
    evaluation_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
):
    """
    Delete an evaluation/report by ID.
    """
    evaluation = session.get(LlmInteraction, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found.")

    # Ensure the current user is the owner of the evaluation
    if evaluation.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this evaluation."
        )

    # Only allow deletion of veradoc evaluations
    if evaluation.functionality != "veradoc":
        raise HTTPException(status_code=400, detail="Invalid evaluation type.")

    session.delete(evaluation)
    session.commit()
    return Message(message="Evaluation deleted successfully.")


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
    # Disconnect monitoring disabled due to false positives

    try:
        print("Starting checklist optimization...")

        # 1. Retrieve knowledge base
        kb = session.get(KnowledgeBase, request_data.knowledge_base_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # 2. Set up the same infrastructure as process_rag_checklist
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract ChromaDB
            if kb.storage_type == "file" and kb.file_path:
                # File-based storage: extract from file path
                if os.path.exists(kb.file_path):
                    with zipfile.ZipFile(kb.file_path, "r") as zip_ref:
                        zip_ref.extractall(temp_dir)
                else:
                    raise HTTPException(
                        status_code=400, detail="Knowledge base file not found on disk"
                    )
            elif kb.data:
                # Database storage: extract from data field
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

            # Create retriever based on search mode
            if request_data.search_mode == "full_scan":
                print("Using full document scan mode for optimization")

                # Create a simple retriever that returns all documents
                class FullScanRetriever:
                    def __init__(self, chroma_db):
                        self.chroma_db = chroma_db

                    def get_relevant_documents(self, query):
                        try:
                            all_data = self.chroma_db.get()
                            documents = []

                            if (
                                all_data
                                and "documents" in all_data
                                and all_data["documents"]
                            ):
                                for i, doc_content in enumerate(all_data["documents"]):
                                    metadata = (
                                        all_data["metadatas"][i]
                                        if "metadatas" in all_data
                                        and i < len(all_data["metadatas"])
                                        else {}
                                    )
                                    documents.append(
                                        LangchainDocument(
                                            page_content=doc_content, metadata=metadata
                                        )
                                    )

                            return documents
                        except Exception as e:
                            print(f"Error in FullScanRetriever: {e}")
                            return []

                retriever = FullScanRetriever(chroma_db)
            else:
                print("Using enhanced vector search mode for optimization")
                retriever = SmartRetrieverFactory.create_academic_paper_retriever(
                    chroma_db=chroma_db,
                    search_kwargs={"k": settings.RAG_NUM_CHUNKS},
                )

            # Initialize LLM
            llm = get_default_llm(session, current_user)

            # 3. Process the test document
            file = files[0]
            content = await file.read()
            document_text = await extract_text_from_file_async(content, file.filename)
            print(
                f"Processing test document: {file.filename} ({len(document_text)} characters)"
            )

            # For large files or DOCX files, cancel disconnect monitoring to prevent false positives
            is_docx = file.filename.lower().endswith((".docx", ".doc"))
            large_document_threshold = (
                100000 if is_docx else 200000
            )  # Lower threshold for DOCX

            if len(document_text) > large_document_threshold or (
                is_docx and len(content) > 50000
            ):
                print(
                    f"Large document detected ({file.filename}), disabling disconnect monitoring to prevent false positives"
                )
                if disconnect_monitor:
                    disconnect_monitor.cancel()
                    disconnect_monitor = None

            # 4. Run the review process with current questions
            question_list = request_data.questions.strip().split("\n")
            qa_results = []

            context_prompt_template = settings.VERADOC_CONTEXT_PROMPT_TEMPLATE
            qa_prompt_template = settings.VERADOC_QA_PROMPT_TEMPLATE
            optimize_prompt_template = settings.VERADOC_OPTIMIZE_PROMPT_TEMPLATE

            print(f"Evaluating {len(question_list)} questions...")

            for question in question_list:

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

                # Translate the question context if needed
                question_context = await translate_text_if_needed(
                    question_context, session, current_user, llm
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
                    # Add policy context to the suggestion
                    suggestion.policy_context = qa["context"]
                    suggestions.append(suggestion)
                else:
                    # Question is already working well
                    suggestion = ChecklistSuggestion(
                        original_question=qa["question"],
                        suggested_question=qa["question"],
                        reason="Question already generates positive responses",
                        current_answer=qa["answer"],
                        needs_revision=False,
                        policy_context=qa["context"],
                    )
                    suggestions.append(suggestion)

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
                            # Remove prefixes using more robust logic
                            if "_" in source_name:
                                parts = source_name.split("_")
                                if len(parts) > 1:
                                    first_part = parts[0]
                                    # If first part is short and alphanumeric (likely a prefix), remove it
                                    if len(first_part) <= 10 and first_part.isalnum():
                                        source_name = "_".join(parts[1:])
                                    # Otherwise keep the original filename
                                    # This prevents removing legitimate parts of the filename

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
                "Policy Context",
                "Current Answer",
                "Reason",
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
                policy_context = suggestion.get("policy_context", "")

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
                policy_context_clean = policy_context.replace("\n", " ").replace(
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
                        policy_context_clean,
                        current_answer_clean,
                        reason_clean,
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


@router.post("/generate-questions-with-files", response_model=GenerateQuestionsResponse)
async def generate_questions_with_files(
    session: SessionDep,
    current_user: CurrentUser,
    description: str = Form(...),
    checklist_type: str = Form(default="general"),
    num_questions: Optional[int] = Form(default=None),
    files: List[UploadFile] = File(default=[]),
):
    """
    Generate checklist questions based on a description using LLM, with optional reference documents.
    """
    from app.services.text_processing import chunk_text
    from app.core.config import settings

    try:
        # Get the default LLM
        llm = get_default_llm(session, current_user)

        # Process uploaded files to extract reference document content
        reference_document_content = ""
        if files:
            print(f"Processing {len(files)} uploaded files for question generation")

            for file in files:
                if file.size > 0:
                    try:
                        # Read and process the file content with visual enhancement
                        file_content = await file.read()

                        # Use enhanced processing with vision capabilities
                        from app.services.document_utils import (
                            extract_text_with_vision_enhancement,
                        )

                        file_text = await extract_text_with_vision_enhancement(
                            file_content,
                            file.filename or "unknown",
                            llm,
                            purpose="checklist question generation",
                        )

                        if file_text.strip():
                            reference_document_content += f"\n\n--- Content from {file.filename} ---\n{file_text.strip()}"
                            print(
                                f"Extracted {len(file_text)} characters from {file.filename} (with vision enhancement)"
                            )

                    except Exception as e:
                        print(f"Error processing file {file.filename}: {str(e)}")
                        # Add the error info to the document content so user knows what happened
                        reference_document_content += f"\n\n--- Error processing {file.filename} ---\nError: {str(e)}\n"
                        continue

        # Check if content exceeds token limits and chunk if necessary
        if reference_document_content:
            print(
                f"Total document content: {len(reference_document_content)} characters"
            )

            # Using conservative chunking similar to TWINCHECK settings
            max_chunk_size = 80000  # Conservative chunk size for 128K context limit

            if len(reference_document_content) > max_chunk_size:
                print(
                    f"Document too large ({len(reference_document_content)} chars), chunking for processing"
                )

                # Chunk the document content
                chunks = chunk_text(
                    reference_document_content, max_tokens=max_chunk_size
                )

                # Process each chunk to generate questions
                all_chunk_questions = []

                for i, chunk in enumerate(chunks):
                    print(f"Processing chunk {i+1}/{len(chunks)}")

                    # Generate questions for this chunk
                    chunk_prompt_variables = {
                        "description": description,
                        "checklist_type": checklist_type,
                        "reference_documents_instruction": "You can find additional requirements in the reference documents provided below.",
                        "reference_documents_content": chunk,
                        "additional_instructions": "\n11. Use the reference documents provided below to identify additional requirements that should be included in the checklist questions",
                    }

                    try:
                        chunk_response = invoke_llm(
                            llm,
                            settings.VERADOC_GENERATE_QUESTIONS_PROMPT_TEMPLATE,
                            chunk_prompt_variables,
                        )

                        # Parse questions from chunk response
                        chunk_questions = []
                        lines = chunk_response.strip().split("\n")
                        in_questions_section = False

                        for line in lines:
                            line = line.strip()
                            if line.startswith("QUESTIONS:"):
                                in_questions_section = True
                                continue
                            elif line.startswith("ANALYSIS:"):
                                in_questions_section = False
                                continue

                            if in_questions_section:
                                if re.match(r"^\d+\.\s+", line):
                                    question = re.sub(r"^\d+\.\s+", "", line)
                                    if question.strip():
                                        chunk_questions.append(question.strip())

                        # If parsing failed, try simpler approach
                        if not chunk_questions:
                            for line in lines:
                                line = line.strip()
                                if re.match(r"^\d+\.\s+", line):
                                    question = re.sub(r"^\d+\.\s+", "", line)
                                    if question.strip():
                                        chunk_questions.append(question.strip())

                        all_chunk_questions.extend(chunk_questions)

                    except Exception as e:
                        print(f"Error processing chunk {i+1}: {e}")
                        continue

                # Deduplicate and refine questions across all chunks
                if all_chunk_questions:
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_questions = []
                    for q in all_chunk_questions:
                        if q.lower() not in seen:
                            seen.add(q.lower())
                            unique_questions.append(q)

                    # If we have too many questions, synthesize and prioritize
                    if len(unique_questions) > (num_questions or 50):
                        synthesis_prompt_variables = {
                            "description": description,
                            "checklist_type": checklist_type,
                            "questions_list": "\n".join(
                                [f"{i+1}. {q}" for i, q in enumerate(unique_questions)]
                            ),
                            "num_questions": num_questions or 20,
                        }

                        synthesis_prompt = f"""From the following list of checklist questions, select and refine the {num_questions or 20} most important and relevant questions for {checklist_type} verification based on: {description}

Questions to review:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(unique_questions)])}

Requirements:
1. Select the most critical and actionable questions
2. Ensure no redundancy
3. Maintain clarity and specificity
4. Focus on questions most relevant to the description

Return only the final selected questions, one per line, numbered."""

                        try:
                            refined_response = invoke_llm(llm, synthesis_prompt, {})
                            questions = []
                            for line in refined_response.strip().split("\n"):
                                line = line.strip()
                                if line and (
                                    line[0].isdigit()
                                    or line.startswith("-")
                                    or line.startswith("*")
                                ):
                                    question = re.sub(r"^\d+\.\s+", "", line)
                                    question = re.sub(r"^[-*]\s+", "", question)
                                    if question.strip():
                                        questions.append(question.strip())
                        except Exception as e:
                            print(f"Error in question synthesis: {e}")
                            questions = unique_questions[: num_questions or 20]
                    else:
                        questions = unique_questions[: num_questions or 20]

                    # For analysis, show chunked processing was used
                    analysis = f"Generated {len(questions)} questions from chunked document analysis ({len(chunks)} chunks processed) based on the provided description to ensure comprehensive evaluation coverage."

                    # Record the interaction
                    record_llm_interaction(
                        session=session,
                        user_id=current_user.id,
                        functionality="generate_checklist_questions",
                        input_data={
                            "description": description,
                            "requested_questions": num_questions,
                            "checklist_type": checklist_type,
                            "chunked_processing": True,
                            "chunk_count": len(chunks),
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
                else:
                    # Fallback to description-only generation if chunk processing failed
                    reference_document_content = ""

        # Continue with existing logic for small documents or when no files provided
        if reference_document_content:
            reference_documents_instruction = "You can find additional requirements in the reference documents provided below."
            additional_instructions = "\n11. Use the reference documents provided below to identify additional requirements that should be included in the checklist questions"
        else:
            reference_documents_instruction = ""
            reference_document_content = ""
            additional_instructions = ""

        prompt_variables = {
            "description": description,
            "checklist_type": checklist_type,
            "reference_documents_instruction": reference_documents_instruction,
            "reference_documents_content": reference_document_content,
            "additional_instructions": additional_instructions,
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
        if num_questions:
            questions = questions[:num_questions]

        if not analysis:
            analysis = f"Generated {len(questions)} questions based on the provided description to ensure comprehensive evaluation coverage."

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="generate_checklist_questions",
            input_data={
                "description": description,
                "requested_questions": num_questions,
                "checklist_type": checklist_type,
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


@router.post("/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_questions(
    session: SessionDep, current_user: CurrentUser, request: GenerateQuestionsRequest
):
    """
    Generate checklist questions based on a description using LLM (JSON version).
    Optionally uses a knowledge base as reference for generating questions.
    """
    try:
        # Get the default LLM
        llm = get_default_llm(session, current_user)

        # Handle optional description
        description = request.description or ""

        # Prepare variables for the prompt
        prompt_variables = {
            "description": description,
            "checklist_type": request.checklist_type or "general",
            "reference_documents_instruction": "",
            "reference_documents_content": "",
            "additional_instructions": "",
        }

        # If knowledge base is provided, retrieve content using selected search mode
        if request.knowledge_base_id:
            try:
                from app.services.content_retrieval import (
                    retrieve_knowledge_base_content,
                )

                print(
                    f"Retrieving knowledge base content for KB ID: {request.knowledge_base_id}, search mode: {request.search_mode}"
                )
                content, instruction = await retrieve_knowledge_base_content(
                    session=session,
                    current_user=current_user,
                    knowledge_base_id=request.knowledge_base_id,
                    search_mode=request.search_mode,
                    query=description,
                )

                if content:
                    print(
                        f"Successfully retrieved KB content: {len(content)} characters"
                    )
                    prompt_variables["reference_documents_content"] = content
                    prompt_variables["reference_documents_instruction"] = (
                        f"{instruction} The questions should be relevant to the description while also "
                        f"considering the content and requirements found in these reference documents. "
                        f"Search mode used: {request.search_mode}"
                    )
                    prompt_variables["additional_instructions"] = (
                        "\n11. Use the reference documents provided below to identify additional requirements that should be included in the checklist questions"
                    )
                else:
                    print("Warning: No content retrieved from knowledge base")

            except Exception as e:
                print(f"Error retrieving knowledge base documents: {e}")
                import traceback

                traceback.print_exc()
                # Continue without reference documents if there's an error
                pass

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
        if request.num_questions:
            questions = questions[: request.num_questions]

        if not analysis:
            search_method = (
                "vector search"
                if request.search_mode == "vector"
                else "full document scan"
            )
            analysis = f"Generated {len(questions)} checklist questions based on the provided description using {search_method}"
            if request.knowledge_base_id:
                analysis += " with knowledge base reference."

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="generate_checklist_questions",
            input_data={
                "description": request.description,
                "checklist_type": request.checklist_type,
                "requested_questions": request.num_questions,
                "knowledge_base_id": request.knowledge_base_id,
                "search_mode": request.search_mode,
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
