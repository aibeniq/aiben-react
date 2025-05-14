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
    text = content.decode("utf-8")  # Assuming the file is text-based (e.g., .txt, .docx, .pdf)

    # Create the prompt
    prompt_template = ChatPromptTemplate.from_template(
        """Here is a template of the fields that I want you to extract from this document: {template}
        Here is the full text of a document: {document_text}
        Fill out the template based on the fields you can find."""
    )
    prompt = prompt_template.format_prompt(template=template, document_text=text)

    # Call the LLM
    response = llm(prompt.to_messages())
    return response.content  # Assuming the LLM returns a JSON string

async def compare_documents(template1: Dict[str, str], template2: Dict[str, str]) -> str:
    """
    Compare the extracted fields from two documents using the LLM.
    """
    # Create the prompt
    prompt_template = ChatPromptTemplate.from_template(
        """I am going to show you two sets of information from two documents that were compared:
        Document 1: {template1}
        Document 2: {template2}
        Are there mismatches in any of the fields? If so, give them in a bulleted list along with a description of why they mismatch."""
    )
    prompt = prompt_template.format_prompt(template1=template1, template2=template2)

    # Call the LLM
    response = llm(prompt.to_messages())
    return response.content  # Assuming the LLM returns a plain text response

@router.post("/process", response_model=FormConnectResponse)
async def process_form(
    form_connect_in: FormConnectRequest = Depends(),
    files: List[UploadFile] = File(...),
):
    """
    Process the uploaded files and fields.
    """
    print("Now processing files...")
    # Parse the fields into a list
    field_list = form_connect_in.fields.splitlines()

    if not field_list:
        raise HTTPException(status_code=400, detail="No fields provided.")

    # Generate the JSON template
    template = generate_template(field_list)

    # Extract fields from both documents
    extracted1 = await extract_fields_from_document(files[0], template)
    extracted2 = await extract_fields_from_document(files[1], template)

    # Compare the extracted fields
    comparison_results = await compare_documents(extracted1, extracted2)

    # Return the comparison results
    return FormConnectResponse(results=comparison_results)