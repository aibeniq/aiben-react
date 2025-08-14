import uuid
import json
import csv
import tempfile
import os
import markdown
from pathlib import Path
from io import BytesIO, StringIO
from datetime import datetime
from fastapi.responses import StreamingResponse
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from bs4 import BeautifulSoup
from app.models import (
    FormConnectRequest,
    FormConnectResponse,
    FormConnectForm,
    FormConnectDetailResponse,
    GenerateFormFieldsRequest,
    GenerateFormFieldsResponse,
    DocxRequest,
    LlmInteraction,
    Message,
    KnowledgeBase,
    EmbeddingModel,
)
from app.services.llms import (
    get_default_llm,
    invoke_llm,
    invoke_llm_with_image,
    record_llm_interaction,
)
from app.services.translation import translate_text_if_needed
from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings

from sqlmodel import Session, select
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Dict, Any, Literal
import re
import traceback

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage
from dotenv import load_dotenv

from app.services.embeddings import load_embeddings_model
from app.services.knowledgebases import get_embedding_model
from app.services.retrievers import create_ensemble_retriever

import base64
from tempfile import NamedTemporaryFile

# import fitz  # PyMuPDF - Removed for commercial licensing
from app.services.pdf_utils import load_pdf_with_pypdf

from datetime import datetime

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

router = APIRouter(prefix="/formconnect", tags=["formconnect"])


def generate_template(fields: List[str]) -> Dict[str, str]:
    """
    Generate a JSON template from a list of fields.
    Each field will have a blank value.
    """
    return {field: "" for field in fields}


async def extract_fields_from_digitized_document(
    file: UploadFile, template: Dict[str, str], llm=None, search_mode: str = "full_scan"
) -> Dict[str, str]:
    """
    Extract fields from a document using the LLM.
    Supports both full text processing and vector search modes.
    """
    # Read the file content
    content = await file.read()

    if search_mode == "vector":
        # TRUE VECTOR SEARCH IMPLEMENTATION
        return await extract_fields_using_vector_search(file, content, template, llm)
    else:
        # FULL TEXT MODE (existing implementation)
        return await extract_fields_using_full_text(
            content, file.filename, template, llm
        )


