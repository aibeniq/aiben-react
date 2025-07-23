from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, List
from pydantic import BaseModel
import tempfile
import os
import uuid
import traceback
import re
from app.services.embeddings import load_embeddings_model
from app.services.llms import (
    create_llm,
    get_default_llm,
    invoke_llm,
    record_llm_interaction,
)
from app.services.knowledgebases import get_embedding_model
from app.services.retrievers import (
    create_ensemble_retriever,
)  # Import the ensemble retriever
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    KnowledgeBase,
    EmbeddingModel,
    LlmModel,
    Source as SourceORM,
    SourceData,
    User,
)
from app.core.config import settings
from app.services.pdf_utils import load_pdf_with_pypdf
from sqlmodel import select

# from langchain_community.document_loaders import PyPDFLoader  # Removed - using pypdf instead

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import tempfile
import os
import zipfile
import traceback
from io import BytesIO
import asyncio
import uuid
import re
from datetime import datetime
import threading
from pathlib import Path

router = APIRouter(prefix="/chat", tags=["chat"])


# Request models for chat endpoints
class ChatRequest(BaseModel):
    """Request model for general chat endpoint"""

    prompt: str
    knowledge_base_id: Optional[str] = None
    search_type: str = "vector"  # "vector" or "full_text"
    chat_history: Optional[str] = None
    session_id: Optional[str] = None
    is_follow_up: bool = False


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


# Create a simple cache for vector databases and retrievers
# might want to use a more robust solution like Redis for production
class SessionCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
        self.expiry = {}  # For tracking session expiration
        self._cleanup_interval = 3600  # 1 hour in seconds
        self._session_timeout = 3600  # 1 hour timeout (increased from 30 minutes)

    def get(self, session_id):
        with self.lock:
            if session_id in self.cache:
                # Update last access time
                self.expiry[session_id] = datetime.now()
                print(f"✅ Cache HIT for session {session_id}")
                return self.cache[session_id]
            else:
                print(f"❌ Cache MISS for session {session_id}")
                print(f"Available sessions: {list(self.cache.keys())}")
                return None

    def set(self, session_id, data):
        with self.lock:
            self.cache[session_id] = data
            self.expiry[session_id] = datetime.now()
            print(f"💾 Cache SET for session {session_id}")
            print(f"Cache now contains {len(self.cache)} sessions")

    def cleanup(self):
        """Remove sessions older than 1 hour (increased timeout)"""
        now = datetime.now()
        with self.lock:
            expired = [
                sid for sid, time in self.expiry.items() 
                if (now - time).total_seconds() > self._session_timeout
            ]
            for sid in expired:
                if sid in self.cache:
                    del self.cache[sid]
                    print(f"🗑️ Cleaned up expired session {sid}")
                if sid in self.expiry:
                    del self.expiry[sid]
            if expired:
                print(f"Session cleanup removed {len(expired)} expired sessions")
            else:
                print(f"Session cleanup: no expired sessions found (active: {len(self.cache)})")

    def debug_info(self):
        """Debug method to see cache state"""
        with self.lock:
            now = datetime.now()
            info = {
                "total_sessions": len(self.cache),
                "sessions": {}
            }
            for sid, last_access in self.expiry.items():
                age_seconds = (now - last_access).total_seconds()
                info["sessions"][sid] = {
                    "age_seconds": age_seconds,
                    "expires_in": self._session_timeout - age_seconds
                }
            return info


# Initialize the cache
session_cache = SessionCache()


