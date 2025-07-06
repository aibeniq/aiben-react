import tempfile
import os
import asyncio
import uuid
from datetime import datetime
import threading
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, List, Union
from pydantic import BaseModel
from sqlmodel import select

from langchain_core.language_models import BaseChatModel, BaseLLM
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate

from app.core.config import settings
from app.api.deps import CurrentUser, SessionDep, VectorDBDep
from app.services.embeddings import EmbeddingService
from app.services.llms import LlmService
from app.models import (
    KnowledgeBase,
    Source as SourceORM,
    User,
)


router = APIRouter(prefix="/chat", tags=["chat"])


# Response models for chatbot endpoints
class SourceMetadata(BaseModel):
    """Metadata for document sources"""

    source: Optional[str] = None
    source_data_id: Optional[str] = None
    page: Optional[int] = None
    # Allow additional fields since metadata can contain various keys

    class Config:
        extra = "allow"


class Source(BaseModel):
    """Source document snippet with metadata"""

    content: str
    metadata: SourceMetadata


class QueryResponse(BaseModel):
    """Response model for knowledge base query endpoint"""

    answer: str
    sources: List[Source]
    session_id: str
    rephrased_question: str


class DocumentQueryResponse(BaseModel):
    """Response model for document query endpoint"""

    answer: str
    sources: List[Source]
    session_id: str
    rephrased_question: str


class TextQueryResponse(BaseModel):
    """Response model for text query endpoint"""

    answer: str
    session_id: str
    rephrased_question: str


# Create a simple cache for LLMs only (might use redis for production)
class SessionCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
        self.expiry = {}  # For tracking session expiration
        self._cleanup_interval = 3600  # 1 hour in seconds

    def get(self, session_id):
        with self.lock:
            if session_id in self.cache:
                # Update last access time
                self.expiry[session_id] = datetime.now()
                return self.cache[session_id]
        return None

    def set(self, session_id, data):
        with self.lock:
            self.cache[session_id] = data
            self.expiry[session_id] = datetime.now()

    def cleanup(self):
        """Remove sessions older than 30 minutes"""
        now = datetime.now()
        with self.lock:
            expired = [
                sid for sid, time in self.expiry.items() if (now - time).seconds > 1800
            ]  # 30 minutes
            for sid in expired:
                if sid in self.cache:
                    del self.cache[sid]
                if sid in self.expiry:
                    del self.expiry[sid]


# Initialize the cache
session_cache = SessionCache()


def rephrase_question_with_context(
    llm: BaseChatModel,
    chat_history: str,
    current_question: str,
) -> str:
    """Rephrase the user's latest question considering previous chat context"""

    # Skip rephrasing if this is the first question
    if not chat_history or chat_history.count("\n\n") < 1:
        print("No previous context to consider, returning original question")
        return current_question

    try:
        prompt_template = PromptTemplate.from_template(
            settings.CHATBOT_REPHRASING_PROMPT_TEMPLATE
        )
        variables = {"chat_history": chat_history, "question": current_question}
        prompt = prompt_template.invoke(variables)
        response = llm.invoke(prompt)

        rephrased_question = response.content.strip()
        print(f"Original question: {current_question}")
        print(f"Rephrased question: {rephrased_question}")
        return rephrased_question

    except Exception as e:
        print(f"Error rephrasing question: {e}")
        return current_question