async def extract_fields_using_vector_search(
    file: UploadFile, content: bytes, template: Dict[str, str], llm=None
) -> Dict[str, str]:
    """
    Extract fields using vector search to find relevant document sections.
    Uses a temporary ChromaDB instance to perform semantic search.
    """
    try:
        import tempfile
        import shutil
        from langchain_community.vectorstores import Chroma
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from app.services.embeddings import load_embeddings_model
        from app.services.knowledgebases import get_embedding_model
        from app.services.retrievers import create_ensemble_retriever

        print(f"🔍 Using vector search mode for field extraction from {file.filename}")

        # Get embedding model
        from app.api.deps import get_session

        session = next(get_session())
        embedding_info = get_embedding_model(session)

        if not embedding_info:
            print("❌ No embedding model available, falling back to full text mode")
            return await extract_fields_using_full_text(
                content, file.filename, template, llm
            )

        print(
            f"Using embedding model: {embedding_info['model_id']} ({embedding_info['provider']})"
        )

        # Extract text from the document first using unified processing
        from app.services.document_utils import extract_text_from_file_unified

        text = extract_text_from_file_unified(content, file.filename or "unknown")

        if not text.strip():
            return {k: "Could not extract: Empty document" for k in template.keys()}

        # Create temporary directory for ChromaDB
        temp_dir = tempfile.mkdtemp()

        try:
            # Load embedding model
            embeddings = load_embeddings_model(
                provider=embedding_info["provider"], model_id=embedding_info["model_id"]
            )

            # Split text into chunks for vector storage
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.RAG_DOCUMENT_CHUNK_SIZE,
                chunk_overlap=settings.RAG_DOCUMENT_CHUNK_OVERLAP,
                length_function=len,
            )
            chunks = text_splitter.split_text(text)

            print(f"📄 Split document into {len(chunks)} chunks for vector search")

            # Create ChromaDB vector store
            chroma_db = Chroma.from_texts(
                texts=chunks,
                embedding=embeddings,
                persist_directory=temp_dir,
                metadatas=[
                    {"source": file.filename, "chunk_id": i} for i in range(len(chunks))
                ],
            )

            # Create retriever for semantic search
            retriever = create_ensemble_retriever(
                chroma_db=chroma_db,
                vector_weight=0.8,  # Higher weight for vector search in FormConnect
                keyword_weight=0.2,
                search_kwargs={"k": settings.FORMCONNECT_VECTOR_SEARCH_CHUNKS},
            )

            # Extract fields using vector search
            extracted_data = {}
            field_count = len(template)

            print(f"🔎 Extracting {field_count} fields using vector search...")

            for i, (field_name, field_description) in enumerate(template.items(), 1):
                print(f"[{i}/{field_count}] Searching for: {field_name}")

                # Create search query combining field name and description
                search_query = f"{field_name} {field_description}".strip()

                try:
                    # Retrieve relevant chunks
                    relevant_docs = retriever.invoke(search_query)

                    if relevant_docs:
                        # Combine relevant text from retrieved chunks
                        relevant_chunks = []
                        total_tokens = 0

                        for doc in relevant_docs:
                            chunk_text = doc.page_content
                            chunk_tokens = count_tokens(chunk_text)

                            # Limit total context to avoid token limits
                            if (
                                total_tokens + chunk_tokens > 10000
                            ):  # Conservative limit
                                break

                            relevant_chunks.append(chunk_text)
                            total_tokens += chunk_tokens

                        relevant_text = "\n\n".join(relevant_chunks)

                        if relevant_text.strip():
                            # Create field-specific extraction prompt
                            field_prompt = f"""Extract the value for "{field_name}" from the following text.

Field description: {field_description}

Relevant text:
{relevant_text}

Instructions:
1. Look for the specific information related to "{field_name}"
2. If found, return only the extracted value
3. If not found, return "Not found"
4. Be precise and concise

Extracted value:"""

                            # Extract field value using LLM
                            field_response = invoke_llm(llm, field_prompt, {})
                            extracted_value = (
                                field_response.content
                                if hasattr(field_response, "content")
                                else str(field_response)
                            )
                            extracted_data[field_name] = extracted_value.strip()

                            print(f"   ✅ Found: {extracted_value.strip()[:50]}...")
                        else:
                            extracted_data[field_name] = "Not found"
                            print(f"   ❌ No relevant content found")
                    else:
                        extracted_data[field_name] = "Not found"
                        print(f"   ❌ No search results")

                except Exception as e:
                    print(f"   ❌ Error searching for {field_name}: {str(e)}")
                    extracted_data[field_name] = f"Error: {str(e)}"

            print("✅ Vector search extraction completed")
            return extracted_data

        finally:
            # Cleanup temporary directory
            try:
                shutil.rmtree(temp_dir)
                print(f"🧹 Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                print(f"Warning: Could not cleanup temporary directory: {str(e)}")

    except Exception as e:
        print(f"❌ Vector search failed: {str(e)}. Falling back to full text mode.")
        return await extract_fields_using_full_text(
            content, file.filename, template, llm
        )


async def extract_fields_using_full_text(
    content: bytes, filename: str, template: Dict[str, str], llm=None
) -> Dict[str, str]:
    """
    Extract fields using full text processing (original method).
    """
    print(f"📄 Using full text mode for field extraction from {filename}")

    # Check file extension to determine processing method
    file_ext = Path(filename).suffix.lower() if filename else ""

    try:
        # Use unified document processing for all file types
        from app.services.document_utils import extract_text_from_file_unified

        text = extract_text_from_file_unified(content, filename)

        if not text.strip():
            return {
                k: f"Could not extract: Empty document {filename}"
                for k in template.keys()
            }

        # Check token count and implement chunking if needed
        token_count = count_tokens(text + json.dumps(template))

        if token_count > 150000:  # Token limit safety
            print(
                f"⚠️ Large document detected ({token_count} tokens), implementing chunking..."
            )
            return await extract_fields_with_chunking(text, template, llm)

    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
        return {
            k: f"Could not extract: Error processing {filename} - {str(e)}"
            for k in template.keys()
        }

    # Create the prompt for full text extraction
    prompt_template = settings.FORMCONNECT_DIGITIZED_PROMPT_TEMPLATE
    variables = {"template": json.dumps(template), "document_text": text}
    response = invoke_llm(llm, prompt_template, variables)

    # Try to parse JSON from the response
    try:
        # The output might already be a dictionary
        if isinstance(response, dict):
            return response
        content_dict = json.loads(response)
        return content_dict
    except Exception:
        return {"raw_content": str(response)}


def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens in text for the given model."""
    try:
        import tiktoken

        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except KeyError:
        # Fallback to cl100k_base for unknown models
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))


async def extract_fields_with_chunking(
    document_text: str, template: Dict[str, str], llm=None
) -> Dict[str, str]:
    """
    Extract fields from large documents using chunking.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    print("🔄 Processing large document with chunking...")

    # Create chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=50000,  # Conservative chunk size
        chunk_overlap=200,
        length_function=len,
    )

    chunks = splitter.split_text(document_text)
    print(f"📄 Split document into {len(chunks)} chunks")

    all_extractions = []

    # Process each chunk
    for i, chunk in enumerate(chunks):
        print(f"[{i+1}/{len(chunks)}] Processing chunk ({count_tokens(chunk)} tokens)")

        try:
            prompt_template = settings.FORMCONNECT_DIGITIZED_PROMPT_TEMPLATE
            variables = {"template": json.dumps(template), "document_text": chunk}
            response = invoke_llm(llm, prompt_template, variables)

            try:
                if isinstance(response, dict):
                    chunk_extraction = response
                else:
                    chunk_extraction = json.loads(response)
                all_extractions.append(chunk_extraction)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from chunk {i+1}: {e}")
                continue

        except Exception as e:
            print(f"Error processing chunk {i+1}: {str(e)}")
            continue

    # Merge extractions from all chunks
    return merge_field_extractions(all_extractions, template)


