import asyncio
import os
import tempfile
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep, VectorDBDep
from app.core.config import settings
from app.models import (
    KnowledgeBase,
    User,
)
from app.models import (
    Source as SourceORM,
)
from app.services.embeddings import EmbeddingService
from app.services.llms import LlmService

router = APIRouter(prefix="/chat", tags=["chat"])


# Response models for chatbot endpoints
class SourceMetadata(BaseModel):
    """Metadata for document sources"""

    source: str | None = None
    source_id: str | None = None
    page: int | None = None
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
    sources: list[Source]
    session_id: str
    rephrased_question: str


class DocumentQueryResponse(BaseModel):
    """Response model for document query endpoint"""

    answer: str
    sources: list[Source]
    session_id: str
    rephrased_question: str


class TextQueryResponse(BaseModel):
    """Response model for text query endpoint"""

    answer: str
    session_id: str
    rephrased_question: str


@dataclass
class SessionCacheData:
    llm: BaseChatModel
    kb_id: str | None = None
    retriever: Any | None = None


# Create a simple cache for LLMs only (might use redis for production)
class SessionCache:
    def __init__(self) -> None:
        self.cache: dict[str, SessionCacheData] = {}
        self.lock = threading.Lock()
        self.expiry: dict[str, datetime] = {}  # For tracking session expiration
        self._cleanup_interval = 3600  # 1 hour in seconds
        self._max_cache_size = 1000  # Prevent unbounded growth

    def get(self, session_id: str) -> SessionCacheData | None:
        with self.lock:
            if session_id in self.cache:
                # Update last access time
                self.expiry[session_id] = datetime.now()
                return self.cache[session_id]
        return None

    def set(self, session_id: str, data: SessionCacheData) -> None:
        with self.lock:
            # Prevent unbounded growth
            if len(self.cache) >= self._max_cache_size:
                self._cleanup_expired()

            self.cache[session_id] = data
            self.expiry[session_id] = datetime.now()

    def _cleanup_expired(self) -> None:
        """Internal cleanup method that assumes lock is already held"""
        now = datetime.now()
        expired = [
            sid
            for sid, time in self.expiry.items()
            if (now - time).total_seconds() > 1800  # 30 minutes
        ]

        for sid in expired:
            self.cache.pop(sid, None)  # Use pop to avoid KeyError
            self.expiry.pop(sid, None)

    def cleanup(self) -> None:
        """Remove sessions older than 30 minutes"""
        try:
            with self.lock:
                self._cleanup_expired()
        except Exception as e:
            print(f"Error during cache cleanup: {e}")
            # Continue execution even if cleanup fails


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

        if not isinstance(response.content, str):
            raise HTTPException(
                status_code=500,
                detail=f"Response content is not a string: {response.content}",
            )
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
    chat_history: str | None = None,
    session_id: str | None = None,
    is_follow_up: bool = False,
) -> QueryResponse:
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

        if is_follow_up and cached_data and cached_data.kb_id == kb_id:
            print(f"Using cached LLM for session {session_id}")
            llm = cached_data.llm

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
                SessionCacheData(llm=llm, kb_id=kb_id),
            )

        # Get knowledge base info for vectordb service
        kb = session.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        # Get embedding model info for the knowledge base
        embedding_model = EmbeddingService.get_model_spec(kb.embedding_model_id)
        if not embedding_model:
            raise HTTPException(
                status_code=400,
                detail="Knowledge base has an invalid embedding model",
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
        sources: list[Source] = []
        for chunk in chunks:
            entity = chunk["entity"]

            # Create metadata similar to the old format
            metadata = SourceMetadata(
                source=entity.get("source", ""),
                source_id=entity.get("source_id", ""),
                page=entity.get("page", ""),
            )

            # Try to get source id from the source table
            if entity.get("source_id"):
                source_entry = session.exec(
                    select(SourceORM).where(SourceORM.id == entity["source_id"])
                ).first()

                if source_entry:
                    metadata.source_id = str(source_entry.id)
                    # Use the source name if available
                    if source_entry.name:
                        metadata.source = source_entry.name
                    print(f"Found source entry with ID: {source_entry.id}")
                else:
                    print(
                        f"No source entry found for source_id: {entity.get('source_id')}"
                    )

            source = Source(
                content=(
                    entity["content"][:300] + "..."
                    if len(entity["content"]) > 300
                    else entity["content"]
                ),
                metadata=metadata,
            )
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
            if not isinstance(answer.content, str):
                raise HTTPException(
                    status_code=500,
                    detail=f"Response content is not a string: {answer.content}",
                )
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
                "sources": [s.metadata for s in sources],
            },
        )

        return QueryResponse(
            answer=answer.content,
            sources=sources,
            session_id=session_id,  # Return session ID for client to use in follow-ups
            rephrased_question=rephrased_question,
        )

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
    question: str | None = None,
    chat_history: str | None = None,
    session_id: str | None = None,
    is_follow_up: bool = False,
    file: UploadFile = File(None),
) -> DocumentQueryResponse:
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

    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")

    try:
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Check if we have a cached retriever for this session
        retriever = None
        llm = None
        temp_path = None

        if is_follow_up and session_id:
            print("Using cached resources for follow-up question")
            cached_data = session_cache.get(session_id)
            if cached_data and cached_data.retriever:
                print(f"Using cached resources for document session {session_id}")
                retriever = cached_data.retriever
                llm = cached_data.llm

        # If no cached retriever or this is a new document, set up everything
        if not retriever or not isinstance(llm, BaseChatModel):
            print("Setting up new resources for document query")
            # Get the user's default models
            user = session.get(User, current_user.id)
            if not user:
                raise HTTPException(status_code=400, detail="User not found")

            model_info = EmbeddingService.get_model_spec(user.default_embedding_model)
            if not model_info:
                raise HTTPException(
                    status_code=400, detail="Invalid user default embedding model"
                )
            model_id = model_info.id

            llm = LlmService.get_model(user.default_llm)

            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(await file.read())
                temp_path = temp_file.name

            # Detect file type and use appropriate loader
            if file.filename.endswith(".pdf"):
                pdf_loader = PyPDFLoader(temp_path)
                documents = pdf_loader.load()
            else:
                # Default to text loader for other files
                text_loader = TextLoader(temp_path)
                documents = text_loader.load()

            # Load and split the document
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

            # Cache the resources
            session_cache.set(
                session_id,
                SessionCacheData(llm=llm, retriever=retriever),
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
        sources: list[Source] = []
        for doc in docs:
            # Ensure source_data_id is included in metadata if available
            metadata = SourceMetadata(
                source=doc.metadata.get("source", ""),
                source_id=doc.metadata.get("source_id", ""),
                page=doc.metadata.get("page", ""),
            )

            # If the metadata contains a source path that matches a pattern from a KB
            if metadata.source and isinstance(metadata.source, str):
                # Try to find the corresponding source_data_id
                source_path = metadata.source
                source_entry = session.exec(
                    select(SourceORM).where(SourceORM.name == Path(source_path).name)
                ).first()

                if source_entry:
                    metadata.source_id = str(source_entry.source_data_id)

            source = Source(
                content=(
                    doc.page_content[:300] + "..."
                    if len(doc.page_content) > 300
                    else doc.page_content
                ),
                metadata=metadata,
            )
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
            if not isinstance(answer.content, str):
                raise HTTPException(
                    status_code=500,
                    detail=f"Response content is not a string: {answer.content}",
                )
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
                "sources": [s.metadata for s in sources],
            },
        )

        return DocumentQueryResponse(
            answer=answer.content,
            sources=sources,
            session_id=session_id,
            rephrased_question=rephrased_question,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error querying document: {str(e)}"
        )

    finally:
        # Only clean up temp files if not cached
        if (
            temp_path
            and not is_follow_up
            and session_id
            and not session_cache.get(session_id)
        ):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Error removing temporary file: {e}")