@router.post("/knowledge-base/{kb_id}", response_model=QueryResponse)
async def query_knowledge_base(
    session: SessionDep,
    current_user: CurrentUser,
    vectordb_service: VectorDBDep,
    kb_id: str,
    question: str,
    chat_history: str = None,
    use_default_models: bool = False,
    session_id: str = None,
    is_follow_up: bool = False,
):
    """Query a knowledge base with a question."""
    try:
        print(
            f"Received request - session_id: {session_id}, is_follow_up: {is_follow_up}"
        )

        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Check if we have a cached LLM for this session
        cached_data = session_cache.get(session_id)
        print(
            f"Session cache lookup - ID: {session_id}, Found: {cached_data is not None}"
        )

        llm = None

        if is_follow_up and cached_data and cached_data.get("kb_id") == kb_id:
            print(f"Using cached LLM for session {session_id}")
            llm = cached_data.get("llm")

        # If no cached LLM, we need to set everything up
        if not llm or not isinstance(llm, BaseChatModel):
            print("Setting up new resources for knowledge base query")
            # 1. Retrieve knowledge base from database
            kb = session.get(KnowledgeBase, kb_id)
            if not kb:
                raise HTTPException(status_code=404, detail="Knowledge base not found")

            # Check access rights
            if kb.owner_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have access to this knowledge base",
                )

            # 2. Get the LLM
            llm = LlmService.get_model(current_user.default_llm)

            # Cache the LLM
            session_cache.set(
                session_id,
                {
                    "kb_id": kb_id,
                    "llm": llm,
                },
            )

        # Get knowledge base info for vectordb service
        kb = session.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # Get embedding model info for the knowledge base
        if kb.embedding_model_id:
            if EmbeddingService.is_valid_model_id(kb.embedding_model_id):
                embedding_model = EmbeddingService.get_model_spec(kb.embedding_model_id)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Knowledge base has an invalid embedding model",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Knowledge base has no embedding model",
            )

        # Rephrase the question using chat history if available
        if chat_history:
            print("Rephrasing question with context")
            rephrased_question = rephrase_question_with_context(
                llm, chat_history, question
            )
        else:
            rephrased_question = question

        # Search for relevant chunks using vectordb service
        search_result = vectordb_service.search_semantic(
            query=rephrased_question,
            embedding_model_id=embedding_model.id,
            knowledge_base_id=str(kb.id),
            limit=5,
            output_fields=["content", "source_id", "title", "author", "url"],
        )

        if not search_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {search_result.get('error', 'Unknown error')}",
            )

        chunks = search_result["results"]
        context = "\n\n".join([chunk["entity"]["content"] for chunk in chunks])
        print(
            "Retrieved context:",
            context[:200] + "..." if len(context) > 200 else context,
        )

        # Create a list of sources for citation
        sources = []
        for chunk in chunks:
            entity = chunk["entity"]

            # Create metadata similar to the old format
            metadata = {
                "source_id": entity.get("source_id", ""),
                "title": entity.get("title", ""),
                "author": entity.get("author", ""),
                "url": entity.get("url", ""),
            }

            # Try to get source id from the source table
            if entity.get("source_id"):
                source_entry = session.exec(
                    select(SourceORM).where(SourceORM.id == entity["source_id"])
                ).first()

                if source_entry:
                    metadata["source_id"] = str(source_entry.id)
                    # Use the source name if available
                    if source_entry.name:
                        metadata["source"] = source_entry.name
                    print(f"Found source entry with ID: {source_entry.id}")
                else:
                    print(
                        f"No source entry found for source_id: {entity.get('source_id')}"
                    )

            source = {
                "content": (
                    entity["content"][:300] + "..."
                    if len(entity["content"]) > 300
                    else entity["content"]
                ),
                "metadata": metadata,
            }
            sources.append(source)

        # Generate the answer
        try:
            print("Generating answer for knowledge base query...")
            # Define prompt for question answering
            qa_prompt_template = PromptTemplate.from_template(
                settings.CHATBOT_KB_QA_PROMPT_TEMPLATE
            )
            variables = {"context": context, "question": rephrased_question}
            prompt = qa_prompt_template.invoke(variables)
            answer = llm.invoke(prompt)
            print(f"Got response: {answer.content[:100]}...")
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating answer: {str(e)}"
            )

        # Record the interaction
        LlmService.record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot",
            input_data={
                "question": question,
                "rephrased_question": rephrased_question,
                "kb_id": kb_id,
            },
            output_data=answer.content,
            metadata={
                "session_id": session_id,
                "is_follow_up": is_follow_up,
                "sources": [s["metadata"] for s in sources],
            },
        )

        return {
            "answer": answer.content,
            "sources": sources,
            "session_id": session_id,  # Return session ID for client to use in follow-ups
            "rephrased_question": rephrased_question,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error querying knowledge base: {str(e)}"
        )