def merge_field_extractions(
    extractions: list, template: Dict[str, str]
) -> Dict[str, str]:
    """
    Merge field extractions from multiple document chunks.
    """
    if not extractions:
        return {k: "Not found" for k in template.keys()}

    if len(extractions) == 1:
        return extractions[0]

    # Start with the template structure
    merged = {k: "Not found" for k in template.keys()}

    # For each field, take the first non-empty value found
    for extraction in extractions:
        for field, value in extraction.items():
            if field in merged and value and str(value).strip():
                # Only update if current value is empty/placeholder
                current_value = str(merged[field]).strip()
                if current_value.lower() in ["not found", "", "n/a", "null", "none"]:
                    merged[field] = value

    return merged


async def extract_fields_from_handwritten_document(
    file: UploadFile, template: Dict[str, str], llm
) -> Dict[str, str]:
    """
    Extract fields from a handwritten document.
    """
    print("Now extracting fields from handwritten document:", file.filename)
    content = await file.read()

    # Define image file extensions
    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp",
    ]
    file_ext = Path(file.filename).suffix.lower()

    # Check if the file is an image
    if file_ext in image_extensions:
        try:
            img_base64 = base64.b64encode(content).decode("utf-8")

            # Use the template from config
            prompt_template = settings.FORMCONNECT_HANDWRITTEN_PROMPT_TEMPLATE
            variables = {"template": template}

            print("Now invoking LLM with base-encoded image...")
            response = invoke_llm_with_image(
                llm,
                prompt_template,
                variables=variables,
                image_base64=img_base64,
                image_type=file_ext[1:] if file_ext.startswith(".") else file_ext,
            )

            # Try to parse JSON from the response
            try:
                import json

                if isinstance(response, dict):
                    return response
                content_dict = json.loads(response)
                return content_dict
            except Exception:
                return {"raw_content": str(response)}
        except Exception as e:
            return {k: f"Error processing image: {str(e)}" for k in template.keys()}

    # Fallback for non-image files
    await file.seek(0)
    return await extract_fields_from_digitized_document(
        file, template, llm, "full_scan"
    )


async def compare_multiple_documents(
    documents: List[Dict[str, str]], file_names: List[str], llm, current_user, session
) -> str:
    """
    Compare fields across multiple documents using the LLM.
    """
    # Create a combined representation of all documents WITH ACTUAL FILENAMES
    documents_str = ""
    clean_filenames = []

    for i, (doc, name) in enumerate(zip(documents, file_names)):
        # Clean the filename (remove " (digitized)" or " (handwritten)" suffix)
        clean_filename = name.replace(" (digitized)", "").replace(" (handwritten)", "")
        clean_filenames.append(clean_filename)

        # Convert dict to string, escaping any curly braces for the formatter
        doc_str = str(doc).replace("{", "{{").replace("}", "}}")
        documents_str += f"Document: {clean_filename}\nExtracted Data: {doc_str}\n\n"

    print(
        "documents_str for comparison:", documents_str[:500]
    )  # Print first 500 chars for debugging

    # Create an enhanced prompt that explicitly instructs the LLM to use actual filenames
    enhanced_prompt_template = """Compare the extracted fields across the following documents and provide a detailed analysis.

IMPORTANT: When referring to documents in your analysis and tables, use the actual document filenames provided below, NOT generic labels like "Document 1", "Document 2", etc.

Document Filenames:
{filename_list}

Documents to compare:
{documents_str}

Instructions:
1. Create a comparison table showing field values across all documents
2. Use the actual document filenames as column headers in any tables
3. Identify discrepancies and highlight the most likely correct values
4. Provide a summary of findings
5. If creating markdown tables, use the document filenames as column headers

Format your response in markdown with clear tables and analysis."""

    variables = {
        "documents_str": documents_str,
        "filename_list": "\n".join([f"- {name}" for name in clean_filenames]),
    }
    response = invoke_llm(llm, enhanced_prompt_template, variables)
    # Translate the response if needed
    translated_response = await translate_text_if_needed(
        response, session, current_user, llm
    )
    return translated_response


