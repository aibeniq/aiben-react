from app.models import FormConnectRequest, FormConnectResponse
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Dict

from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage
from dotenv import load_dotenv
import os

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
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

def generate_template(fields: List[str]) -> Dict[str, str]:
    """
    Generate a JSON template from a list of fields.
    Each field will have a blank value.
    """
    return {field: "" for field in fields}

async def extract_fields_from_document(file: UploadFile, template: Dict[str, str]) -> Dict[str, str]:
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
    files: List[UploadFile] = File(...),
):
    """
    Process the uploaded files and fields.
    """
    print(f"Now processing {len(files)} files...")
    
    # Check if we have at least one file
    if len(files) < 1:
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
    
    for file in files:
        extracted = await extract_fields_from_document(file, template)
        extracted_results.append(extracted)
        file_names.append(file.filename)
        
        # Reset file position for potential future reads
        await file.seek(0)

    # If there's only one file, we can't do comparison
    if len(files) == 1:
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