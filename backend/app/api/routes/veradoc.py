import uuid
from app.models import VeraDocRequest, VeraDocResponse, VeraDocChecklist, RagChecklistRequest, EmbeddingModel, Source, KnowledgeBase

from app.api.deps import CurrentUser, SessionDep
from app.core.config import settings
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
import re
import base64
from tempfile import NamedTemporaryFile
from pathlib import Path
import fitz  # PyMuPDF

from datetime import datetime

import tempfile
import shutil
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
            llm = get_default_llm(session)
            print("LLM successfully loaded.")
            
            # 5. Define the prompts for the different stages
            context_prompt_template = settings.VERADOC_CONTEXT_PROMPT_TEMPLATE
            qa_prompt_template = settings.VERADOC_QA_PROMPT_TEMPLATE
            final_prompt_template = settings.VERADOC_FINAL_PROMPT_TEMPLATE

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
                
                # Step 2: Get the relevant policy context for this question
                # Check if the model is a ReplicateWrapper or LangChain LLM
                is_replicate_model = hasattr(llm, '__class__') and 'ReplicateWrapper' in llm.__class__.__name__
                
                if is_replicate_model:
                    print("Using Replicate model for context chain")
                    try:
                        # Format the prompt directly for Replicate
                        formatted_context_prompt = context_prompt_template.format(
                            context=context,
                            question=question
                        )
                        question_context = llm.invoke(formatted_context_prompt)
                        print(f"Got context from Replicate model: {question_context[:100]}...")
                    except Exception as e:
                        print(f"Error getting context with Replicate model: {e}")
                        import traceback
                        traceback.print_exc()
                        question_context = "Error retrieving policy context."
                else:
                    # Standard LangChain approach
                    print("Using LangChain model for context chain")
                    context_prompt = ChatPromptTemplate.from_template(context_prompt_template)
                    context_chain = context_prompt | llm
                    context_response = context_chain.invoke({
                        "context": context, 
                        "question": question
                    })
                    question_context = context_response.content
                
                # Step 3: Answer the question based on the uploaded document and policy context
                if is_replicate_model:
                    print("Using Replicate model for QA chain")
                    try:
                        # Format the prompt directly for Replicate
                        formatted_qa_prompt = qa_prompt_template.format(
                            document_text=document_text[:10000],  # Limit length to avoid token issues
                            question=question,
                            question_context=question_context
                        )
                        answer = llm.invoke(formatted_qa_prompt)
                        print(f"Got answer from Replicate model: {answer[:100]}...")
                    except Exception as e:
                        print(f"Error getting answer with Replicate model: {e}")
                        import traceback
                        traceback.print_exc()
                        answer = "Error generating answer."
                else:
                    # Standard LangChain approach
                    print("Using LangChain model for QA chain")
                    qa_prompt = ChatPromptTemplate.from_template(qa_prompt_template)
                    qa_chain = qa_prompt | llm
                    qa_response = qa_chain.invoke({
                        "document_text": document_text[:10000],  # Limit length to avoid token issues
                        "question": question,
                        "question_context": question_context
                    })
                    answer = qa_response.content

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
            qa_pairs_text = ""
            for i, qa in enumerate(qa_pairs):
                qa_pairs_text += f"Question {i+1}: {qa['question']}\nAnswer: {qa['answer']}\n\n"
            
            # Final evaluation
            if is_replicate_model:
                print("Using Replicate model for final evaluation")
                try:
                    # Format the prompt directly for Replicate
                    formatted_final_prompt = final_prompt_template.format(
                        qa_pairs=qa_pairs_text
                    )
                    final_evaluation = llm.invoke(formatted_final_prompt)
                    print(f"Got final evaluation from Replicate model: {final_evaluation[:100]}...")
                except Exception as e:
                    print(f"Error getting final evaluation with Replicate model: {e}")
                    import traceback
                    traceback.print_exc()
                    final_evaluation = "Error generating final evaluation."
            else:
                # Standard LangChain approach
                print("Using LangChain model for final evaluation")
                final_prompt = ChatPromptTemplate.from_template(final_prompt_template)
                final_chain = final_prompt | llm
                final_response = final_chain.invoke({
                    "qa_pairs": qa_pairs_text
                })
                final_evaluation = final_response.content
            
            # 9. Compile the results
            result = {
                "final_evaluation": final_evaluation,
                "qa_pairs": qa_pairs
            }
            
            return VeraDocResponse(results=result)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
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