async def _handle_full_text_kb_query(
    session: SessionDep,
    current_user: CurrentUser,
    kb_id: str,
    question: str,
    chat_history: str = None,
    use_default_models: bool = False,
    session_id: str = None,
    is_follow_up: bool = False,
):
    """Handle full text scan for knowledge base query."""
    from app.services.text_processing import chunk_text

    # Get the knowledge base
    kb = session.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Check access rights
    if kb.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this knowledge base",
        )

    # Get LLM
    llm = get_default_llm(session, current_user)

    # Rephrase the question using chat history if available
    if chat_history:
        rephrased_question = rephrase_question_with_context(llm, chat_history, question)
    else:
        rephrased_question = question

    # Get all source files from the knowledge base
    sources = session.exec(
        select(SourceORM).where(SourceORM.knowledge_base_id == kb.id)
    ).all()

    if not sources:
        raise HTTPException(
            status_code=404, detail="No sources found in knowledge base"
        )

    # Extract text from all files and process chunks
    all_chunk_analyses = []
    source_citations = []

    print(f"Processing {len(sources)} sources from knowledge base {kb.title}")

    for source in sources:
        print(f"Processing source: {source.name}")
        # Get source data
        source_data = session.get(SourceData, source.source_data_id)
        if not source_data:
            print(f"No source data found for source {source.name}")
            continue

        print(
            f"Found source data for {source.name}, size: {len(source_data.data) if source_data.data else 0} bytes"
        )

        # Extract text from the source
        try:
            # The source_data.data contains the file as a ZIP, we need to extract it first
            from app.api.routes.veradoc import extract_text_from_file

            # Debug: Check the first few bytes of the data
            data_header = source_data.data[:20] if source_data.data else b""
            print(f"Data header for {source.name}: {data_header}")

            # Check if this is actually a ZIP file
            if not source_data.data.startswith(b"PK"):
                print(
                    f"WARNING: {source.name} does not appear to be a ZIP file, trying direct extraction"
                )
                file_content = extract_text_from_file(source_data.data, source.name)
            else:
                # Extract the file content from the ZIP
                zip_data = BytesIO(source_data.data)
                with zipfile.ZipFile(zip_data, "r") as zip_file:
                    # Get the first file in the archive (there should only be one)
                    file_info = zip_file.infolist()[0]
                    print(f"Extracting file: {file_info.filename} from ZIP")
                    raw_file_content = zip_file.read(file_info.filename)
                    print(f"Extracted {len(raw_file_content)} bytes from ZIP")

                    # Check the header of the extracted content
                    extracted_header = (
                        raw_file_content[:20] if raw_file_content else b""
                    )
                    print(f"Extracted file header: {extracted_header}")

                    # Now extract text from the raw file content
                    file_content = extract_text_from_file(raw_file_content, source.name)

        except zipfile.BadZipFile as e:
            print(f"Error extracting ZIP file for source {source.name}: {e}")
            print(
                f"Data starts with: {source_data.data[:50] if source_data.data else 'No data'}"
            )
            # Try direct extraction as fallback
            try:
                print(f"Attempting direct text extraction for {source.name}")
                file_content = extract_text_from_file(source_data.data, source.name)
            except Exception as fallback_e:
                print(
                    f"Fallback extraction also failed for {source.name}: {fallback_e}"
                )
                file_content = f"Failed to extract from {source.name}: ZIP error: {str(e)}, Direct error: {str(fallback_e)}"
        except Exception as e:
            print(f"Error extracting text from source {source.name}: {e}")
            file_content = f"Failed to extract text from {source.name}: {str(e)}"

        if (
            file_content.strip()
            and not file_content.startswith("Failed to extract")
            and not file_content.startswith("Unable to extract")
        ):
            print(
                f"Successfully extracted {len(file_content)} characters from {source.name}"
            )
            # Chunk the text
            chunks = chunk_text(
                file_content, max_tokens=settings.FULL_SCAN_DOCUMENT_CHUNK_SIZE
            )
            print(f"Created {len(chunks)} chunks from {source.name}")

            # Analyze each chunk
            for i, chunk in enumerate(chunks):
                try:
                    print(f"Analyzing chunk {i+1}/{len(chunks)} from {source.name}")
                    chunk_analysis = invoke_llm(
                        llm,
                        settings.CHATBOT_FULL_TEXT_CHUNK_PROMPT_TEMPLATE,
                        {"chunk": chunk, "question": rephrased_question},
                    )

                    if "No relevant information found" not in chunk_analysis:
                        print(
                            f"Found relevant information in chunk {i+1} from {source.name}"
                        )
                        all_chunk_analyses.append(chunk_analysis)
                        source_citations.append(
                            {
                                "content": chunk,  # Remove 300 character truncation
                                "metadata": {
                                    "source": source.name,
                                    "source_data_id": str(source.source_data_id),
                                },
                            }
                        )
                    else:
                        print(
                            f"No relevant information found in chunk {i+1} from {source.name}"
                        )
                except Exception as e:
                    print(f"Error analyzing chunk {i+1} from {source.name}: {e}")
                    continue
        else:
            print(
                f"Could not extract text from source {source.name}: {file_content[:100] if file_content else 'No content'}"
            )

    print(
        f"Full text scan complete. Found {len(all_chunk_analyses)} relevant chunk analyses."
    )

    if not all_chunk_analyses:
        final_answer = "I couldn't find relevant information to answer your question in the knowledge base."
        sources = []
    else:
        # Synthesize all chunk analyses
        chunk_analyses_text = "\n\n".join(
            [
                f"Analysis {i+1}: {analysis}"
                for i, analysis in enumerate(all_chunk_analyses)
            ]
        )

        final_answer = invoke_llm(
            llm,
            settings.CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE,
            {"question": rephrased_question, "chunk_analyses": chunk_analyses_text},
        )

    # Record the interaction
    record_llm_interaction(
        session=session,
        user_id=current_user.id,
        functionality="chatbot_full_text",
        input_data={
            "question": question,
            "rephrased_question": rephrased_question,
            "kb_id": kb_id,
            "search_mode": "full_text",
        },
        output_data=final_answer,
        metadata={
            "session_id": session_id,
            "is_follow_up": is_follow_up,
            "chunk_count": len(all_chunk_analyses),
        },
    )

    return {
        "answer": final_answer,
        "sources": source_citations,
        "session_id": session_id,
        "rephrased_question": rephrased_question,
    }