@router.post("/process", response_model=FormConnectResponse)
async def process_form(
    session: SessionDep,
    current_user: CurrentUser,
    fields: str,
    search_mode: Literal["vector", "full_scan"] = "vector",
    digitized_files: List[UploadFile] = File(None),
    handwritten_files: List[UploadFile] = File(None),
):
    """
    Process the uploaded files and fields.

    Handles two types of files:
    - digitized_files: Standard text extraction
    - handwritten_files: OCR-based extraction (placeholder)
    """
    print("process_form function invoked!")
    print(f"Received search_mode: {search_mode}")
    print(f"Request data: fields={fields[:50]}...")

    # Get the default LLM
    llm = get_default_llm(session, current_user)

    # Log the model type being used
    if hasattr(llm, "__class__") and "ReplicateWrapper" in llm.__class__.__name__:
        print(
            f"Using Replicate model for FormConnect: {getattr(llm, 'model_id', 'unknown')}"
        )
    else:
        print(f"Using LangChain model for FormConnect: {type(llm).__name__}")

    total_files = (len(digitized_files) if digitized_files else 0) + (
        len(handwritten_files) if handwritten_files else 0
    )
    print(
        f"Now processing {total_files} files ({len(digitized_files) if digitized_files else 0} digitized, {len(handwritten_files) if handwritten_files else 0} handwritten)..."
    )

    # Check if we have at least one file
    if total_files < 1:
        raise HTTPException(
            status_code=400, detail="At least one file must be uploaded."
        )

    # Parse the fields into a list
    field_list = fields.splitlines()

    if not field_list:
        raise HTTPException(status_code=400, detail="No fields provided.")

    # Generate the JSON template
    template = generate_template(field_list)

    # Extract fields from all documents
    extracted_results = []
    file_names = []

    # Process digitized files using the existing function
    if digitized_files:
        for file in digitized_files:
            extracted = await extract_fields_from_digitized_document(
                file, template, llm, search_mode
            )

            print("Results for file name:", file.filename)
            print("Extracted fields:", extracted)
            extracted_results.append(extracted)
            file_names.append(f"{file.filename} (digitized)")

            # Reset file position for potential future reads
            await file.seek(0)

    # Process handwritten files using a specialized function (placeholder)
    if handwritten_files:
        for file in handwritten_files:
            extracted = await extract_fields_from_handwritten_document(
                file, template, llm
            )
            extracted_results.append(extracted)

            print("Results for file name:", file.filename)
            print("Extracted fields:", extracted)

            file_names.append(f"{file.filename} (handwritten)")

            # Reset file position for potential future reads
            await file.seek(0)

    # If there's only one file, we can't do comparison
    if total_files == 1:
        result = {
            "message": "Only one document provided. No comparison performed.",
            "extracted_data": extracted_results[0],
        }
    else:
        # Compare the extracted fields
        comparison_result = await compare_multiple_documents(
            extracted_results, file_names, llm, current_user, session
        )
        result = {
            "message": "Documents compared successfully",
            "comparison": comparison_result,
            "extracted_data": extracted_results,
        }

    interaction_id = record_llm_interaction(
        session=session,
        user_id=current_user.id,
        functionality="formconnect",
        input_data={"fields": fields, "files": file_names, "search_mode": search_mode},
        output_data=result,
        metadata={
            "file_count": total_files,
            "field_count": len(field_list),
            "document_count": total_files,
            "digitized_files": (
                [f.filename for f in digitized_files] if digitized_files else []
            ),
            "handwritten_files": (
                [f.filename for f in handwritten_files] if handwritten_files else []
            ),
            "fields": field_list,
            "search_mode": search_mode,
        },
    )

    print(f"[DEBUG] FormConnect interaction_id returned: {interaction_id}")
    # Add interaction_id to the result
    result["interaction_id"] = str(interaction_id) if interaction_id else None
    print(
        f"[DEBUG] FormConnect result with interaction_id: {result.get('interaction_id')}"
    )

    # Return the comparison results as a dictionary
    return FormConnectResponse(results=result)


