import uuid
from app.models import FormConnectRequest, FormConnectResponse, FormConnectForm, ModelProvider, LlmModel
from app.services.llms import create_llm, get_default_llm, invoke_llm, invoke_llm_with_image, record_llm_interaction
from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings

from sqlmodel import Session, select
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Dict

from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage
from dotenv import load_dotenv

import json
import os

import base64
from tempfile import NamedTemporaryFile
from pathlib import Path
import fitz  # PyMuPDF

from datetime import datetime

# Load environment variables from .env file
load_dotenv(dotenv_path="c:/miniconda/aibeniq-react/.env", override=True)

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
    print("WARNING: OPENAI_API_KEY is not set in environment variables. Some FormConnect features will be limited.")

router = APIRouter(prefix="/formconnect", tags=["formconnect"])

def generate_template(fields: List[str]) -> Dict[str, str]:
    """
    Generate a JSON template from a list of fields.
    Each field will have a blank value.
    """
    return {field: "" for field in fields}

async def extract_fields_from_digitized_document(file: UploadFile, template: Dict[str, str], llm=None) -> Dict[str, str]:
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
        return {k: f"Could not extract: Binary file {file.filename}" for k in template.keys()}

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
    

async def extract_fields_from_handwritten_document(file: UploadFile, template: Dict[str, str], llm) -> Dict[str, str]:
    """
    Extract fields from a handwritten document.
    """
    print("Now extracting fields from handwritten document:", file.filename)
    content = await file.read()
    
    # Define image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.webp']
    file_ext = Path(file.filename).suffix.lower()
    
    # Check if the file is an image
    if file_ext in image_extensions:
        try:
            img_base64 = base64.b64encode(content).decode('utf-8')
            
            # Use the template from config
            prompt_template = settings.FORMCONNECT_HANDWRITTEN_PROMPT_TEMPLATE
            variables = {"template": template}

            print("Now invoking LLM with base-encoded image...")
            response = invoke_llm_with_image(
                llm,
                prompt_template,
                variables=variables,
                image_base64=img_base64,
                image_type=file_ext[1:] if file_ext.startswith('.') else file_ext
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


async def compare_multiple_documents(documents: List[Dict[str, str]], file_names: List[str], llm) -> str:
    """
    Compare fields across multiple documents using the LLM.
    """
    # Create a combined representation of all documents
    documents_str = ""
    for i, (doc, name) in enumerate(zip(documents, file_names)):
        # Convert dict to string, escaping any curly braces for the formatter
        doc_str = str(doc).replace("{", "{{").replace("}", "}}")
        documents_str += f"Document {i+1} ({name}): {doc_str}\n\n"

    print("documents_str for comparison:", documents_str[:500])  # Print first 500 chars for debugging
    
    # Create the prompt for multi-document comparison
    prompt_template = settings.FORMCONNECT_COMPARISON_PROMPT_TEMPLATE
    variables = {"documents_str": documents_str}
    response = invoke_llm(llm, prompt_template, variables)
    return response


@router.post("/process", response_model=FormConnectResponse)
async def process_form(
    session: SessionDep,
    current_user: CurrentUser,
    form_connect_in: FormConnectRequest = Depends(),
    digitized_files: List[UploadFile] = File(None),
    handwritten_files: List[UploadFile] = File(None),
):
    """
    Process the uploaded files and fields.
    
    Handles two types of files:
    - digitized_files: Standard text extraction
    - handwritten_files: OCR-based extraction (placeholder)
    """
    # Get the default LLM
    llm = get_default_llm(session, current_user)

    # Log the model type being used
    if hasattr(llm, '__class__') and 'ReplicateWrapper' in llm.__class__.__name__:
        print(f"Using Replicate model for FormConnect: {getattr(llm, 'model_id', 'unknown')}")
    else:
        print(f"Using LangChain model for FormConnect: {type(llm).__name__}")
    
    total_files = (len(digitized_files) if digitized_files else 0) + (len(handwritten_files) if handwritten_files else 0)
    print(f"Now processing {total_files} files ({len(digitized_files) if digitized_files else 0} digitized, {len(handwritten_files) if handwritten_files else 0} handwritten)...")
    
    # Check if we have at least one file
    if total_files < 1:
        raise HTTPException(status_code=400, detail="At least one file must be uploaded.")
    
    # Parse the fields into a list
    field_list = form_connect_in.fields.splitlines()

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
            extracted = await extract_fields_from_digitized_document(file, template, llm)

            print("Results for file name:", file.filename)
            print("Extracted fields:", extracted)
            extracted_results.append(extracted)
            file_names.append(f"{file.filename} (digitized)")
            
            # Reset file position for potential future reads
            await file.seek(0)
    
    # Process handwritten files using a specialized function (placeholder)
    if handwritten_files:
        for file in handwritten_files:
            extracted = await extract_fields_from_handwritten_document(file, template, llm)
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
            "extracted_data": extracted_results[0]
        }
    else:
        # Compare the extracted fields
        comparison_result = await compare_multiple_documents(extracted_results, file_names, llm)
        result = {
            "message": "Documents compared successfully",
            "comparison": comparison_result,
            "extracted_data": extracted_results
        }

    record_llm_interaction(
        session=session,
        user_id=current_user.id,
        functionality="formconnect",
        input_data={
            "fields": form_connect_in.fields,
            "files": file_names
        },
        output_data=result,
        metadata={
            "file_count": total_files
        }
    )

    # Return the comparison results as a dictionary
    return FormConnectResponse(results=result)

# Functions related to Forms
@router.post("/forms", response_model=FormConnectForm)
def create_form(form: FormConnectForm, session: SessionDep, current_user: CurrentUser,):
    """
    Save a new form to the database.
    """
    existing_form = session.exec(select(FormConnectForm).where(FormConnectForm.name == form.name)).first()
    if existing_form:
        raise HTTPException(status_code=400, detail="A form with this name already exists.")
    
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
def update_form(form_id: uuid.UUID, updated_form: FormConnectForm, session: SessionDep, current_user: CurrentUser):
    """
    Update an existing form.
    """
    form = session.get(FormConnectForm, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    
    # Ensure the current user is the owner of the form
    if form.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this form.")
    
    form.name = updated_form.name
    form.description = updated_form.description
    form.fields = updated_form.fields
    form.date_modified = datetime.utcnow()
    
    session.add(form)
    session.commit()
    session.refresh(form)
    return form

@router.delete("/forms/{form_id}")
def delete_form(form_id: uuid.UUID, session: SessionDep, current_user: CurrentUser):
    """
    Delete a form by ID.
    """
    form = session.get(FormConnectForm, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    
    # Ensure the current user is the owner of the form
    if form.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this form.")
    
    session.delete(form)
    session.commit()
    return {"message": "Form deleted successfully."}