async def _handle_full_text_document_query(
    session: SessionDep,
    current_user: CurrentUser,
    files: List[UploadFile],
    question: str,
    chat_history: str = None,
    use_default_models: bool = False,
    session_id: str = None,
    is_follow_up: bool = False,
):
    """Handle full text scan for document query with multiple files."""
    from app.services.text_processing import chunk_text

    # Get LLM
    llm = get_default_llm(session, current_user)

    # Rephrase the question using chat history if available
    if chat_history:
        rephrased_question = rephrase_question_with_context(llm, chat_history, question)
    else:
        rephrased_question = question

    # Process each file independently
    all_document_analyses = []
    all_source_citations = []
    temp_paths = []

    try:
        # Process each file
        for file_idx, file in enumerate(files):
            # Save uploaded file temporarily and extract text
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(await file.read())
                temp_path = temp_file.name
                temp_paths.append(temp_path)
            # File is now closed and ready to be read by loaders

            # Extract text from file
            if file.filename.endswith(".pdf"):
                documents = load_pdf_with_pypdf(temp_path, file.filename)
            else:
                loader = TextLoader(temp_path)
                documents = loader.load()
            full_text = "\n\n".join([doc.page_content for doc in documents])

            # Chunk the text
            chunks = chunk_text(
                full_text, max_tokens=settings.FULL_SCAN_DOCUMENT_CHUNK_SIZE
            )

            # Analyze each chunk for this file
            file_chunk_analyses = []
            file_source_citations = []

            for i, chunk in enumerate(chunks):
                try:
                    chunk_analysis = invoke_llm(
                        llm,
                        settings.CHATBOT_FULL_TEXT_CHUNK_PROMPT_TEMPLATE,
                        {"chunk": chunk, "question": rephrased_question},
                    )

                    if "No relevant information found" not in chunk_analysis:
                        file_chunk_analyses.append(chunk_analysis)
                        file_source_citations.append(
                            {
                                "content": chunk,  # Remove 300 character truncation
                                "metadata": {
                                    "source": file.filename,
                                    "chunk": i + 1,
                                    "file_index": file_idx + 1,
                                },
                            }
                        )
                except Exception as e:
                    print(f"Error analyzing chunk {i} in file {file.filename}: {e}")
                    continue

            # If we found relevant chunks in this file, create a document-level analysis
            if file_chunk_analyses:
                # Synthesize chunks for this specific document
                file_chunk_analyses_text = "\n\n".join(
                    [
                        f"Chunk {i+1}: {analysis}"
                        for i, analysis in enumerate(file_chunk_analyses)
                    ]
                )

                # Create a document-level analysis
                document_analysis = invoke_llm(
                    llm,
                    settings.CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE,
                    {
                        "question": rephrased_question,
                        "chunk_analyses": file_chunk_analyses_text,
                    },
                )

                # Store the analysis for this document
                all_document_analyses.append(
                    {"filename": file.filename, "analysis": document_analysis}
                )

                # Add source citations for this file
                all_source_citations.extend(file_source_citations)

        # If no documents had relevant information
        if not all_document_analyses:
            final_answer = "I couldn't find relevant information to answer your question in any of the uploaded documents."
            sources = []
        elif len(all_document_analyses) == 1:
            # If only one document had relevant information, use its analysis directly
            final_answer = all_document_analyses[0]["analysis"]
            sources = all_source_citations
        else:
            # If multiple documents have relevant information, synthesize across documents
            document_analyses_text = "\n\n".join(
                [
                    f"Document '{doc['filename']}' Analysis: {doc['analysis']}"
                    for doc in all_document_analyses
                ]
            )

            # Create a final synthesis across all documents
            final_answer = invoke_llm(
                llm,
                f"""Based on the following analyses from multiple documents, provide a comprehensive answer to the question: {rephrased_question}

Document Analyses:
{{document_analyses}}

Please synthesize the information from all documents into a coherent, comprehensive answer. If there are contradictions between documents, note them. If documents complement each other, combine the insights.""",
                {"document_analyses": document_analyses_text},
            )
            sources = all_source_citations

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot_full_text",
            input_data={
                "question": question,
                "rephrased_question": rephrased_question,
                "documents": [file.filename for file in files],
                "search_mode": "full_text",
            },
            output_data=final_answer,
            metadata={
                "session_id": session_id,
                "is_follow_up": is_follow_up,
                "document_count": len(files),
                "relevant_documents": len(all_document_analyses),
            },
        )

        return {
            "answer": final_answer,
            "sources": sources,
            "session_id": session_id,
            "rephrased_question": rephrased_question,
        }

    finally:
        # Clean up temp files
        for temp_path in temp_paths:
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Error removing temporary file {temp_path}: {e}")