# Functions related to Forms
@router.post("/forms", response_model=FormConnectForm)
def create_form(
    form: FormConnectForm,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Save a new form to the database.
    """
    existing_form = session.exec(
        select(FormConnectForm).where(FormConnectForm.name == form.name)
    ).first()
    if existing_form:
        raise HTTPException(
            status_code=400, detail="A form with this name already exists."
        )

    form.owner_id = current_user.id
    session.add(form)
    session.commit()
    session.refresh(form)
    return form


@router.get("/forms", response_model=List[FormConnectForm])
def get_forms(session: SessionDep, current_user: CurrentUser):
    """
    Retrieve all forms from the database for this user.
    """
    return session.exec(
        select(FormConnectForm).where(FormConnectForm.owner_id == current_user.id)
    ).all()


@router.get("/forms/{form_id}", response_model=FormConnectForm)
def get_form(form_id: uuid.UUID, session: SessionDep):
    """
    Retrieve a specific form by ID.
    """
    form = session.get(FormConnectForm, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    return form


@router.put("/forms/{form_id}", response_model=FormConnectForm)
def update_form(
    form_id: uuid.UUID,
    updated_form: FormConnectForm,
    session: SessionDep,
    current_user: CurrentUser,
):
    """
    Update an existing form.
    """
    form = session.get(FormConnectForm, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    # Ensure the current user is the owner of the form
    if form.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this form."
        )

    form.name = updated_form.name
    form.description = updated_form.description
    form.fields = updated_form.fields
    form.date_modified = datetime.utcnow()

    session.add(form)
    session.commit()
    session.refresh(form)
    return form


@router.delete("/forms/{form_id}", response_model=Message)
def delete_form(form_id: uuid.UUID, session: SessionDep, current_user: CurrentUser):
    """
    Delete a form by ID.
    """
    form = session.get(FormConnectForm, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    # Ensure the current user is the owner of the form
    if form.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this form."
        )

    session.delete(form)
    session.commit()
    return Message(message="Form deleted successfully.")


# Add this new endpoint to get history details for a specific form processing
@router.get("/history/{interaction_id}", response_model=FormConnectDetailResponse)
async def get_form_detail(
    interaction_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
):
    """Retrieve a specific form processing's full content by ID."""
    print("Received interaction ID:", interaction_id)
    try:
        report = session.get(LlmInteraction, interaction_id)
        if not report:
            raise HTTPException(
                status_code=404, detail="Form processing result not found"
            )

        # No longer need to check this as we now allow viewing other users' outputs
        # if report.user_id != current_user.id:
        #    raise HTTPException(
        #        status_code=403, detail="You don't have access to this form processing"
        #    )

        if report.functionality != "formconnect":
            raise HTTPException(
                status_code=400, detail="This is not a FormConnect processing"
            )

        # Try to reconstruct the original form processing structure
        try:
            input_data = json.loads(report.input_data) if report.input_data else {}
            output_data = json.loads(report.output_data) if report.output_data else {}

            # Create a response that matches the structure expected by the frontend
            result = {
                "id": str(report.id),
                "date_created": report.date_created,
                "fields": input_data.get("fields", ""),
                "file_names": input_data.get("files", []),
                "results": output_data,
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
                    "message": f"Unable to reconstruct form processing from {report.date_created}.\n\n"
                    f"This might be due to an older format or incomplete data."
                },
                # Add empty feedback object for consistency
                "feedback": {
                    "feedback": None,
                    "feedbackText": None,
                    "feedbackDate": None,
                },
            }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving form processing details: {str(e)}",
        )


# Also add a history endpoint to get a list of past form processing operations
@router.get("/history", response_model=List[Dict[str, Any]])
async def get_form_history(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 20,
    show_all: bool = False,
):
    """Retrieve past form processing history for the current user or all users."""
    print("Retrieving FormConnect history. Show all:", show_all)

    try:
        # Start with base query
        query = select(LlmInteraction).where(
            LlmInteraction.functionality == "formconnect"
        )

        # Only filter by user if not showing all users
        if not show_all:
            query = query.where(LlmInteraction.user_id == current_user.id)

        # Add ordering and pagination
        interactions = session.exec(
            query.order_by(LlmInteraction.date_created.desc()).offset(skip).limit(limit)
        ).all()

        result = []
        for interaction in interactions:
            # Parse the input_data and output_data
            try:
                input_data = (
                    json.loads(interaction.input_data) if interaction.input_data else {}
                )
                output_data = (
                    json.loads(interaction.output_data)
                    if interaction.output_data
                    else {}
                )
                # Fix: Use extra_data instead of metadata
                metadata = interaction.extra_data if interaction.extra_data else {}

                file_count = len(input_data.get("files", []))
                fields = input_data.get("fields", "").split("\n")
                field_count = len([f for f in fields if f.strip()])

                # Create result item
                result_item = {
                    "id": str(interaction.id),
                    "date_created": interaction.date_created,
                    "file_names": input_data.get("files", []),
                    "file_count": file_count,
                    "field_count": field_count,
                    "fields": fields,
                    "has_feedback": interaction.feedback is not None,
                    # Add metadata information for enhanced display
                    "metadata": metadata,
                    "digitized_files": metadata.get("digitized_files", []),
                    "handwritten_files": metadata.get("handwritten_files", []),
                    "document_count": metadata.get("document_count", file_count),
                    "search_mode": metadata.get("search_mode", "unknown"),
                }

                # Add feedback information if exists
                if interaction.feedback:
                    result_item["feedback"] = {
                        "feedback": interaction.feedback,
                        "feedbackText": interaction.feedback_text,
                    }

                # Add user info for all-users view
                if show_all:
                    from app.models import User  # Import here to avoid circular imports

                    user = session.get(User, interaction.user_id)
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
                    "id": str(interaction.id),
                    "date_created": interaction.date_created,
                    "file_names": [],
                    "file_count": 0,
                    "field_count": 0,
                    "fields": [],
                    "has_feedback": interaction.feedback is not None,
                    # Add empty metadata for consistency
                    "metadata": {},
                    "digitized_files": [],
                    "handwritten_files": [],
                    "document_count": 0,
                    "search_mode": "unknown",
                }

                # Add user info for all-users view
                if show_all:
                    from app.models import User  # Import here to avoid circular imports

                    user = session.get(User, interaction.user_id)
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
            status_code=500,
            detail=f"Error retrieving form processing history: {str(e)}",
        )