@router.post("/document", response_model=DocumentQueryResponse)
async def query_document(
    session: SessionDep,
    current_user: CurrentUser,
    question: str = None,
    chat_history: str = None,
    use_default_models: bool = False,
    session_id: str = None,
    is_follow_up: bool = False,
    file: UploadFile = File(None),
):
    """Query an uploaded document with a question."""
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    # If it's a follow-up but no session ID provided, can't proceed
    if is_follow_up and not session_id:
        raise HTTPException(
            status_code=400, detail="Session ID required for follow-up questions"
        )

    # If not a follow-up, we need a file
    if not is_follow_up and not file:
        raise HTTPException(
            status_code=400, detail="File is required for initial questions"
        )

    try:
        # Check if we have a cached retriever for this session
        retriever = None
        llm = None
        temp_path = None

        if is_follow_up and session_id:
            print("Using cached resources for follow-up question")
            cached_data = session_cache.get(session_id)
            if cached_data:
                print(f"Using cached resources for document session {session_id}")
                retriever = cached_data.get("retriever")
                llm = cached_data.get("llm")

        # If no cached retriever or this is a new document, set up everything
        if not retriever:
            print("Setting up new resources for document query")
            # Get the user's default models
            user = session.get(User, current_user.id)
            if not user:
                raise HTTPException(status_code=400, detail="User not found")
            if not user.default_embedding_model:
                raise HTTPException(
                    status_code=400, detail="User has no default embedding model"
                )
            if not user.default_llm:
                raise HTTPException(
                    status_code=400, detail="User has no default LLM model"
                )

            model_info = EmbeddingService.get_model_spec(user.default_embedding_model)
            model_id = model_info.id

            llm = LlmService.get_model(user.default_llm)

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(await file.read())
                temp_path = temp_file.name

            # Detect file type and use appropriate loader
            if file.filename.endswith(".pdf"):
                loader = PyPDFLoader(temp_path)
            else:
                # Default to text loader for other files
                loader = TextLoader(temp_path)

            # Load and split the document
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)

            # Create embeddings
            embeddings = EmbeddingService.get_model(model_id=model_id)

            # Create vector store in a temp directory that persists for the session
            vector_dir = tempfile.mkdtemp()
            vector_store = Chroma.from_documents(
                documents=chunks, embedding=embeddings, persist_directory=vector_dir
            )
            # Create a hybrid retriever that combines vector-based and keyword-based retrieval
            # TODO: implement this using the vectordb service
            retriever = vector_store.as_retriever(search_kwargs={"k": 5})

            # Generate a session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())

            # Cache the resources
            session_cache.set(
                session_id,
                {
                    "retriever": retriever,
                    "llm": llm,
                    "vector_dir": vector_dir,
                    "temp_path": temp_path,
                },
            )

        # Rephrase the question using chat history if available
        if chat_history:
            print("Rephrasing question with context")
            rephrased_question = rephrase_question_with_context(
                llm, chat_history, question
            )
        else:
            rephrased_question = question

        # Retrieve relevant context
        docs = retriever.get_relevant_documents(rephrased_question)
        context = "\n\n".join([doc.page_content for doc in docs])

        # Create a list of sources for citation
        sources = []
        for doc in docs:
            # Ensure source_data_id is included in metadata if available
            metadata = doc.metadata.copy()  # Copy to avoid modifying the original

            # If the metadata contains a source path that matches a pattern from a KB
            if "source" in metadata and isinstance(metadata["source"], str):
                # Try to find the corresponding source_data_id
                source_path = metadata["source"]
                source_entry = session.exec(
                    select(SourceORM).where(SourceORM.name == Path(source_path).name)
                ).first()

                if source_entry:
                    metadata["source_data_id"] = str(source_entry.source_data_id)

            source = {
                "content": (
                    doc.page_content[:300] + "..."
                    if len(doc.page_content) > 300
                    else doc.page_content
                ),
                "metadata": metadata,
            }
            sources.append(source)

        # Generate the answer - with branching for different model types
        try:
            print("Generating answer for document query...")
            qa_prompt_template = PromptTemplate.from_template(
                settings.CHATBOT_KB_QA_PROMPT_TEMPLATE
            )
            variables = {"context": context, "question": rephrased_question}
            prompt = qa_prompt_template.invoke(variables)
            answer = llm.invoke(prompt)
            print(f"Got response: {answer.content[:100]}...")
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating answer: {str(e)}"
            )

        print("Response:", answer.content[:100])
        print("Sources:", len(sources))

        # After generating the answer and before returning:
        LlmService.record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot",
            input_data={
                "question": question,
                "rephrased_question": rephrased_question,
                "document": file.filename,
            },
            output_data=answer.content,
            metadata={
                "session_id": session_id,
                "is_follow_up": is_follow_up,
                "sources": [s["metadata"] for s in sources],
            },
        )

        return {
            "answer": answer.content,
            "sources": sources,
            "session_id": session_id,
            "rephrased_question": rephrased_question,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error querying document: {str(e)}"
        )

    finally:
        # Only clean up temp files if not cached
        if temp_path and not is_follow_up and not session_cache.get(session_id):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Error removing temporary file: {e}")


