import uuid
from app.models import (
    FormConnectRequest,
    FormConnectResponse,
    FormConnectForm,
    FormConnectDetailResponse,
    GenerateFormFieldsRequest,
    GenerateFormFieldsResponse,
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

import json
import os

import base64
from tempfile import NamedTemporaryFile
from pathlib import Path
import fitz  # PyMuPDF

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
    file: UploadFile, template: Dict[str, str], llm=None
) -> Dict[str, str]:
    """
    Extract fields from a document using the LLM.
    """
    # Read the file content
    content = await file.read()

    try:
        text = content.decode("utf-8")  # Try to decode as UTF-8
    except UnicodeDecodeError:
        # If it's not a text file, we could handle binary files differently
        # For now, just return an error message in the template
        return {
            k: f"Could not extract: Binary file {file.filename}"
            for k in template.keys()
        }

    # Create the prompt
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
    return await extract_fields_from_digitized_document(file, template, llm)


async def compare_multiple_documents(
    documents: List[Dict[str, str]], file_names: List[str], llm
) -> str:
    """
    Compare fields across multiple documents using the LLM.
    """
    # Create a combined representation of all documents
    documents_str = ""
    for i, (doc, name) in enumerate(zip(documents, file_names)):
        # Convert dict to string, escaping any curly braces for the formatter
        doc_str = str(doc).replace("{", "{{").replace("}", "}}")
        documents_str += f"Document {i+1} ({name}): {doc_str}\n\n"

    print(
        "documents_str for comparison:", documents_str[:500]
    )  # Print first 500 chars for debugging

    # Create the prompt for multi-document comparison
    prompt_template = settings.FORMCONNECT_COMPARISON_PROMPT_TEMPLATE
    variables = {"documents_str": documents_str}
    response = invoke_llm(llm, prompt_template, variables)
    return response


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
                file, template, llm
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
            extracted_results, file_names, llm
        )
        result = {
            "message": "Documents compared successfully",
            "comparison": comparison_result,
            "extracted_data": extracted_results,
        }

    record_llm_interaction(
        session=session,
        user_id=current_user.id,
        functionality="formconnect",
        input_data={"fields": fields, "files": file_names, "search_mode": search_mode},
        output_data=result,
        metadata={"file_count": total_files},
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
                "analysis": analysis,
            },
            metadata={},
        )

        return GenerateFormFieldsResponse(fields=fields, description_analysis=analysis)

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