def rephrase_question_with_context(llm, chat_history, current_question):
    """Rephrase the user's latest question considering previous chat context"""

    # Skip rephrasing if this is the first question
    if not chat_history or chat_history.count("\n\n") < 1:
        print("No previous context to consider, returning original question")
        return current_question

    print("Now rephrasing question with context")

    # Use the unified invoke_llm function
    try:
        rephrased_question = invoke_llm(
            llm,
            settings.CHATBOT_REPHRASING_PROMPT_TEMPLATE,
            {"chat_history": chat_history, "question": current_question},
        )

        rephrased_question = rephrased_question.strip()
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
    kb_id: str,
    question: str,
    chat_history: str = None,
    use_default_models: bool = False,
    session_id: str = None,
    is_follow_up: bool = False,
    search_mode: str = "vector",  # Add search mode parameter
):
    """Query a knowledge base with a question using either vector search or full text scan."""
    try:
        print(
            f"Received request - session_id: {session_id}, is_follow_up: {is_follow_up}, search_mode: {search_mode}"
        )

        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # Validate search mode
        if search_mode not in ["vector", "full_text"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid search mode. Must be 'vector' or 'full_text'",
            )

        # Handle full text scan mode
        if search_mode == "full_text":
            return await _handle_full_text_kb_query(
                session,
                current_user,
                kb_id,
                question,
                chat_history,
                use_default_models,
                session_id,
                is_follow_up,
            )

        # Continue with existing vector search implementation
        # Check if we have a cached retriever for this session
        cached_data = session_cache.get(session_id)
        print(
            f"Session cache lookup - ID: {session_id}, Found: {cached_data is not None}"
        )

        if cached_data:
            print(f"Cache contents for {session_id}: {list(cached_data.keys())}")
        retriever = None
        llm = None

        print("Session ID:", session_id)
        print("Is follow-up:", is_follow_up)
        print("Cached data:", cached_data)
        print("Cached KB ID:", cached_data.get("kb_id") if cached_data else None)
        print("KB ID:", kb_id)

        if is_follow_up and cached_data and cached_data.get("kb_id") == kb_id:
            print(f"Using cached resources for session {session_id}")
            retriever = cached_data.get("retriever")
            llm = cached_data.get("llm")

        # If no cached retriever, we need to set everything up
        if not retriever:
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

            # 2. Create a temporary directory for ChromaDB
            temp_dir = tempfile.mkdtemp()

            # Extract the zipped ChromaDB into the temp directory
            if kb.data:
                with zipfile.ZipFile(BytesIO(kb.data), "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            else:
                raise HTTPException(
                    status_code=400, detail="Knowledge base has no vector database data"
                )

            # 3. Use knowledge base's embedding model or fallback to default
            if kb.embedding_model_id:
                # Use knowledge base's specific model
                embedding_model = session.get(EmbeddingModel, kb.embedding_model_id)
                if embedding_model:
                    model_id = embedding_model.model_id
                    provider = embedding_model.provider
                else:
                    # Fallback
                    embedding_info = get_embedding_model(session)
                    model_id = embedding_info["model_id"]
                    provider = embedding_info["provider"]
            elif use_default_models:
                # Get the user's default embedding model
                user = session.get(User, current_user.id)
                if user and user.default_embedding_model:
                    embedding_model = session.get(
                        EmbeddingModel, user.default_embedding_model
                    )
                    if embedding_model:
                        model_id = embedding_model.model_id
                        provider = embedding_model.provider
                    else:
                        raise HTTPException(
                            status_code=404,
                            detail="Default embedding model not found for user",
                        )
                else:
                    # Fallback to system default (first system model)
                    embedding_model = session.exec(
                        select(EmbeddingModel).where(EmbeddingModel.owner_id.is_(None))
                    ).first()
                    if embedding_model:
                        model_id = embedding_model.model_id
                        provider = embedding_model.provider
                    else:
                        raise HTTPException(
                            status_code=404, detail="No default embedding model found"
                        )
            else:
                # Fallback
                embedding_info = get_embedding_model(session)
                model_id = embedding_info["model_id"]
                provider = embedding_info["provider"]

            embeddings = load_embeddings_model(provider=provider, model_id=model_id)

            # Load the Chroma database
            chroma_db = Chroma(
                persist_directory=temp_dir, embedding_function=embeddings
            )

            # Create a hybrid retriever that combines vector-based and keyword-based retrieval
            retriever = create_ensemble_retriever(
                chroma_db=chroma_db,
                vector_weight=0.7,  # Weight for vector-based retrieval
                keyword_weight=0.3,  # Weight for keyword-based retrieval
                search_kwargs={"k": settings.RAG_NUM_CHUNKS},  # Use config value
            )

            # 4. Get the LLM
            if use_default_models:
                llm = get_default_llm(session, current_user)
                print("Default LLM model retrieved")
            else:
                llm_model = session.get(LlmModel, kb.llm_model_id)
                if llm_model:
                    llm = create_llm(
                        llm_model.provider, llm_model.model_id, temperature=0.0
                    )
                else:
                    llm = get_default_llm(session, current_user)

            # Cache the resources
            session_cache.set(
                session_id,
                {
                    "kb_id": kb_id,
                    "retriever": retriever,
                    "llm": llm,
                    "temp_dir": temp_dir,  # Store the temp directory path to avoid deletion
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

        # 5. Retrieve relevant context for the question
        docs = retriever.get_relevant_documents(rephrased_question)
        context = "\n\n".join([doc.page_content for doc in docs])
        print("Retrieved context:", context)

        # Create a list of sources for citation
        sources = []
        for doc in docs:
            # Ensure source_data_id is included in metadata if available
            metadata = doc.metadata.copy()  # Copy to avoid modifying the original

            # If the metadata contains a source path that matches a pattern from a KB
            if "source" in metadata and isinstance(metadata["source"], str):
                # Try to find the corresponding source_data_id
                source_path = metadata["source"]
                # Extract just the filename
                raw_filename = Path(source_path).name

                # Extract the real filename after the underscore using regex
                # This looks for any characters followed by an underscore, then captures everything after
                match = re.search(r"^[^_]*_(.+)$", raw_filename)
                if match:
                    # Use the captured group (everything after the underscore)
                    filename = match.group(1)
                else:
                    # Fallback to the original filename if no underscore found
                    filename = raw_filename

                # Debug info
                print(f"Looking up source with filename: {filename}")

                # Try to find the source by name
                source_entry = session.exec(
                    select(SourceORM).where(SourceORM.name == filename)
                ).first()

                if source_entry:
                    print(f"Found source entry with ID: {source_entry.source_data_id}")
                    metadata["source_data_id"] = str(source_entry.source_data_id)
                else:
                    print(f"No source entry found for filename: {filename}")

            source = {
                "content": doc.page_content,  # Remove 300 character truncation
                "metadata": metadata,
            }
            sources.append(source)

        # 6. Define prompt for question answering
        qa_prompt_template = settings.CHATBOT_KB_QA_PROMPT_TEMPLATE

        # 7. Generate the answer - with branching for different model types
        try:
            print("Generating answer for knowledge base query...")
            answer_content = invoke_llm(
                llm,
                qa_prompt_template,
                {"context": context, "question": rephrased_question},
            )
            print(f"Got response: {answer_content[:100]}...")
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating answer: {str(e)}"
            )

        # After generating the answer and before returning:
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot",
            input_data={
                "question": question,
                "rephrased_question": rephrased_question,
                "kb_id": kb_id,
            },
            output_data=answer_content,
            metadata={
                "session_id": session_id,
                "is_follow_up": is_follow_up,
                "sources": [s["metadata"] for s in sources],
            },
        )

        return {
            "answer": answer_content,
            "sources": sources,
            "session_id": session_id,  # Return session ID for client to use in follow-ups
            "rephrased_question": rephrased_question,
        }

    except Exception as e:
        # Don't delete the temp dir on error if it's cached
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
    search_mode: str = "vector",  # Add search mode parameter
    files: List[UploadFile] = File(None),
):
    """Query uploaded documents with a question using either vector search or full text scan."""
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    # If it's a follow-up but no session ID provided, can't proceed
    if is_follow_up and not session_id:
        raise HTTPException(
            status_code=400, detail="Session ID required for follow-up questions"
        )

    # If not a follow-up, we need at least one file
    if not is_follow_up and (not files or len(files) == 0):
        raise HTTPException(
            status_code=400,
            detail="At least one file is required for initial questions",
        )

    # Validate search mode
    if search_mode not in ["vector", "full_text"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid search mode. Must be 'vector' or 'full_text'",
        )

    # Handle full text scan mode
    if search_mode == "full_text":
        # For follow-up questions, files will be None, so use cached data
        if is_follow_up and session_id:
            cached_data = session_cache.get(session_id)
            if not cached_data:
                raise HTTPException(
                    status_code=400,
                    detail="Session expired or not found. Please upload documents again."
                )
            # Use the cached files/session for full text processing
        elif not files or len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="For full-text scan, please upload at least one document.",
            )
        return await _handle_full_text_document_query(
            session,
            current_user,
            files,
            question,
            chat_history,
            use_default_models,
            session_id,
            is_follow_up,
        )

    # Continue with existing vector search implementation
    try:
        # Check if we have a cached retriever for this session
        retriever = None
        llm = None
        temp_paths = []

        # For follow-up questions, we MUST use cached resources
        if is_follow_up and session_id:
            print(f"🔍 Looking for cached resources for session: {session_id}")
            print(f"Cache contains {len(session_cache.cache)} sessions")
            print(f"Available session IDs: {list(session_cache.cache.keys())}")
            
            # Debug cache state
            cache_debug = session_cache.debug_info()
            print(f"Cache debug info: {cache_debug}")
            
            cached_data = session_cache.get(session_id)
            if not cached_data:
                print(f"❌ CACHE MISS: Session {session_id} not found in cache")
                print(f"Available sessions: {list(session_cache.cache.keys())}")
                
                # Instead of failing, gracefully degrade to treating this as a new request
                print("⚠️ Treating follow-up as new request due to cache miss")
                is_follow_up = False  # Treat as new request
                
                # Make sure we have files for the new request
                if not files or len(files) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail="Session expired and no files provided. Please upload documents again."
                    )
            else:
                print(f"✅ CACHE HIT: Using cached resources for document session {session_id}")
                retriever = cached_data.get("retriever")
                llm = cached_data.get("llm")
                
                # Validate that we actually got the cached resources
                if not retriever or not llm:
                    print(f"❌ INVALID CACHE: Session {session_id} exists but missing retriever/llm")
                    print(f"Cached data keys: {list(cached_data.keys()) if cached_data else 'None'}")
                    
                    # Gracefully degrade instead of failing
                    print("⚠️ Treating follow-up as new request due to incomplete cache")
                    is_follow_up = False
                    if not files or len(files) == 0:
                        raise HTTPException(
                            status_code=400,
                            detail="Session incomplete and no files provided. Please upload documents again."
                        )
                else:
                    print(f"✅ Successfully retrieved cached retriever and LLM for session {session_id}")

        # If this is NOT a follow-up, set up new resources
        elif not is_follow_up:
            print("Setting up new resources for document query")
            
            # Ensure we have files for new sessions
            if not files or len(files) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Files are required for new document queries"
                )
            # Get the user's default models
            user = session.get(User, current_user.id)
            if user and user.default_embedding_model:
                embedding_model = session.get(
                    EmbeddingModel, user.default_embedding_model
                )
                if not embedding_model:
                    raise HTTPException(
                        status_code=404,
                        detail="Default embedding model not found for user",
                    )
            else:
                # Fallback to system default (first system model)
                embedding_model = session.exec(
                    select(EmbeddingModel).where(EmbeddingModel.owner_id.is_(None))
                ).first()
                if not embedding_model:
                    raise HTTPException(
                        status_code=404, detail="No default embedding model found"
                    )

            if user and user.default_llm:
                llm_model = session.get(LlmModel, user.default_llm)
                if not llm_model:
                    raise HTTPException(
                        status_code=404, detail="Default LLM model not found for user"
                    )
            else:
                # Fallback to system default (first system model)
                llm_model = session.exec(
                    select(LlmModel).where(LlmModel.owner_id.is_(None))
                ).first()
                if not llm_model:
                    raise HTTPException(
                        status_code=404, detail="No default LLM model found"
                    )

            # Process all uploaded files and combine them into a single document collection
            all_documents = []

            for file in files:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(await file.read())
                    temp_path = temp_file.name
                    temp_paths.append(temp_path)
                # File is now closed and ready to be read by loaders

                # Detect file type and use appropriate loader
                if file.filename.endswith(".pdf"):
                    documents = load_pdf_with_pypdf(temp_path, file.filename)
                else:
                    # Default to text loader for other files
                    loader = TextLoader(temp_path)
                    documents = loader.load()

                # Add file source information to metadata
                for doc in documents:
                    if not hasattr(doc, "metadata") or doc.metadata is None:
                        doc.metadata = {}
                    doc.metadata["source_filename"] = file.filename

                all_documents.extend(documents)

            # Split all documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            chunks = text_splitter.split_documents(all_documents)

            # Create embeddings
            embeddings = load_embeddings_model(
                provider=embedding_model.provider, model_id=embedding_model.model_id
            )

            # Create vector store in a temp directory that persists for the session
            vector_dir = tempfile.mkdtemp()
            vector_store = Chroma.from_documents(
                documents=chunks, embedding=embeddings, persist_directory=vector_dir
            )
            # Create a hybrid retriever that combines vector-based and keyword-based retrieval
            retriever = create_ensemble_retriever(
                chroma_db=vector_store,
                vector_weight=0.7,  # Weight for vector-based retrieval
                keyword_weight=0.3,  # Weight for keyword-based retrieval
                search_kwargs={"k": 5},  # Search parameters
            )

            # Create LLM
            llm = create_llm(
                provider=llm_model.provider,
                model_id=llm_model.model_id,
                temperature=0.0,
            )

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
                    "temp_paths": temp_paths,
                },
            )
        
        # If we reach here without retriever/llm, something went wrong
        if not retriever or not llm:
            raise HTTPException(
                status_code=500,
                detail="Failed to set up or retrieve cached resources"
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
                "content": doc.page_content,  # Remove 300 character truncation
                "metadata": metadata,
            }
            sources.append(source)

        # Define prompt
        qa_prompt_template = settings.CHATBOT_KB_QA_PROMPT_TEMPLATE

        # Generate the answer - with branching for different model types
        try:
            print("Generating answer for document query...")
            answer_content = invoke_llm(
                llm,
                qa_prompt_template,
                {"context": context, "question": rephrased_question},
            )
            print(f"Got response: {answer_content[:100]}...")
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating answer: {str(e)}"
            )

        print("Response:", answer_content[:100])
        print("Sources:", len(sources))

        # After generating the answer and before returning:
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot",
            input_data={
                "question": question,
                "rephrased_question": rephrased_question,
                "documents": [file.filename for file in files] if files else [],
            },
            output_data=answer_content,
            metadata={
                "session_id": session_id,
                "is_follow_up": is_follow_up,
                "sources": [s["metadata"] for s in sources],
            },
        )

        return {
            "answer": answer_content,
            "sources": sources,
            "session_id": session_id,
            "rephrased_question": rephrased_question,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error querying document: {str(e)}"
        )

    finally:
        # Only clean up temp files if not cached
        if temp_paths and not is_follow_up and not session_cache.get(session_id):
            for temp_path in temp_paths:
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    print(f"Error removing temporary file {temp_path}: {e}")


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
        if not llm:
            print("Setting up new LLM for text query")
            # Get the default LLM model
            llm = get_default_llm(session, current_user)
            print("Default LLM model retrieved")
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

        # Define prompt template for general Q&A
        qa_prompt_template = settings.CHATBOT_GENERAL_QA_PROMPT_TEMPLATE

        # Handle different model types
        answer_content = ""

        # Generate the answer using invoke_llm
        try:
            print("Generating answer for text query...")
            answer_content = invoke_llm(
                llm, qa_prompt_template, {"question": rephrased_question}
            )
            print(f"Got response: {answer_content[:100]}...")
        except Exception as e:
            print(f"Error generating answer: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating answer: {str(e)}"
            )

        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot",
            input_data={"question": question, "rephrased_question": rephrased_question},
            output_data=answer_content,
            metadata={"session_id": session_id, "is_follow_up": is_follow_up},
        )

        return {
            "answer": answer_content,
            "session_id": session_id,
            "rephrased_question": rephrased_question,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error processing question: {str(e)}"
        )