# Add a cleanup task that runs periodically
@router.on_event("startup")
async def startup_event():
    async def cleanup_sessions():
        while True:
            await asyncio.sleep(1800)  # 30 minutes
            session_cache.cleanup()
            print("Session cache cleanup performed")

    asyncio.create_task(cleanup_sessions())


@router.post("/text", response_model=TextQueryResponse)
async def query_text(
    session: SessionDep,
    current_user: CurrentUser,
    question: str,
    chat_history: str = None,
    session_id: str = None,
    is_follow_up: bool = False,
):
    """Answer a direct text question without a knowledge base or document."""
    try:
        print(
            f"Received text query - session_id: {session_id}, is_follow_up: {is_follow_up}"
        )

        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Check if we have a cached LLM for this session
        cached_data = session_cache.get(session_id)
        llm = None

        if is_follow_up and cached_data:
            print(f"Using cached LLM for session {session_id}")
            llm = cached_data.get("llm")

        # If no cached LLM, get a new one
        if not llm or not isinstance(llm, BaseChatModel):
            print("Setting up new LLM for text query")
            # Get the default LLM model
            llm = LlmService.get_model(current_user.default_llm)
            print("Default LLM model retrieved:", llm)
            # Cache the LLM
            session_cache.set(session_id, {"llm": llm, "type": "text_query"})
            print("LLM cached for session", session_id)

        # Rephrase the question using chat history if available
        if chat_history:
            print("Rephrasing question with context")
            rephrased_question = rephrase_question_with_context(
                llm, chat_history, question
            )
            print("Rephrased question:", rephrased_question)
        else:
            print("No chat history, using original question")
            rephrased_question = question

        # Handle different model types
        answer = None

        try:
            print("Generating answer for text query...")
            qa_prompt_template = PromptTemplate.from_template(
                settings.CHATBOT_GENERAL_QA_PROMPT_TEMPLATE
            )
            variables = {"question": rephrased_question}
            prompt = qa_prompt_template.invoke(variables)
            answer = llm.invoke(prompt)
            print(f"Got response: {answer.content[:100]}...")
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating answer: {str(e)}"
            )

        LlmService.record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot",
            input_data={"question": question, "rephrased_question": rephrased_question},
            output_data=answer.content,
            metadata={"session_id": session_id, "is_follow_up": is_follow_up},
        )

        return {
            "answer": answer.content,
            "session_id": session_id,
            "rephrased_question": rephrased_question,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing question: {str(e)}"
        )
