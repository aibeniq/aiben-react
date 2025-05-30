import uuid
from app.models import VeraDocRequest, VeraDocResponse, VeraDocChecklist, RagChecklistRequest, EmbeddingModel, Source, KnowledgeBase

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
from app.services.knowledgebases import get_embedding_model
from app.services.embeddings import load_embeddings_model
from app.services.llms import get_default_llm, invoke_llm

from sqlmodel import Session, select
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request as FastAPIRequest
from typing import List, Dict
import asyncio
from dotenv import load_dotenv
import os
import re
import base64
from tempfile import NamedTemporaryFile
from pathlib import Path
import fitz  # PyMuPDF

from datetime import datetime
from starlette.requests import Request
import tempfile
import shutil
import traceback
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import zipfile
from io import BytesIO

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

router = APIRouter(prefix="/veradoc", tags=["veradoc"])

# Initialize the LLM
#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

def generate_template(questions: List[str]) -> Dict[str, str]:
    """
    Generate a JSON template from a list of questions.
    Each field will have a blank value.
    """
    return {field: "" for field in questions}

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

            # Print all metadata in the vectorstore
            print("======= CHROMA VECTORDB METADATA CONTENTS =======")
            # Get all documents with their metadata
            all_docs = chroma_db.get()
            if all_docs and 'metadatas' in all_docs:
                for i, metadata in enumerate(all_docs['metadatas']):
                    print(f"Document {i+1} Metadata: {metadata}")
                    # If you want to see document content as well
                    if 'documents' in all_docs and i < len(all_docs['documents']):
                        doc_preview = all_docs['documents'][i][:200] + "..." if len(all_docs['documents'][i]) > 100 else all_docs['documents'][i]
                        print(f"Content preview: {doc_preview}")
                    print("-" * 50)
            else:
                print("No documents or metadata found in the vectorstore")
            print("================================================")


            retriever = chroma_db.as_retriever(search_kwargs={"k": 5})
            
            # 4. Initialize the LLM
            #llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
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
            question_list = request_data.questions.strip().split('\n')
            
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
                if cancellation_requested:
                    print("Operation cancelled by client disconnect, stopping processing")
                    return VeraDocResponse(results={"status": "cancelled", "message": "Operation cancelled by user"})
                
                question = question.strip()
                if not question:
                    continue
                
                # Step 1: Retrieve relevant context from the knowledge base
                docs = retriever.get_relevant_documents(question)
                context = "\n\n".join([doc.page_content for doc in docs])

                # Store source documents for citation
                source_citations = []
                for doc in docs:
                    # Ensure source_data_id is included in metadata if available
                    metadata = doc.metadata.copy()  # Copy to avoid modifying the original
                    
                    # If the metadata contains a source path that matches a pattern from a KB
                    if 'source' in metadata and isinstance(metadata['source'], str):
                        # Try to find the corresponding source_data_id
                        source_path = metadata['source']
                        # Extract just the filename
                        raw_filename = Path(source_path).name
                        
                        # Extract the real filename after the underscore using regex
                        # This looks for any characters followed by an underscore, then captures everything after
                        match = re.search(r'^[^_]*_(.+)$', raw_filename)
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
                            select(Source)
                            .where(Source.name == filename)
                        ).first()
                        
                        if source_entry:
                            metadata['source_data_id'] = str(source_entry.source_data_id)
                    
                    source = {
                        "content": doc.page_content,
                        "metadata": metadata
                    }
                    source_citations.append(source)

                if cancellation_requested:
                    print("Operation cancelled by client disconnect, stopping processing")
                    return VeraDocResponse(results={"status": "cancelled", "message": "Operation cancelled by user"})
                
                # Step 2: Get the relevant policy context for this question
                print("Generating context for question...")
                question_context = invoke_llm(
                    llm,
                    context_prompt_template,
                    {"context": context, "question": question}
                )
                print(f"Got context: {question_context[:100]}...")

                if cancellation_requested:
                    print("Operation cancelled by client disconnect, stopping processing")
                    return VeraDocResponse(results={"status": "cancelled", "message": "Operation cancelled by user"})
                
                # Step 3: Answer the question based on the uploaded document and policy context
                print("Generating answer based on document and context...")
                answer = invoke_llm(
                    llm,
                    qa_prompt_template,
                    {
                        "document_text": document_text[:10000],  # Limit length to avoid token issues
                        "question": question,
                        "question_context": question_context
                    }
                )
                print(f"Got answer: {answer[:100]}...")

                print("Source citations for question:", question)
                for source in source_citations:
                    print(f"Source: {source['metadata'].get('source', 'Unknown')}, Content: {source['content']}")
                
                # Store the question-answer pair with context
                qa_pairs.append({
                    "question": question,
                    "answer": answer,
                    "context": question_context,
                    "source_citations": source_citations
                })
            
            # 8. Generate the final evaluation
            if cancellation_requested:
                print("Operation cancelled by client disconnect, stopping processing")
                return VeraDocResponse(results={"status": "cancelled", "message": "Operation cancelled by user"})
            
            qa_pairs_text = ""
            for i, qa in enumerate(qa_pairs):
                qa_pairs_text += f"Question {i+1}: {qa['question']}\nAnswer: {qa['answer']}\n\n"
            
            # Final evaluation
            print("Generating final evaluation...")
            final_evaluation = invoke_llm(
                llm,
                final_prompt_template,
                {"qa_pairs": qa_pairs_text}
            )
            print(f"Got final evaluation: {final_evaluation[:100]}...")
            
            # 9. Compile the results
            result = {
                "final_evaluation": final_evaluation,
                "qa_pairs": qa_pairs
            }
            
            return VeraDocResponse(results=result)
            
    except Exception as e:
        print("Error processing RAG checklist:")
        print(str(e))
        
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing RAG checklist: {str(e)}")
    finally:
        # Clean up the disconnect monitor if it exists
        if disconnect_monitor:
            disconnect_monitor.cancel()

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
    checklist.questions = updated_checklist.questions
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