@router.post("/generate-fields", response_model=GenerateFormFieldsResponse)
async def generate_form_fields(
    session: SessionDep, current_user: CurrentUser, request: GenerateFormFieldsRequest
):
    """
    Generate form fields based on a description with optional knowledge base reference.
    """
    try:
        # Get the default LLM
        llm = get_default_llm(session, current_user)

        # Prepare variables for the prompt
        prompt_variables = {
            "description": request.description,
            "example_instruction": "",
            "analysis_instruction": "",
            "analysis_note": "",
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
                    knowledge_base_id=str(request.knowledge_base_id),
                    search_mode=request.search_mode,
                    query=request.description,
                )

                if content:
                    prompt_variables["knowledge_base_content"] = (
                        f"REFERENCE DOCUMENTS FROM KNOWLEDGE BASE:\n{content}"
                    )
                    prompt_variables["knowledge_base_instruction"] = (
                        f"\n11. {instruction} Use them as examples to understand the types of fields "
                        f"that are typically found in similar documents. Search mode used: {request.search_mode}"
                    )
                    prompt_variables["analysis_instruction"] = (
                        f". Briefly mention how the knowledge base content (using {request.search_mode}) influenced the field selection"
                    )

            except Exception as e:
                print(f"Error retrieving from knowledge base: {str(e)}")
                # Continue without knowledge base content rather than failing
                pass

        # Generate fields using the LLM
        fields_response = invoke_llm(
            llm,
            settings.FORMCONNECT_GENERATE_FIELDS_PROMPT_TEMPLATE,
            prompt_variables,
        )

        # Parse the response to extract fields and analysis
        fields = []
        analysis = ""

        lines = fields_response.strip().split("\n")
        in_fields_section = False
        in_analysis_section = False

        for line in lines:
            line = line.strip()
            if line.startswith("FIELDS:"):
                in_fields_section = True
                in_analysis_section = False
                continue
            elif line.startswith("ANALYSIS:"):
                in_fields_section = False
                in_analysis_section = True
                continue

            if in_fields_section:
                # Extract fields (numbered list)
                if re.match(r"^\d+\.\s+", line):
                    field = re.sub(r"^\d+\.\s+", "", line)
                    if field.strip():
                        fields.append(field.strip())
            elif in_analysis_section:
                if line:
                    if analysis:
                        analysis += " " + line
                    else:
                        analysis = line

        # If parsing failed, try simpler approach
        if not fields:
            # Split by lines and look for numbered items
            for line in lines:
                line = line.strip()
                if re.match(r"^\d+\.\s+", line):
                    field = re.sub(r"^\d+\.\s+", "", line)
                    if field.strip():
                        fields.append(field.strip())

        # Ensure we have some fields
        if not fields:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate fields from the description. Please try with a more detailed description.",
            )

        # Apply user-specified limit if provided, otherwise use all generated fields
        if request.num_fields:
            fields = fields[: request.num_fields]

        if not analysis:
            search_method = (
                "vector search"
                if request.search_mode == "vector"
                else "full document scan"
            )
            analysis = f"Generated {len(fields)} form fields based on the provided description using {search_method}"
            if request.knowledge_base_id:
                analysis += " with knowledge base reference."

        # Translate the analysis if needed
        translated_analysis = await translate_text_if_needed(
            analysis, session, current_user, llm
        )

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="generate_form_fields",
            input_data={
                "description": request.description,
                "requested_fields": request.num_fields,
                "knowledge_base_id": (
                    str(request.knowledge_base_id)
                    if request.knowledge_base_id
                    else None
                ),
                "search_mode": request.search_mode,
            },
            output_data={
                "fields_count": len(fields),
                "analysis": translated_analysis,
            },
            metadata={},
        )

        return GenerateFormFieldsResponse(
            fields=fields, description_analysis=translated_analysis
        )

    except Exception as e:
        print(f"Error generating form fields: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error generating form fields: {str(e)}"
        )


