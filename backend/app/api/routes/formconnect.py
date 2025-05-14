from app.models import FormConnectRequest, FormConnectResponse
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

# Load environment variables from .env file
load_dotenv(dotenv_path="c:/miniconda/aibeniq-react/.env", override=True)

# Retrieve the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
print(openai_api_key)
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = openai_api_key
router = APIRouter(prefix="/formconnect", tags=["formconnect"])

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

def generate_template(fields: List[str]) -> Dict[str, str]:
    """
    Generate a JSON template from a list of fields.
    Each field will have a blank value.
    """
    return {field: "" for field in fields}

async def extract_fields_from_digitized_document(file: UploadFile, template: Dict[str, str]) -> Dict[str, str]:
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
    prompt_template = ChatPromptTemplate.from_template(
        """Here is a template of the fields that I want you to extract from this document: {template}
        Here is the full text of a document: {document_text}
        Fill out the template based on the fields you can find."""
    )
    prompt = prompt_template.format_prompt(template=template, document_text=text)

    # Call the LLM
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

async def extract_fields_from_handwritten_document(file: UploadFile, template: Dict[str, str]) -> Dict[str, str]:
    """
    Extract fields from a handwritten document by either:
    1. For PDFs: extracting images from the PDF and sending to the LLM
    2. For image files: sending the image directly to the LLM
    
    Args:
        file: Uploaded file containing handwritten content (PDF or image format)
        template: Dictionary template of fields to extract
        
    Returns:
        Dictionary of extracted fields
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
            multimodal_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
            response = multimodal_llm(messages)
            
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
    
    # Check if the file is a PDF
    elif file.filename.lower().endswith('.pdf'):
        try:
            # Save the PDF to a temporary file
            with NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # [Rest of your existing PDF processing code]
            # Extract images from the PDF
            pdf_document = fitz.open(temp_file_path)
            image_list = []
            
            # Process each page of the PDF
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                
                # Get images from the page
                image_list.append(f"--- Page {page_num + 1} ---")
                
                # Render the page to an image
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img_bytes = pix.tobytes("png")
                
                # Encode the image to base64 for sending to the LLM
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                image_list.append(img_base64)
            
            # Clean up the temporary file
            Path(temp_file_path).unlink(missing_ok=True)
            
            # Create a prompt with the images for the LLM
            prompt_template = ChatPromptTemplate.from_template(
                """Here is a template of the fields that I want you to extract from these document images: {template}
                
                I'm sending you images from a document with handwritten content.
                
                For each field in the template, try to locate and extract the corresponding value from the images.
                Pay special attention to handwritten text and ensure accuracy in your extraction.
                
                Return your results as a JSON object matching the template structure.
                """
            )
            
            # Format the prompt with the template
            prompt = prompt_template.format_prompt(template=template)
            
            # Create a list of messages with text and images
            messages = prompt.to_messages()
            
            # Add the images to the message content (in a format that works with multimodal models)
            if isinstance(messages[0].content, str):
                # Convert to multimodal format
                content_parts = [{"type": "text", "text": messages[0].content}]
                
                # Add each image as content parts
                for i, img in enumerate(image_list):
                    if img.startswith('---'):  # This is a page marker
                        content_parts.append({"type": "text", "text": img})
                    else:
                        content_parts.append({
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/png;base64,{img}"
                            }
                        })
                
                messages[0].content = content_parts
            
            # Call the LLM (use a multimodal model that supports images)
            multimodal_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
            response = multimodal_llm(messages)
            
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
                return {"raw_content": str(response.content)}
            
        except Exception as e:
            # If PDF processing fails, return an error
            return {k: f"Error processing PDF: {str(e)}" for k in template.keys()}
    
    else:
        # For non-PDF, non-image files, fall back to the regular extraction
        # but add a note that this was supposed to be processed as handwritten
        await file.seek(0)  # Reset file position
        result = await extract_fields_from_digitized_document(file, template)
        
        # Add a note that this was meant to be processed as handwritten
        for key in result:
            if result[key]:
                result[key] = f"[HANDWRITTEN (processed as text)] {result[key]}"
        
        return result

async def compare_multiple_documents(documents: List[Dict[str, str]], file_names: List[str]) -> str:
    """
    Compare fields across multiple documents using the LLM.
    
    Args:
        documents: List of dictionaries containing extracted fields
        file_names: List of file names corresponding to the documents
        
    Returns:
        String with comparison results
    """
    # Create a combined representation of all documents
    documents_str = ""
    for i, (doc, name) in enumerate(zip(documents, file_names)):
        documents_str += f"Document {i+1} ({name}): {doc}\n\n"
    
    # Create the prompt for multi-document comparison
    prompt_template = ChatPromptTemplate.from_template(
        """I am going to show you information extracted from multiple documents:
        
        {documents}
        
        Please analyze all the documents and:
        1. Identify any fields that have different values across documents
        2. For each discrepancy, list the field name and the different values found
        3. If possible, suggest which value is most likely correct
        4. Provide a summary of how consistent the documents are overall
        
        Format your response as a clear, readable report."""
    )
    
    prompt = prompt_template.format_prompt(documents=documents_str)

    # Call the LLM
    response = llm(prompt.to_messages())
    return response.content


@router.post("/process", response_model=FormConnectResponse)
async def process_form(
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
            extracted = await extract_fields_from_digitized_document(file, template)

            print("Results for file name:", file.filename)
            print("Extracted fields:", extracted)
            extracted_results.append(extracted)
            file_names.append(f"{file.filename} (digitized)")
            
            # Reset file position for potential future reads
            await file.seek(0)
    
    # Process handwritten files using a specialized function (placeholder)
    if handwritten_files:
        for file in handwritten_files:
            extracted = await extract_fields_from_handwritten_document(file, template)
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
        comparison_result = await compare_multiple_documents(extracted_results, file_names)
        result = {
            "message": "Documents compared successfully",
            "comparison": comparison_result,
            "extracted_data": extracted_results
        }

    # Return the comparison results as a dictionary
    return FormConnectResponse(results=result)