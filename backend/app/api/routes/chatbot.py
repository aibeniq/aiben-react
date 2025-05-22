from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.embeddings import load_embeddings_model
from app.services.llms import create_llm, get_default_llm
from app.services.knowledgebases import get_embedding_model
from app.api.deps import CurrentUser, SessionDep
from app.models import KnowledgeBase, EmbeddingModel, LlmModel
from sqlmodel import Session, select
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
import tempfile
import os
import zipfile
from io import BytesIO

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/knowledge-base/{kb_id}")
async def query_knowledge_base(
    session: SessionDep,
    current_user: CurrentUser,
    kb_id: str,
    question: str,
    use_default_models: bool = False,
):
    """
    Query a knowledge base with a question.
    """
    try:
        # 1. Retrieve knowledge base from database
        kb = session.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        # Check access rights (optional - remove if you want public access)
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
            
            # 3. Load the vector database with the appropriate embedding model
            if use_default_models:
                # Use default embedding model
                embedding_model = session.exec(
                    select(EmbeddingModel).where(EmbeddingModel.is_default == True)
                ).first()
                if not embedding_model:
                    raise HTTPException(status_code=404, detail="No default embedding model found")
                model_id = embedding_model.model_id
                provider = embedding_model.provider
            elif kb.embedding_model_id:
                # Use the knowledge base's specific model
                embedding_model = session.get(EmbeddingModel, kb.embedding_model_id)
                if embedding_model:
                    model_id = embedding_model.model_id
                    provider = embedding_model.provider
                else:
                    # Fallback if the model was deleted
                    embedding_info = get_embedding_model(session)
                    model_id = embedding_info["model_id"]
                    provider = embedding_info["provider"]
            else:
                # Fallback to default
                embedding_info = get_embedding_model(session)
                model_id = embedding_info["model_id"]
                provider = embedding_info["provider"]
            
            print(f"Using embedding model: {model_id} ({provider})")
            embeddings = load_embeddings_model(
                provider=provider,
                model_id=model_id
            )
            
            # Load the Chroma database
            chroma_db = Chroma(persist_directory=temp_dir, embedding_function=embeddings)
            retriever = chroma_db.as_retriever(search_kwargs={"k": 5})
            
            # 4. Get the LLM
            if use_default_models:
                llm = get_default_llm(session)
                print("Using default LLM")
            else:
                # Use the knowledge base's specific LLM
                llm_model = session.get(LlmModel, kb.llm_model_id)
                if llm_model:
                    llm = create_llm(llm_model.provider, llm_model.model_id, temperature=0.0)
                    print(f"Using knowledge base's LLM: {llm_model.model_id}")
                else:
                    llm = get_default_llm(session)
                    print("Knowledge base LLM not found, using default LLM")
            
            # 5. Retrieve relevant context for the question
            docs = retriever.get_relevant_documents(question)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create a list of sources for citation
            sources = []
            for doc in docs:
                source = {
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source)
            
            # 6. Define prompt for question answering
            qa_prompt_template = """
            You are a helpful assistant that answers questions based on the provided context.
            
            CONTEXT:
            {context}
            
            QUESTION: {question}
            
            INSTRUCTIONS:
            1. Answer the question based ONLY on the information provided in the CONTEXT.
            2. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer this question."
            3. Be concise and to the point.
            4. Don't make up information or use knowledge outside the provided context.
            
            ANSWER:
            """
            
            qa_prompt = ChatPromptTemplate.from_template(qa_prompt_template)
            
            # 7. Generate the answer
            chain = qa_prompt | llm
            response = chain.invoke({
                "context": context, 
                "question": question
            })

            print("Response:", response.content)
            print("Sources:", sources)	
            
            return {
                "answer": response.content,
                "sources": sources
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying knowledge base: {str(e)}")


@router.post("/document")
async def query_document(
    session: SessionDep,
    file: UploadFile = File(...),
    question: str = None,
    use_default_models: bool = False,
):
    """
    Query an uploaded document with a question.
    """
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    # Get the default models
    embedding_model = session.exec(
        select(EmbeddingModel).where(EmbeddingModel.is_default == True)
    ).first()
    
    if not embedding_model:
        raise HTTPException(status_code=404, detail="No default embedding model found")
    
    llm_model = session.exec(
        select(LlmModel).where(LlmModel.is_default == True)
    ).first()
    
    if not llm_model:
        raise HTTPException(status_code=404, detail="No default LLM model found")
    
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
        embeddings = load_embeddings_model(
            provider=embedding_model.provider,
            model_id=embedding_model.model_id
        )
        
        # Create vector store
        with tempfile.TemporaryDirectory() as vector_dir:
            vector_store = Chroma.from_documents(
                documents=chunks, 
                embedding=embeddings,
                persist_directory=vector_dir
            )
            retriever = vector_store.as_retriever(search_kwargs={"k": 5})
            
            # Create LLM
            llm = create_llm(
                provider=llm_model.provider,
                model_id=llm_model.model_id,
                temperature=0.0
            )
            
            # Retrieve relevant context
            docs = retriever.get_relevant_documents(question)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create a list of sources for citation
            sources = []
            for doc in docs:
                source = {
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source)
            
            # Define prompt
            qa_prompt_template = """
            You are a helpful assistant that answers questions based on the provided context.
            
            CONTEXT:
            {context}
            
            QUESTION: {question}
            
            INSTRUCTIONS:
            1. Answer the question based ONLY on the information provided in the CONTEXT.
            2. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer this question."
            3. Be concise and to the point.
            4. Don't make up information or use knowledge outside the provided context.
            
            ANSWER:
            """
            
            qa_prompt = ChatPromptTemplate.from_template(qa_prompt_template)
            
            # Generate the answer
            chain = qa_prompt | llm
            response = chain.invoke({
                "context": context, 
                "question": question
            })

            print("Response:", response.content)
            print("Sources:", sources)	
            
            return {
                "answer": response.content,
                "sources": sources
            }
    
    finally:
        # Clean up temporary file
        os.unlink(temp_path)