@router.post("/", response_model=QueryResponse)
async def chat(
    session: SessionDep,
    current_user: CurrentUser,
    request: ChatRequest,
):
    """Main chat endpoint that routes to appropriate handlers based on context."""
    try:
        print(f"Received chat request: {request}")

        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        if request.knowledge_base_id:
            # Route to knowledge base query
            return await query_knowledge_base(
                session=session,
                current_user=current_user,
                kb_id=request.knowledge_base_id,
                question=request.prompt,
                chat_history=request.chat_history,
                session_id=session_id,
                is_follow_up=request.is_follow_up,
                search_mode=request.search_type,
            )
        else:
            # Route to text query (general chat without KB)
            response = await query_text(
                session=session,
                current_user=current_user,
                question=request.prompt,
                chat_history=request.chat_history,
                session_id=session_id,
                is_follow_up=request.is_follow_up,
            )

            # Convert TextQueryResponse to QueryResponse format
            return QueryResponse(
                answer=response.answer,
                sources=[],  # Text queries don't have sources
                session_id=response.session_id,
                rephrased_question=response.rephrased_question,
            )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")


# Add a cleanup task that runs periodically
@router.on_event("startup")
async def startup_event():
    async def cleanup_sessions():
        while True:
            await asyncio.sleep(1800)  # 30 minutes
            session_cache.cleanup()
            print("Session cache cleanup performed")

    asyncio.create_task(cleanup_sessions())
