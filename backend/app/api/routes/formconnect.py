import uuid
from app.models import FormConnectRequest, FormConnectResponse, FormConnectForm, ModelProvider, LlmModel
from app.services.llms import create_llm, get_default_llm
from app.api.deps import CurrentUser, SessionDep

from sqlmodel import Session, select
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Dict

from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage
from dotenv import load_dotenv
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
    prompt_text = f"""Here is a template of the fields that I want you to extract from this document: {template}
    Here is the full text of a document: {text}
    Fill out the template based on the fields you can find."""

    # Check if the model is a ReplicateWrapper or LangChain LLM
    if hasattr(llm, '__class__') and 'ReplicateWrapper' in llm.__class__.__name__:
        print("Using Replicate model for document extraction")
        try:
            # Direct invoke for Replicate models
            response_text = llm.invoke(prompt_text)
            
            # Try to parse JSON from the response
            try:
                import json
                # Try to find JSON in the response
                import re
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
                if json_match:
                    content_dict = json.loads(json_match.group(1))
                    return content_dict
                
                # If no JSON code block, try direct parsing
                content_dict = json.loads(response_text)
                return content_dict
            except (json.JSONDecodeError, AttributeError):
                # If parsing fails, return raw content
                return {"raw_content": str(response_text)}
                
        except Exception as e:
            print(f"Error extracting with Replicate model: {e}")
            import traceback
            traceback.print_exc()
            return {k: f"Error: {str(e)}" for k in template.keys()}
    else:
        # Handle LangChain-compatible LLM
        print("Using LangChain model for document extraction")
        prompt_template = ChatPromptTemplate.from_template(
            """Here is a template of the fields that I want you to extract from this document: {template}
            Here is the full text of a document: {document_text}
            Fill out the template based on the fields you can find."""
        )
        
        try:
            prompt = prompt_template.format_prompt(template=template, document_text=text)
            response = llm(prompt.to_messages())
            
            # Try to parse the response as JSON
            try:
                import json
                # The output might already be a dictionary
                if isinstance(response.content, dict):
                    return response.content
                # Otherwise, try to parse it as JSON
                content_dict = json.loads(response.content)
                return content_dict
            except (json.JSONDecodeError, AttributeError):
                # If JSON parsing fails or response.content is not string-like
                # Return the content wrapped in a dictionary
                return {"raw_content": str(response.content)}
        except Exception as e:
            print(f"Error extracting with LangChain model: {e}")
            import traceback
            traceback.print_exc()
            return {k: f"Error: {str(e)}" for k in template.keys()}
        

async def extract_fields_from_handwritten_document(file: UploadFile, template: Dict[str, str], llm) -> Dict[str, str]:
    """
    Extract fields from a handwritten document.
    """
    # Read the file content
    content = await file.read()
    
    # Define image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tif', '.tiff', '.webp']
    file_ext = Path(file.filename).suffix.lower()
    
    # Check if the file is an image
    if file_ext in image_extensions:
        try:
            # For image files, we can directly encode to base64
            img_base64 = base64.b64encode(content).decode('utf-8')
            
            # If using Replicate, we need to handle it differently
            if hasattr(llm, '__class__') and 'ReplicateWrapper' in llm.__class__.__name__:
                print("WARNING: Replicate models may not support image processing in the same way")
                print("Using Replicate model for image extraction - text-only fallback")
                
                # Fall back to text-only prompt without the image
                prompt_text = f"""Here is a template of the fields that I want you to extract: {template}
                
                NOTE: This was supposed to be an image file with handwritten content, but I'm using a text-only model.
                If you cannot process images, please respond with 'Cannot process image content'."""
                
                try:
                    response_text = llm.invoke(prompt_text)
                    return {"raw_content": str(response_text)}
                except Exception as e:
                    print(f"Error with Replicate image extraction: {e}")
                    return {k: "Cannot process image with this model" for k in template.keys()}
            else:
                # For LangChain models that support images
                print("Using LangChain model for image extraction")
                # Create a prompt for the image
                prompt_template = ChatPromptTemplate.from_template(
                    """Here is a template of the fields that I want you to extract from this image: {template}
                    
                    I'm sending you an image with handwritten content.
                    
                    For each field in the template, try to locate and extract the corresponding value from the image.
                    Pay special attention to handwritten text and ensure accuracy in your extraction.
                    
                    Return your results as a JSON object matching the template structure.
                    """
                )
                
                # Format the prompt with the template
                prompt = prompt_template.format_prompt(template=template)
                
                # Create a list of messages with text and image
                messages = prompt.to_messages()
                
                # Add the image to the message content
                if isinstance(messages[0].content, str):
                    # Convert to multimodal format
                    content_parts = [
                        {"type": "text", "text": messages[0].content},
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/{file_ext[1:]};base64,{img_base64}"
                            }
                        }
                    ]
                    
                    messages[0].content = content_parts
                
                # Call the LLM with image capability
                response = llm(messages)
                
                # Parse response as JSON
                try:
                    import json
                    if isinstance(response.content, dict):
                        return response.content
                    content_dict = json.loads(response.content)
                    return content_dict
                except (json.JSONDecodeError, AttributeError):
                    return {"raw_content": str(response.content)}
        except Exception as e:
            # If image processing fails, return an error
            return {k: f"Error processing image: {str(e)}" for k in template.keys()}
    
    # For non-image files or if using Replicate, fall back to text-based extraction
    await file.seek(0)  # Reset file position
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
    prompt_text = f"""I am going to show you information extracted from multiple documents:
    
    {documents_str}
    
    Please analyze all the documents and identify any fields that have different values across documents.
    
    Create a markdown table with the following format:
    1. First column should be titled "FIELD" and contain the field name
    2. Each additional column should have the document name as header (e.g., "Document 1", "Document 2")
    3. Include ONLY fields where there are discrepancies between documents
    
    After the table, please:
    1. For each discrepancy, suggest which value is most likely correct and why
    2. Provide a summary of how consistent the documents are overall
    
    Example format:
    ```markdown
    | FIELD | Document 1 | Document 2 | ... |
    |-------|------------|------------|-----|
    | Name  | John Smith | J. Smith   | ... |
    | Date  | 2023-01-01 | 2023-01-15 | ... |
    ```
    
    ONLY return the Markdown table -- do NOT return any other text. 
    Also, do NOT add tick marks like ``` and the label 'markdown': just give the actual markdown table content as raw text.
    However, if there are no discrepancies, please state that all fields match across documents.
    """

    # Check if the model is a ReplicateWrapper or LangChain LLM
    if hasattr(llm, '__class__') and 'ReplicateWrapper' in llm.__class__.__name__:
        print("Using Replicate model for document comparison")
        try:
            # Direct invoke for Replicate models
            response_text = llm.invoke(prompt_text)
            print("Comparison response from Replicate:", response_text[:100])
            return response_text
        except Exception as e:
            print(f"Error comparing with Replicate model: {e}")
            import traceback
            traceback.print_exc()
            return f"Error comparing documents: {str(e)}"
    else:
        # Handle LangChain-compatible LLM
        print("Using LangChain model for document comparison")
        try:
            prompt_template = ChatPromptTemplate.from_template(prompt_text)
            prompt = prompt_template.format_prompt(documents_str=documents_str)
            response = llm(prompt.to_messages())
            print("Comparison response from LangChain:", response.content[:100])
            return response.content
        except Exception as e:
            print(f"Error comparing with LangChain model: {e}")
            import traceback
            traceback.print_exc()
            return f"Error comparing documents: {str(e)}"


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