# Add a cleanup task that runs periodically
@router.on_event("startup")
async def startup_event() -> None:
    async def cleanup_sessions() -> None:
        while True:
            try:
                await asyncio.sleep(1800)  # 30 minutes
                session_cache.cleanup()
                print("Session cache cleanup performed")
            except Exception as e:
                print(f"Error in cleanup task: {e}")
                # Continue running even if cleanup fails

    asyncio.create_task(cleanup_sessions())


@router.post("/text", response_model=TextQueryResponse)
async def query_text(
    session: SessionDep,
    current_user: CurrentUser,
    question: str,
    chat_history: str | None = None,
    session_id: str | None = None,
    is_follow_up: bool = False,
) -> TextQueryResponse:
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
            llm = cached_data.llm

        # If no cached LLM, get a new one
        if not llm or not isinstance(llm, BaseChatModel):
            print("Setting up new LLM for text query")
            # Get the default LLM model
            llm = LlmService.get_model(current_user.default_llm)
            print("Default LLM model retrieved:", llm)
            # Cache the LLM
            session_cache.set(session_id, SessionCacheData(llm=llm))
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
            if not isinstance(answer.content, str):
                raise HTTPException(
                    status_code=500,
                    detail=f"Response content is not a string: {answer.content}",
                )
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

        return TextQueryResponse(
            answer=answer.content,
            session_id=session_id,
            rephrased_question=rephrased_question,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing question: {str(e)}"
        )
