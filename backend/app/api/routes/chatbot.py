from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional
from app.services.embeddings import load_embeddings_model
from app.services.llms import create_llm
from app.api.deps import CurrentUser, SessionDep
from app.models import KnowledgeBase, EmbeddingModel, LlmModel
from sqlmodel import Session, select
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
import tempfile
import os

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/knowledge-base/{kb_id}")
async def query_knowledge_base(
    session: SessionDep,
    kb_id: str,
    question: str,
    use_default_models: bool = False,
):
    # Get the knowledge base
    kb = session.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Get models - either default ones or the ones associated with the KB
    if use_default_models:
        embedding_model = session.exec(
            select(EmbeddingModel).where(EmbeddingModel.is_default == True)
        ).first()
        
        llm_model = session.exec(
            select(LlmModel).where(LlmModel.is_default == True)
        ).first()
    else:
        embedding_model = session.get(EmbeddingModel, kb.embedding_model_id)
        llm_model = session.get(LlmModel, kb.llm_model_id)
    
    # Load the vector store
    vector_store = FAISS.load_local(kb.vectorstore_path, 
                                   load_embeddings_model(embedding_model.provider, 
                                                        embedding_model.model_id))
    
    # Create the LLM
    llm = create_llm(llm_model.provider, llm_model.model_id, 
                    temperature=0.0)
    
    # Create the QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever()
    )
    
    # Run the query
    result = qa_chain({"query": question})
    
    return {"answer": result["result"]}

@router.post("/document")
async def query_document(
    session: SessionDep,
    file: UploadFile = File(...),
    question: str = Form(...),
    use_default_models: bool = Form(False),
):
    # Get the default models
    embedding_model = session.exec(
        select(EmbeddingModel).where(EmbeddingModel.is_default == True)
    ).first()
    
    llm_model = session.exec(
        select(LlmModel).where(LlmModel.is_default == True)
    ).first()
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name
    
    try:
        # Detect file type and use appropriate loader
        if file.filename.endswith('.pdf'):
            loader = PyPDFLoader(temp_path)
        else:
            # Default to text loader for other files
            loader = TextLoader(temp_path)
        
        # Load and split the document
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create embeddings
        embeddings = load_embeddings_model(embedding_model.provider, 
                                          embedding_model.model_id)
        
        # Create vector store
        vector_store = FAISS.from_documents(chunks, embeddings)
        
        # Create LLM
        llm = create_llm(llm_model.provider, llm_model.model_id, 
                        temperature=0.0)
        
        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever()
        )
        
        # Run the query
        result = qa_chain({"query": question})
        
        return {"answer": result["result"]}
    
    finally:
        # Clean up temporary file
        os.unlink(temp_path)