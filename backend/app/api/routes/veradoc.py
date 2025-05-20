import uuid
from app.models import VeraDocRequest, VeraDocResponse, VeraDocChecklist, RagChecklistRequest, EmbeddingModel

from app.api.deps import CurrentUser, SessionDep

from app.services.knowledgebases import get_embedding_model
from app.services.embeddings import load_embeddings_model
from app.services.llms import get_default_llm

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

import tempfile
import shutil
import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from app.models import KnowledgeBase
import zipfile
from io import BytesIO

# Load environment variables from .env file
load_dotenv(dotenv_path="c:/miniconda/aibeniq-react/.env", override=True)

# Retrieve the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")
print(openai_api_key)
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")

# Set up OpenAI API key
os.environ["OPENAI_API_KEY"] = openai_api_key
router = APIRouter(prefix="/veradoc", tags=["veradoc"])

# Initialize the LLM
#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

def generate_template(fields: List[str]) -> Dict[str, str]:
    """
    Generate a JSON template from a list of fields.
    Each field will have a blank value.
    """
    return {field: "" for field in fields}

# Add the new endpoint
@router.post("/process-rag", response_model=VeraDocResponse)
async def process_rag_checklist(
    session: SessionDep,
    current_user: CurrentUser,
    request: RagChecklistRequest = Depends(),
    files: List[UploadFile] = File(...),
    handwritten_files: List[UploadFile] = File(None),
):
    """
    Process the uploaded files using RAG with a knowledge base.
    """
    try:
        # 1. Retrieve knowledge base from database
        kb = session.get(KnowledgeBase, request.knowledge_base_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        if kb.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="You don't have access to this knowledge base")
        
        # 2. Create a temporary directory for ChromaDB
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zipped ChromaDB into the temp directory
            if kb.data:
                with zipfile.ZipFile(BytesIO(kb.data), 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
            else:
                raise HTTPException(status_code=400, detail="Knowledge base has no vector database data")
            
            # 3. Load the vector database with the SAME model used to create the knowledge base
            # Use the knowledge base's specific embedding model if available
            if kb.embedding_model_id:
                embedding_model = session.get(EmbeddingModel, kb.embedding_model_id)
                if embedding_model:
                    # Use the KB's original model
                    model_id = embedding_model.model_id
                    provider = embedding_model.provider
                    print(f"Using knowledge base's original embedding model: {model_id}")
                else:
                    # Fallback if the model was deleted from the database
                    embedding_info = get_embedding_model(session)
                    model_id = embedding_info["model_id"]
                    provider = embedding_info["provider"]
                    print(f"Original embedding model not found, using current default: {model_id}")
            else:
                # For knowledge bases created before tracking embedding models
                embedding_info = get_embedding_model(session)
                model_id = embedding_info["model_id"]
                provider = embedding_info["provider"]
                print(f"Knowledge base has no embedding model record, using current default: {embedding_info}")
            
            print(f"Initializing embedding model: {model_id} ({provider})")
            embeddings = load_embeddings_model(
                provider=provider,
                model_id=model_id
            )
            chroma_db = Chroma(persist_directory=temp_dir, embedding_function=embeddings)
            retriever = chroma_db.as_retriever(search_kwargs={"k": 5})
            
            # 4. Initialize the LLM
            #llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
            print("Now loading default LLM...")
            llm = get_default_llm(session)
            
            # 5. Define the prompts for the different stages
            context_prompt_template = """
            CONTEXT:
            {context}
            
            INSTRUCTION: 
            What necessary information from the context above should be kept in mind when answering the following question? {question} 
            ONLY INCLUDE POLICY INFORMATION THAT WOULD BE SPECIFICALLY PERTINENT TO THE QUESTION -- do NOT just repeat general requirements.
            
            ANSWER:
            According to the policy context, the following should be kept in mind when answering the question:
            """
            
            context_prompt = ChatPromptTemplate.from_template(context_prompt_template)
            
            qa_prompt_template = """
            Read the following document and answer the following question clearly and concisely in 100 words or less.
            
            SAMPLE DOCUMENT: {document_text}
            
            QUESTION: {question}
            
            Keep the following RELEVANT REQUIREMENTS in mind when answering the question:
            {question_context}
            
            ANSWER:
            """
            
            qa_prompt = ChatPromptTemplate.from_template(qa_prompt_template)
            
            final_prompt_template = """
            According to policy, an acceptable document must have all of the elements described in the following questions.
            Read the following question-and-answer pairs about a certain proposal and determine whether or not it conforms to the policy.
            
            Remember: if any single element is missing from the proposal, it automatically means that the entire proposal does NOT conform to policy.
            If the plan does not conform to policy, explain why not.
            
            {qa_pairs}
            
            Based on the question-and-answer pairs above, does the plan follow policy?
            """
            
            final_prompt = ChatPromptTemplate.from_template(final_prompt_template)
            
            # 6. Process each uploaded file
            qa_pairs = []
            question_list = request.questions.strip().split('\n')
            
            # Get file content
            file = files[0]  # Process the first file for now
            content = await file.read()
            try:
                document_text = content.decode('utf-8')
            except UnicodeDecodeError:
                # If it's not UTF-8 encoded, it's likely a binary file
                # For PDFs, you could use PyPDF2 or other libraries to extract text
                document_text = f"Failed to extract text from {file.filename}"
            
            # Reset file position
            await file.seek(0)
            
            # 7. Process each question using the RAG approach
            for question in question_list:
                question = question.strip()
                if not question:
                    continue
                
                # Step 1: Retrieve relevant context from the knowledge base
                docs = retriever.get_relevant_documents(question)
                context = "\n\n".join([doc.page_content for doc in docs])
                
                # Step 2: Get the relevant policy context for this question
                context_chain = context_prompt | llm
                context_response = context_chain.invoke({"context": context, "question": question})
                question_context = context_response.content
                
                # Step 3: Answer the question based on the uploaded document and policy context
                qa_chain = qa_prompt | llm
                qa_response = qa_chain.invoke({
                    "document_text": document_text,
                    "question": question,
                    "question_context": question_context
                })
                
                # Store the question-answer pair with context
                qa_pairs.append({
                    "question": question,
                    "answer": qa_response.content,
                    "context": question_context
                })
            
            # 8. Generate the final evaluation
            qa_pairs_text = ""
            for i, qa in enumerate(qa_pairs):
                qa_pairs_text += f"Question {i+1}: {qa['question']}\nAnswer: {qa['answer']}\n\n"
            
            final_chain = final_prompt | llm
            final_response = final_chain.invoke({"qa_pairs": qa_pairs_text})
            
            # 9. Compile the results
            result = {
                "final_evaluation": final_response.content,
                "qa_pairs": qa_pairs
            }
            
            return VeraDocResponse(results=result)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing RAG checklist: {str(e)}")

# Functions related to Checklists
@router.post("/checklists", response_model=VeraDocChecklist)
def create_checklist(checklist: VeraDocChecklist, session: SessionDep, current_user: CurrentUser,):
    """
    Save a new checklist to the database.
    """
    existing_checklist = session.exec(select(VeraDocChecklist).where(VeraDocChecklist.name == checklist.name)).first()
    if existing_checklist:
        raise HTTPException(status_code=400, detail="A checklist with this name already exists.")
    
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
def update_checklist(checklist_id: uuid.UUID, updated_checklist: VeraDocChecklist, session: SessionDep, current_user: CurrentUser):
    """
    Update an existing checklist.
    """
    checklist = session.get(VeraDocChecklist, checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found.")
    
    # Ensure the current user is the owner of the checklist
    if checklist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this checklist.")
    
    checklist.name = updated_checklist.name
    checklist.description = updated_checklist.description
    checklist.fields = updated_checklist.fields
    checklist.date_modified = datetime.utcnow()
    
    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist

@router.delete("/checklists/{checklist_id}")
def delete_checklist(checklist_id: uuid.UUID, session: SessionDep, current_user: CurrentUser):
    """
    Delete a checklist by ID.
    """
    checklist = session.get(VeraDocChecklist, checklist_id)
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found.")
    
    # Ensure the current user is the owner of the checklist
    if checklist.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this checklist.")
    
    session.delete(checklist)
    session.commit()
    return {"message": "Checklist deleted successfully."}