@router.post("/generate-fields-json", response_model=GenerateFormFieldsResponse)
async def generate_form_fields_json(
    session: SessionDep, current_user: CurrentUser, request: GenerateFormFieldsRequest
):
    """
    Generate form fields based on a description with optional knowledge base reference (JSON version).
    """
    # This is the same as generate_form_fields but ensures JSON request/response
    return await generate_form_fields(session, current_user, request)


@router.post("/generate/docx", response_class=StreamingResponse)
async def generate_docx(
    session: SessionDep, current_user: CurrentUser, request: DocxRequest
):
    """
    Generate a DOCX file from the FormConnect results content.
    Handles markdown tables with extra care for proper rendering.
    """
    print("Now generating DOCX of FormConnect results...")
    try:
        # Get the markdown content from the request
        if not request.content:
            raise HTTPException(
                status_code=400, detail="FormConnect content is required"
            )

        # Convert markdown to HTML for parsing with tables extension
        html_content = markdown.markdown(
            request.content, extensions=["tables", "extra"]
        )
        soup = BeautifulSoup(html_content, "html.parser")

        print("Markdown content converted to HTML successfully.")
        # Create a new Document
        doc = Document()

        print("Adding title and date to the document...")
        # Add a title
        title_text = (
            request.title
            if hasattr(request, "title") and request.title
            else "Matching Results"
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

        print("Processing content elements with special attention to tables...")
        # Process each element in the soup
        for element in soup.find_all():
            if element.name == "h1":
                doc.add_heading(element.get_text().strip(), level=1)
            elif element.name == "h2":
                doc.add_heading(element.get_text().strip(), level=2)
            elif element.name == "h3":
                doc.add_heading(element.get_text().strip(), level=3)
            elif element.name == "h4":
                doc.add_heading(element.get_text().strip(), level=4)
            elif element.name == "p":
                text = element.get_text().strip()
                if text:  # Only add non-empty paragraphs
                    paragraph = doc.add_paragraph(text)

            elif element.name == "table":
                # Handle tables with extra care for FormConnect markdown tables
                rows = element.find_all("tr")
                if rows:
                    print(f"Adding table with {len(rows)} rows...")

                    # Count maximum columns across all rows
                    max_cols = 0
                    for row in rows:
                        cells = row.find_all(["th", "td"])
                        max_cols = max(max_cols, len(cells))

                    if max_cols > 0:
                        table = doc.add_table(rows=len(rows), cols=max_cols)
                        table.style = "Table Grid"

                        # Set consistent column widths
                        for col in table.columns:
                            col.width = Inches(6.0 / max_cols)

                        for i, row in enumerate(rows):
                            cells = row.find_all(["th", "td"])
                            for j, cell in enumerate(cells):
                                if j < len(table.rows[i].cells):
                                    cell_text = cell.get_text().strip()
                                    table.rows[i].cells[j].text = cell_text

                                    # Make header row bold and centered
                                    if i == 0 or cell.name == "th":
                                        for paragraph in (
                                            table.rows[i].cells[j].paragraphs
                                        ):
                                            paragraph.alignment = (
                                                WD_ALIGN_PARAGRAPH.CENTER
                                            )
                                            for run in paragraph.runs:
                                                run.bold = True

                                    # Handle cell alignment for data rows
                                    elif (
                                        cell_text.isdigit()
                                        or cell_text.replace(".", "")
                                        .replace("-", "")
                                        .isdigit()
                                    ):
                                        # Right-align numeric content
                                        for paragraph in (
                                            table.rows[i].cells[j].paragraphs
                                        ):
                                            paragraph.alignment = (
                                                WD_ALIGN_PARAGRAPH.RIGHT
                                            )

            elif element.name == "ul":
                # Handle unordered lists
                for li in element.find_all("li", recursive=False):
                    text = li.get_text().strip()
                    if text:
                        paragraph = doc.add_paragraph(text, style="List Bullet")

            elif element.name == "ol":
                # Handle ordered lists
                for li in element.find_all("li", recursive=False):
                    text = li.get_text().strip()
                    if text:
                        paragraph = doc.add_paragraph(text, style="List Number")

        print("Saving the document to a BytesIO object...")
        # Save the document to a BytesIO object
        doc_io = BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"formconnect_results_{timestamp}.docx"

        print(f"DOCX file size: {len(doc_io.getvalue())} bytes")

        # Verify the document can be opened (basic integrity check)
        doc_io.seek(0)
        try:
            test_doc = Document(doc_io)
            print("DOCX file passed integrity check (can be opened by python-docx).")
        except Exception as e:
            print(f"DOCX integrity check failed: {e}")
            raise HTTPException(
                status_code=500, detail=f"Generated DOCX file is corrupted: {str(e)}"
            )

        doc_io.seek(0)
        print(
            "Document saved successfully. Preparing to return as a downloadable file."
        )

        # Return the document as a downloadable file
        return StreamingResponse(
            doc_io,
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
    Generate a CSV file from the FormConnect results content using LLM formatting.
    """
    print("Now generating CSV of FormConnect results...")
    try:
        # Get the content from the request
        if not request.content:
            raise HTTPException(status_code=400, detail="Results content is required")

        # Get the default LLM for formatting
        llm = get_default_llm(session, current_user)

        # Try to parse the content as JSON first (for structured data)
        try:
            content_data = json.loads(request.content)
            extracted_data = content_data.get("extracted_data", [])
            comparison_data = content_data.get("comparison", "")
            message_data = content_data.get("message", "")
        except json.JSONDecodeError:
            # If it's not JSON, treat it as raw content and use LLM to format
            extracted_data = []
            comparison_data = request.content
            message_data = ""

        # Create LLM prompt to format the data as CSV
        csv_prompt_template = """You are tasked with converting FormConnect comparison results into a well-structured CSV format.

Input Data:
{input_data}

Instructions:
1. Analyze the extracted data and comparison results
2. Create a CSV table with the following structure:
   - First column: "Filename" (document names)
   - Subsequent columns: Field names from the form template
3. Each row should represent one document with its extracted field values
4. If a field value is missing for a document, leave the cell empty
5. Clean up any formatting issues and ensure values are CSV-safe
6. Return ONLY the CSV content, no additional text or formatting

Expected format:
Filename,Field1,Field2,Field3,...
Document1.pdf,Value1,Value2,Value3,...
Document2.pdf,Value1,Value2,Value3,...

Return the CSV content:"""

        # Prepare the input data for the LLM
        input_data = {
            "extracted_data": extracted_data,
            "comparison": comparison_data,
            "message": message_data,
        }

        input_data_str = json.dumps(input_data, indent=2)

        variables = {"input_data": input_data_str}

        # Use LLM to generate the CSV content
        print("Calling LLM to format FormConnect results as CSV...")
        csv_content = invoke_llm(llm, csv_prompt_template, variables)

        # Clean up the response - remove any markdown formatting or extra text
        csv_content = csv_content.strip()
        if csv_content.startswith("```csv"):
            csv_content = csv_content[6:]
        if csv_content.startswith("```"):
            csv_content = csv_content[3:]
        if csv_content.endswith("```"):
            csv_content = csv_content[:-3]
        csv_content = csv_content.strip()

        # Ensure we have valid CSV content
        if not csv_content or "Filename" not in csv_content:
            # Fallback to basic formatting if LLM didn't produce good results
            output = StringIO()
            writer = csv.writer(output)

            # Create basic headers
            headers = ["Filename", "Field", "Value"]
            writer.writerow(headers)

            # Add extracted data if available
            if extracted_data:
                for i, doc_data in enumerate(extracted_data):
                    filename = f"Document_{i+1}"
                    if isinstance(doc_data, dict):
                        for field_name, field_value in doc_data.items():
                            cleaned_value = (
                                str(field_value)
                                .replace("\n", " ")
                                .replace("\r", "")
                                .replace('"', '""')
                            )
                            writer.writerow([filename, field_name, cleaned_value])

            # Add comparison data if available
            if comparison_data:
                writer.writerow(
                    [
                        "Comparison Results",
                        "Analysis",
                        comparison_data.replace("\n", " ")
                        .replace("\r", "")
                        .replace('"', '""'),
                    ]
                )

            csv_content = output.getvalue()
            output.close()

        # Convert to bytes
        csv_bytes = csv_content.encode("utf-8")

        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"formconnect_results_{timestamp}.csv"

        print(
            "CSV file generated successfully using LLM formatting. Preparing to return as a downloadable file."
        )

        return StreamingResponse(
            BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating CSV: {str(e)}")
