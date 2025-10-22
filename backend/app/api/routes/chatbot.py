from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, List
from pydantic import BaseModel
import tempfile
import os
import uuid
import re
import json
import redis
from app.services.embeddings import load_embeddings_model
from app.services.llms import (
    create_llm,
    get_default_llm,
    invoke_llm,
    invoke_llm_async,
    record_llm_interaction,
)
from app.services.translation import translate_text_if_needed
from app.services.knowledgebases import get_embedding_model
from app.services.retrievers import (
    create_ensemble_retriever,
)
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    KnowledgeBase,
    EmbeddingModel,
    LlmModel,
    Source as SourceORM,
    SourceData,
    User,
)
from app.services.session_manager import session_manager
from app.core.config import settings
from app.services.pdf_utils import load_pdf_with_pypdf
from app.services.document_utils import (
    extract_documents_from_file_unified,
    extract_documents_and_images_from_file_unified,
    ensure_documents_for_vector_search,
)
from sqlmodel import select

# from langchain_community.document_loaders import PyPDFLoader  # Removed - using pypdf instead

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import tempfile
import os
import zipfile
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
# Session manager is imported from services


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

    # Get LLM
    llm = get_default_llm(session, current_user)

    # Check if LLM supports vision
    from app.services.vision_service import VisionService

    vision_enabled = VisionService.is_vision_enabled(llm)

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
    processed_sources = (
        []
    )  # Track sources that were successfully processed for potential vision analysis

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
            # Track this source as successfully processed
            processed_sources.append(source)
            # Chunk the text
            chunks = chunk_text(
                file_content, max_tokens=settings.FULL_SCAN_DOCUMENT_CHUNK_SIZE
            )
            print(f"Created {len(chunks)} chunks from {source.name}")

            # Analyze each chunk
            for i, chunk in enumerate(chunks):
                try:
                    print(f"Analyzing chunk {i+1}/{len(chunks)} from {source.name}")
                    # Add delay between chunks to prevent rate limit exhaustion
                    if i > 0 and settings.CHATBOT_ENABLE_CHUNK_DELAYS:
                        await asyncio.sleep(settings.PROCESSING_DELAY_BETWEEN_CHUNKS)

                    # Get user language and create language instruction (use preferred_language)
                    user_language = (
                        getattr(current_user, "preferred_language", None) or "en"
                    )
                    language_name = settings.SUPPORTED_LANGUAGES.get(
                        user_language, "English"
                    )
                    language_instruction = f"Respond in this language: {language_name}."
                    print(f"DEBUG: language_instruction = {language_instruction}")

                    chunk_analysis = invoke_llm(
                        llm,
                        settings.CHATBOT_FULL_TEXT_CHUNK_PROMPT_TEMPLATE,
                        {
                            "chunk": chunk,
                            "question": rephrased_question,
                            "language_instruction": language_instruction,
                        },
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
        # No relevant chunks found - still run synthesis template to get standardized insufficient context message
        chunk_analyses_text = "No relevant information found in any chunks."
        # Get user language and create language instruction (use preferred_language)
        user_language = getattr(current_user, "preferred_language", None) or "en"
        language_name = settings.SUPPORTED_LANGUAGES.get(user_language, "English")
        language_instruction = f"Respond in this language: {language_name}."

        print(f"DEBUG: language_instruction = {language_instruction}")

        final_answer = invoke_llm(
            llm,
            settings.CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE,
            {
                "question": rephrased_question,
                "chunk_analyses": chunk_analyses_text,
                "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                "language_instruction": language_instruction,
            },
        )
        sources = []
    else:
        # Synthesize all chunk analyses
        chunk_analyses_text = "\n\n".join(
            [
                f"Analysis {i+1}: {analysis}"
                for i, analysis in enumerate(all_chunk_analyses)
            ]
        )

        # Get user language and create language instruction (use preferred_language)
        user_language = getattr(current_user, "preferred_language", None) or "en"
        language_name = settings.SUPPORTED_LANGUAGES.get(user_language, "English")
        language_instruction = f"Respond in this language: {language_name}."

        print(f"DEBUG: language_instruction = {language_instruction}")

        final_answer = invoke_llm(
            llm,
            settings.CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE,
            {
                "question": rephrased_question,
                "chunk_analyses": chunk_analyses_text,
                "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                "language_instruction": language_instruction,
            },
        )

    # Check if the synthesized answer indicates information wasn't found (always check after synthesis)
    text_analysis_insufficient = settings.LLM_INSUFFICIENT_INFO_PHRASE in final_answer

    print(
        f"Full text synthesis - Text analysis insufficient: {text_analysis_insufficient}"
    )

    # Only perform vision analysis if (text analysis was insufficient OR no relevant chunks found) AND vision is available AND we have processed sources
    vision_analysis_performed = False
    should_attempt_vision = (
        (text_analysis_insufficient or not all_chunk_analyses)
        and vision_enabled
        and processed_sources
    )
    if should_attempt_vision:
        print(
            f"Text analysis insufficient or no relevant chunks found, attempting vision analysis from {len(processed_sources)} processed source files"
        )

        # Extract images from all processed source files
        all_images = []
        for source in processed_sources:
            try:
                source_data = session.get(SourceData, source.source_data_id)
                if source_data and source_data.data:
                    # Extract the raw file content from the ZIP first
                    try:
                        zip_data = BytesIO(source_data.data)
                        with zipfile.ZipFile(zip_data, "r") as zip_file:
                            # Get the first file in the archive (there should only be one)
                            file_info = zip_file.infolist()[0]
                            raw_file_content = zip_file.read(file_info.filename)
                            print(
                                f"Extracted {len(raw_file_content)} bytes from ZIP for source {source.source_data_id}"
                            )
                    except zipfile.BadZipFile:
                        # If it's not a ZIP file, use the data directly
                        print(
                            f"Source {source.source_data_id} is not a ZIP file, using data directly"
                        )
                        raw_file_content = source_data.data

                    # Extract images from the raw file content using the actual filename
                    from app.services.document_utils import (
                        extract_documents_and_images_from_file_unified,
                    )

                    _, images = extract_documents_and_images_from_file_unified(
                        raw_file_content,
                        source.name,  # Use actual filename with extension
                    )
                    all_images.extend(images)
                    print(
                        f"Extracted {len(images)} images from source {source.source_data_id} ({source.name})"
                    )
            except Exception as e:
                print(
                    f"Error extracting images from source {source.source_data_id}: {e}"
                )
                continue

        if all_images:
            print(f"Total images extracted: {len(all_images)}")
            try:
                # Get user language and create language instruction (use preferred_language)
                user_language = (
                    getattr(current_user, "preferred_language", None) or "en"
                )
                language_name = settings.SUPPORTED_LANGUAGES.get(
                    user_language, "English"
                )
                language_instruction = f"Respond in this language: {language_name}."

                print(f"DEBUG: language_instruction = {language_instruction}")

                # Convert base64 images to the format expected by VisionService
                vision_images = []
                for img_b64 in all_images:
                    vision_images.append(
                        {
                            "image_data": img_b64,
                            "metadata": {"source": "knowledge_base_sources"},
                        }
                    )

                vision_result = VisionService.safe_vision_analysis(
                    llm=llm,
                    prompt_template=settings.CHATBOT_VISION_PROMPT_TEMPLATE,
                    variables={
                        "image_count": len(all_images),
                        "source_files": "knowledge_base_sources",
                        "question": rephrased_question,
                        "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                        "language_instruction": language_instruction,
                    },
                    images=vision_images,
                )

                print("Vision analysis result:", vision_result[:200])

                if all_chunk_analyses:
                    # Combine text and vision analysis for full text scan
                    # Use the chunk analyses as the base context and enhance with vision
                    enhanced_chunk_analyses = (
                        chunk_analyses_text
                        + "\n\n"
                        + f"Additional Vision Analysis: {vision_result}"
                    )

                    # Regenerate the final answer with vision-enhanced analysis
                    final_answer = invoke_llm(
                        llm,
                        settings.CHATBOT_FULL_TEXT_SYNTHESIS_PROMPT_TEMPLATE,
                        {
                            "question": rephrased_question,
                            "chunk_analyses": enhanced_chunk_analyses,
                        },
                    )
                else:
                    # No text chunks found, vision analysis is the only source of information
                    # Extract the summary from the vision result JSON
                    try:
                        import json

                        vision_data = json.loads(vision_result)
                        if isinstance(vision_data, dict) and "summary" in vision_data:
                            final_answer = vision_data["summary"]
                        else:
                            final_answer = vision_result  # Fallback to raw result
                    except (json.JSONDecodeError, KeyError):
                        final_answer = vision_result  # Fallback to raw result

                vision_analysis_performed = True
                print(
                    f"Enhanced full text synthesis with vision analysis: {len(final_answer)} chars"
                )

            except Exception as vision_error:
                print(f"Vision analysis failed: {vision_error}")
                # Keep the original text-only answer
        else:
            print("No images found in processed source files")

        # Replace the internal insufficient info phrase with a user-friendly message
        if settings.LLM_INSUFFICIENT_INFO_PHRASE in final_answer:
            final_answer = "I'm sorry, but I couldn't find enough information in the knowledge base to answer your question. The knowledge base may not contain the specific details you're looking for, or the question might be about content not present in the stored documents."

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
                "vision_analysis_performed": vision_analysis_performed,
                "text_analysis_insufficient": text_analysis_insufficient,
                "no_relevant_chunks_found": len(all_chunk_analyses) == 0,
                "processed_sources_count": len(processed_sources),
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

    # Get LLM and check vision capabilities
    llm = get_default_llm(session, current_user)

    # Check if LLM supports vision
    from app.services.vision_service import VisionService

    vision_enabled = VisionService.is_vision_enabled(llm)

    # Rephrase the question using chat history if available
    if chat_history:
        rephrased_question = rephrase_question_with_context(llm, chat_history, question)
    else:
        rephrased_question = question

    # Translate the rephrased question for display purposes
    # translated_rephrased_question = await translate_text_if_needed(
    #     rephrased_question, session, current_user, llm
    # )
    translated_rephrased_question = rephrased_question

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

            # Extract text from file using unified document processing
            with open(temp_path, "rb") as f:
                file_content = f.read()

            # Use the unified document extraction function (uses settings.PDF_PARSING_MODE by default)
            documents = extract_documents_from_file_unified(file_content, file.filename)
            full_text = "\n\n".join([doc.page_content for doc in documents])

            # Extract images if vision is enabled
            file_images = []
            if vision_enabled:
                from app.services.document_utils import (
                    extract_documents_and_images_from_file_unified,
                )

                _, file_images = extract_documents_and_images_from_file_unified(
                    file_content, file.filename
                )
                print(f"Extracted {len(file_images)} images from {file.filename}")

            # Chunk the text
            chunks = chunk_text(
                full_text, max_tokens=settings.FULL_SCAN_DOCUMENT_CHUNK_SIZE
            )

            # Analyze each chunk for this file
            file_chunk_analyses = []
            file_source_citations = []

            for i, chunk in enumerate(chunks):
                # Add delay between chunks to prevent rate limit exhaustion
                if i > 0 and settings.CHATBOT_ENABLE_CHUNK_DELAYS:
                    import asyncio

                    await asyncio.sleep(settings.PROCESSING_DELAY_BETWEEN_CHUNKS)

                try:
                    # Get user language and create language instruction (use preferred_language)
                    user_language = (
                        getattr(current_user, "preferred_language", None) or "en"
                    )
                    language_name = settings.SUPPORTED_LANGUAGES.get(
                        user_language, "English"
                    )
                    language_instruction = f"Respond in this language: {language_name}."
                    print(f"DEBUG: language_instruction = {language_instruction}")

                    chunk_analysis = invoke_llm(
                        llm,
                        settings.CHATBOT_FULL_TEXT_CHUNK_PROMPT_TEMPLATE,
                        {
                            "chunk": chunk,
                            "question": rephrased_question,
                            "language_instruction": language_instruction,
                        },
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

            # Process analysis for this file (whether chunks were found or not)
            vision_analysis_performed = False
            text_analysis_insufficient = False
            document_analysis = ""

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
                        "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                        "language_instruction": language_instruction,
                    },
                )

                # Check if the text analysis indicates information wasn't found
                text_analysis_insufficient = (
                    settings.LLM_INSUFFICIENT_INFO_PHRASE in document_analysis
                )

                print(
                    f"Full text scan - Text analysis insufficient: {text_analysis_insufficient}"
                )
            else:
                # No relevant chunks found - treat as insufficient text analysis
                document_analysis = "No relevant information found in this document."
                text_analysis_insufficient = True
                print(
                    "No relevant chunks found - will attempt vision analysis if available"
                )

            # Perform vision analysis if text analysis was insufficient OR no chunks were found
            if text_analysis_insufficient and vision_enabled and file_images:
                print(
                    f"Text analysis insufficient or no chunks found, performing vision analysis for {file.filename}"
                )

                # Prepare images for processing
                image_data_list = []
                for idx, img_b64 in enumerate(file_images):
                    image_data_list.append(
                        {
                            "image_data": img_b64,
                            "source_file": file.filename,
                            "image_index": idx,
                            "metadata": {"extracted_from": file.filename},
                        }
                    )

                try:
                    vision_analysis = await VisionService.process_images_with_prompt(
                        llm=llm,
                        images=image_data_list,
                        prompt_template=settings.CHATBOT_VISION_PROMPT_TEMPLATE,
                        variables={
                            "question": rephrased_question,
                            "context": chat_history or "",
                            "image_count": len(image_data_list),
                            "source_files": file.filename,
                            "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                        },
                    )

                    # Translate vision analysis if needed
                    # vision_analysis = await translate_text_if_needed(
                    #     vision_analysis, session, current_user, llm
                    # )

                    # When text analysis was insufficient, use vision analysis directly
                    # instead of combining with formatted markers
                    if (
                        text_analysis_insufficient
                        and not settings.LLM_INSUFFICIENT_INFO_PHRASE in vision_analysis
                    ):
                        # Vision analysis provided an answer, use it directly
                        final_document_analysis = vision_analysis
                    else:
                        # Either text analysis was sufficient, or vision also insufficient
                        # Combine them for completeness
                        final_document_analysis = (
                            VisionService.combine_text_and_vision_analysis(
                                document_analysis, vision_analysis, "integrated"
                            )
                        )

                    # Store the final analysis for this document
                    all_document_analyses.append(
                        {
                            "filename": file.filename,
                            "analysis": final_document_analysis,
                            "has_vision_analysis": True,
                            "image_count": len(file_images),
                            "vision_analysis_performed": True,
                        }
                    )
                    vision_analysis_performed = True

                except Exception as vision_error:
                    print(f"Vision analysis error for {file.filename}: {vision_error}")
                    # Fall back to text-only analysis
                    all_document_analyses.append(
                        {
                            "filename": file.filename,
                            "analysis": document_analysis,
                            "vision_error": str(vision_error),
                        }
                    )
            else:
                # No vision analysis needed or available
                if text_analysis_insufficient and not vision_enabled:
                    print(
                        "Text analysis insufficient but vision not available, using text-only"
                    )
                elif text_analysis_insufficient and not file_images:
                    print(
                        "Text analysis insufficient but no images found, using text-only"
                    )
                elif not text_analysis_insufficient:
                    print(
                        "Text analysis appears sufficient, skipping vision analysis to save costs"
                    )
                else:
                    print("Vision analysis not needed for this document")

                # Store the text-only analysis for this document
                all_document_analyses.append(
                    {
                        "filename": file.filename,
                        "analysis": document_analysis,
                        "vision_analysis_performed": False,
                    }
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
            # Get user language and create language instruction (use preferred_language)
            user_language = getattr(current_user, "preferred_language", None) or "en"
            language_name = settings.SUPPORTED_LANGUAGES.get(user_language, "English")
            language_instruction = f"Respond in this language: {language_name}."

            print(f"DEBUG: language_instruction = {language_instruction}")

            final_answer = invoke_llm(
                llm,
                settings.CHATBOT_MULTI_DOCUMENT_SYNTHESIS_PROMPT_TEMPLATE,
                {
                    "question": rephrased_question,
                    "document_analyses": document_analyses_text,
                    "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                    "language_instruction": language_instruction,
                },
            )
            sources = all_source_citations

        # Translate the final answer if needed
        # final_answer = await translate_text_if_needed(
        #     final_answer, session, current_user, llm
        # )

        # Replace the internal insufficient info phrase with a user-friendly message
        if settings.LLM_INSUFFICIENT_INFO_PHRASE in final_answer:
            final_answer = "I'm sorry, but I couldn't find enough information in the provided documents to answer your question. The documents may not contain the specific details you're looking for, or the question might be about content not present in the uploaded files."

        # Record the interaction
        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot_full_text",
            input_data={
                "question": question,
                "rephrased_question": rephrased_question,
                "documents": [file.filename for file in files] if files else [],
                "search_mode": "full_text",
            },
            output_data=final_answer,
            metadata={
                "session_id": session_id,
                "is_follow_up": is_follow_up,
                "document_count": len(files) if files else 0,
                "relevant_documents": len(all_document_analyses),
            },
        )

        return {
            "answer": final_answer,
            "sources": sources,
            "session_id": session_id,
            "rephrased_question": translated_rephrased_question,
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
        cached_data = session_manager.get_session(session_id)
        print(
            f"Session cache lookup - ID: {session_id}, Found: {cached_data is not None}"
        )

        if cached_data:
            print(f"Cache contents for {session_id}: {list(cached_data.keys())}")

        retriever = None
        llm = None

        print("Session ID:", session_id)
        print("Is follow-up:", is_follow_up)
        print("Cached data:", cached_data is not None)
        print("Cached KB ID:", cached_data.get("kb_id") if cached_data else None)
        print("KB ID:", kb_id)

        if is_follow_up and cached_data and cached_data.get("kb_id") == kb_id:
            print(f"Using cached resources for session {session_id}")

            # Try to get objects from cache
            retriever = cached_data.get("retriever")
            llm = cached_data.get("llm")

            # Check if objects need rebuilding and rebuild them gracefully
            if session_manager.session_needs_rebuild(
                cached_data, "retriever"
            ) or session_manager.session_needs_rebuild(cached_data, "llm"):
                print("Session objects need rebuilding - rebuilding from metadata")

                # Get cached metadata
                temp_dir = cached_data.get("temp_dir")

                if not temp_dir:
                    print("No temp_dir in cache - session expired")
                    raise HTTPException(
                        status_code=400,
                        detail="Session expired. Please upload your documents again.",
                    )

                try:
                    # Rebuild retriever if needed
                    if session_manager.session_needs_rebuild(cached_data, "retriever"):
                        print("Rebuilding retriever from vector database")

                        # Get KB and embedding model
                        kb = session.get(KnowledgeBase, kb_id)
                        if not kb:
                            raise HTTPException(
                                status_code=404, detail="Knowledge base not found"
                            )

                        # Get embedding model
                        if kb.embedding_model_id:
                            embedding_model = session.get(
                                EmbeddingModel, kb.embedding_model_id
                            )
                        else:
                            user = session.get(User, current_user.id)
                            if user and user.default_embedding_model:
                                embedding_model = session.get(
                                    EmbeddingModel, user.default_embedding_model
                                )
                            else:
                                embedding_model = session.exec(
                                    select(EmbeddingModel).where(
                                        EmbeddingModel.owner_id.is_(None)
                                    )
                                ).first()

                        if not embedding_model:
                            raise HTTPException(
                                status_code=404, detail="No embedding model found"
                            )

                        # Rebuild embeddings and vector store
                        embeddings = load_embeddings_model(
                            provider=embedding_model.provider,
                            model_id=embedding_model.model_id,
                        )

                        # Reconnect to existing vector database
                        chroma_db = Chroma(
                            persist_directory=temp_dir, embedding_function=embeddings
                        )

                        # Rebuild basic retriever without enhanced filtering
                        retriever = chroma_db.as_retriever(
                            search_kwargs={"k": settings.RAG_NUM_CHUNKS}
                        )
                        print("Successfully rebuilt retriever")

                    # Rebuild LLM if needed
                    if session_manager.session_needs_rebuild(cached_data, "llm"):
                        print("Rebuilding LLM")

                        # Get KB and LLM model
                        kb = session.get(KnowledgeBase, kb_id)
                        if use_default_models:
                            llm = get_default_llm(session, current_user)
                        else:
                            llm_model = session.get(LlmModel, kb.llm_model_id)
                            if llm_model:
                                llm = create_llm(
                                    llm_model.provider,
                                    llm_model.model_id,
                                    temperature=0.0,
                                )
                            else:
                                llm = get_default_llm(session, current_user)
                        print("Successfully rebuilt LLM")

                    # Update session cache with rebuilt objects
                    updated_session_data = cached_data.copy()
                    updated_session_data["retriever"] = retriever
                    updated_session_data["llm"] = llm
                    session_manager.set_session(session_id, updated_session_data)
                    print("Updated session cache with rebuilt objects")

                except Exception as e:
                    print(f"Failed to rebuild session objects: {e}")
                    raise HTTPException(
                        status_code=400,
                        detail="Session expired. Please upload your documents again.",
                    )

        # If no cached retriever, we need to set everything up
        if not retriever:
            print("Setting up new resources for knowledge base query")
            # 1. Retrieve knowledge base from database
            kb = session.get(KnowledgeBase, kb_id)
            if not kb:
                raise HTTPException(status_code=404, detail="Knowledge base not found")

            # 2. Create a temporary directory for ChromaDB
            temp_dir = tempfile.mkdtemp()

            # Extract the zipped ChromaDB into the temp directory
            if kb.storage_type == "file" and kb.file_path:
                # Handle file-based storage
                if not os.path.exists(kb.file_path):
                    raise HTTPException(
                        status_code=400, detail="Knowledge base file not found on disk"
                    )
                with zipfile.ZipFile(kb.file_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
            elif kb.data:
                # Handle database storage
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

            # Create a basic retriever without enhanced filtering to avoid async issues
            retriever = chroma_db.as_retriever(
                search_kwargs={"k": settings.RAG_NUM_CHUNKS}
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
            session_manager.set_session(
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

        # LLM-based relevance filtering for vector search (optional, controlled by config)
        if settings.RAG_ENABLE_LLM_RELEVANCE_FILTER and docs:
            print(
                f"🔍 LLM filtering enabled - analyzing {len(docs)} retrieved chunks for relevance to question..."
            )

            filtered_docs = []
            for i, doc in enumerate(docs):
                print(f"Analyzing chunk {i+1}/{len(docs)} for relevance...")

                relevance_check = invoke_llm(
                    llm,
                    settings.VERADOC_RELEVANCE_FILTER_PROMPT_TEMPLATE,
                    {
                        "chunk": doc.page_content or "",
                        "question": rephrased_question,
                    },
                )

                if "No relevant information found" not in relevance_check:
                    print(f"✅ Chunk {i+1} is relevant")
                    filtered_docs.append(doc)
                else:
                    print(
                        f"❌ Chunk {i+1} is not relevant - excluding from context and citations"
                    )

            print(
                f"📊 Relevance filtering: {len(filtered_docs)}/{len(docs)} chunks are relevant"
            )
            docs = filtered_docs

        context = "\n\n".join([doc.page_content for doc in docs])
        print("Retrieved context:", context)

        # Extract unique source_data_ids from retrieved documents for potential image extraction
        # This must happen BEFORE vision analysis but we need to look up source_data_ids by filename
        relevant_sources = {}  # source_data_id -> filename mapping
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
                    truncated_filename = match.group(1)
                else:
                    # Fallback to the original filename if no underscore found
                    truncated_filename = raw_filename

                # Debug info
                print(f"Looking up source with filename: {truncated_filename}")

                # Try to find the source by truncated name first
                source_entry = session.exec(
                    select(SourceORM).where(SourceORM.name == truncated_filename)
                ).first()

                # 🚨 NEW FALLBACK: If not found with truncated name, try the whole filename
                if not source_entry:
                    source_entry = session.exec(
                        select(SourceORM).where(SourceORM.name == raw_filename)
                    ).first()

                if source_entry:
                    source_data_id = str(source_entry.source_data_id)
                    relevant_sources[source_data_id] = (
                        source_entry.name
                    )  # Store filename with source_id
                    # Also update the doc metadata for later use
                    doc.metadata["source_data_id"] = source_data_id
                    print(
                        f"Found source entry with ID: {source_data_id}, filename: {source_entry.name}"
                    )

        print(
            f"Found {len(relevant_sources)} relevant source files for potential vision analysis"
        )

        # Create a list of sources for citation (now with source_data_id already in metadata)
        sources = []
        for doc in docs:
            source = {
                "content": doc.page_content,  # Remove 300 character truncation
                "metadata": doc.metadata,
            }
            sources.append(source)

        # 6. Define prompt for question answering
        qa_prompt_template = settings.CHATBOT_KB_QA_PROMPT_TEMPLATE

        # Check if LLM supports vision for potential vision analysis
        from app.services.vision_service import VisionService

        vision_enabled = VisionService.is_vision_enabled(llm)

        # 7. Generate the answer - with potential vision analysis
        try:
            print("Generating initial answer for knowledge base query...")
            # Get user language and create language instruction (use preferred_language)
            user_language = getattr(current_user, "preferred_language", None) or "en"
            language_name = settings.SUPPORTED_LANGUAGES.get(user_language, "English")
            language_instruction = f"Respond in this language: {language_name}."

            print(f"DEBUG: language_instruction = {language_instruction}")

            answer_content = invoke_llm(
                llm,
                qa_prompt_template,
                {
                    "context": context,
                    "question": rephrased_question,
                    "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                    "language_instruction": language_instruction,
                },
            )
            print(f"Initial text-only response: {answer_content[:100]}...")

            # Check if the text answer indicates information wasn't found
            text_answer_insufficient = (
                settings.LLM_INSUFFICIENT_INFO_PHRASE in answer_content
            )

            print(f"Text answer insufficient: {text_answer_insufficient}")

            # Only perform vision analysis if text answer was insufficient AND vision is available AND we have relevant sources
            vision_analysis_performed = False
            if text_answer_insufficient and vision_enabled and relevant_sources:
                print(
                    f"Text analysis insufficient, attempting vision analysis from {len(relevant_sources)} source files"
                )

                # Extract images from relevant source files
                all_images = []
                for source_id, filename in relevant_sources.items():
                    try:
                        source_data = session.get(SourceData, source_id)
                        if source_data and source_data.data:
                            # Extract the raw file content from the ZIP first
                            try:
                                zip_data = BytesIO(source_data.data)
                                with zipfile.ZipFile(zip_data, "r") as zip_file:
                                    # Get the first file in the archive (there should only be one)
                                    file_info = zip_file.infolist()[0]
                                    raw_file_content = zip_file.read(file_info.filename)
                                    print(
                                        f"Extracted {len(raw_file_content)} bytes from ZIP for source {source_id}"
                                    )
                            except zipfile.BadZipFile:
                                # If it's not a ZIP file, use the data directly
                                print(
                                    f"Source {source_id} is not a ZIP file, using data directly"
                                )
                                raw_file_content = source_data.data

                            # Extract images from the raw file content using the actual filename
                            from app.services.document_utils import (
                                extract_documents_and_images_from_file_unified,
                            )

                            _, images = extract_documents_and_images_from_file_unified(
                                raw_file_content,
                                filename,  # Use actual filename with extension
                            )
                            all_images.extend(images)
                            print(
                                f"Extracted {len(images)} images from source {source_id} ({filename})"
                            )
                    except Exception as e:
                        print(f"Error extracting images from source {source_id}: {e}")
                        continue

                if all_images:
                    print(f"Total images extracted: {len(all_images)}")
                    try:
                        # Convert base64 images to the format expected by VisionService
                        vision_images = []
                        for img_b64 in all_images:
                            vision_images.append(
                                {
                                    "image_data": img_b64,
                                    "metadata": {"source": "knowledge_base_sources"},
                                }
                            )

                        vision_result = VisionService.safe_vision_analysis(
                            llm=llm,
                            prompt_template=settings.CHATBOT_VISION_PROMPT_TEMPLATE,
                            variables={
                                "image_count": len(all_images),
                                "source_files": "knowledge_base_sources",
                                "question": rephrased_question,
                                "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                                "language_instruction": language_instruction,
                            },
                            images=vision_images,
                        )

                        print("Vision analysis result:", vision_result[:200])

                        # Use combined analysis for knowledge base with vision content
                        final_context = VisionService.combine_text_and_vision_analysis(
                            text_analysis=context,
                            vision_analysis=vision_result,
                            combination_strategy="comprehensive",
                        )
                        context = final_context
                        vision_analysis_performed = True
                        print(
                            f"Enhanced context with vision analysis: {len(context)} chars"
                        )

                        # Regenerate answer with vision-enhanced context
                        answer_content = invoke_llm(
                            llm,
                            qa_prompt_template,
                            {
                                "context": context,
                                "question": rephrased_question,
                                "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                            },
                        )
                        print(
                            f"Got vision-enhanced response: {answer_content[:100]}..."
                        )

                    except Exception as vision_error:
                        print(f"Vision analysis failed: {vision_error}")
                        # Keep the original text-only answer
                else:
                    print("No images found in relevant source files")
            elif not text_answer_insufficient:
                print(
                    "Text analysis appears sufficient, skipping vision analysis to save costs"
                )
            else:
                print(
                    "Vision analysis not available or no relevant sources found, using text-only answer"
                )

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
                "vision_analysis_performed": vision_analysis_performed,
                "text_answer_insufficient": text_answer_insufficient,
            },
        )

        # Replace the internal insufficient info phrase with a user-friendly message
        if settings.LLM_INSUFFICIENT_INFO_PHRASE in answer_content:
            answer_content = "I'm sorry, but I couldn't find enough information in the knowledge base to answer your question. The knowledge base may not contain the specific details you're looking for, or the question might be about content not present in the stored documents."

        return {
            "answer": answer_content,
            "sources": sources,
            "session_id": session_id,  # Return session ID for client to use in follow-ups
            "rephrased_question": rephrased_question,
        }

    except Exception as e:
        # Don't delete the temp dir on error if it's cached
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
        if not files or len(files) == 0:
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
        all_images = []  # Initialize here for both new and follow-up requests

        if is_follow_up and session_id:
            print("Using cached resources for follow-up question")
            cached_data = session_manager.get_session(session_id)
            if cached_data:
                print(f"Found session data for {session_id}")

                # Try to use existing objects first
                retriever = cached_data.get("retriever")
                llm = cached_data.get("llm")

                # Check if objects need rebuilding (after Redis deserialization)
                retriever_needs_rebuild = session_manager.session_needs_rebuild(
                    cached_data, "retriever"
                )
                llm_needs_rebuild = session_manager.session_needs_rebuild(
                    cached_data, "llm"
                )

                if retriever_needs_rebuild or llm_needs_rebuild:
                    print(
                        "Session objects need rebuilding - rebuilding from cached metadata"
                    )

                    # We have session metadata, so we can rebuild the objects
                    vector_dir = cached_data.get("vector_dir")
                    file_names = cached_data.get("file_names", [])

                    if not vector_dir or not file_names:
                        print("Session metadata incomplete - cannot rebuild")
                        raise HTTPException(
                            status_code=400,
                            detail="Session expired. Please upload your documents again.",
                        )

                    print(
                        f"Rebuilding session from vector_dir: {vector_dir}, files: {file_names}"
                    )

                    # Rebuild the retriever if needed
                    if retriever_needs_rebuild:
                        print("Rebuilding retriever from vector database")
                        try:
                            # Get user's default embedding model for rebuilding
                            user = session.get(User, current_user.id)
                            if user and user.default_embedding_model:
                                embedding_model = session.get(
                                    EmbeddingModel, user.default_embedding_model
                                )
                            else:
                                embedding_model = session.exec(
                                    select(EmbeddingModel).where(
                                        EmbeddingModel.owner_id.is_(None)
                                    )
                                ).first()

                            if not embedding_model:
                                raise HTTPException(
                                    status_code=404, detail="No embedding model found"
                                )

                            # Rebuild embeddings and vector store
                            embeddings = load_embeddings_model(
                                provider=embedding_model.provider,
                                model_id=embedding_model.model_id,
                            )

                            # Reconnect to existing vector database
                            vector_store = Chroma(
                                persist_directory=vector_dir,
                                embedding_function=embeddings,
                            )

                            # Rebuild basic retriever without enhanced filtering
                            retriever = vector_store.as_retriever(
                                search_kwargs={"k": settings.RAG_NUM_CHUNKS}
                            )
                            print("Successfully rebuilt retriever")

                        except Exception as e:
                            print(f"Failed to rebuild retriever: {e}")
                            raise HTTPException(
                                status_code=400,
                                detail="Session expired. Please upload your documents again.",
                            )

                    # Rebuild the LLM if needed
                    if llm_needs_rebuild:
                        print("Rebuilding LLM")
                        try:
                            # Get user's default LLM model
                            user = session.get(User, current_user.id)
                            if user and user.default_llm:
                                llm_model = session.get(LlmModel, user.default_llm)
                            else:
                                llm_model = session.exec(
                                    select(LlmModel).where(LlmModel.owner_id.is_(None))
                                ).first()

                            if not llm_model:
                                raise HTTPException(
                                    status_code=404, detail="No LLM model found"
                                )

                            # Rebuild LLM
                            llm = create_llm(
                                provider=llm_model.provider,
                                model_id=llm_model.model_id,
                                temperature=0.0,
                            )
                            print("Successfully rebuilt LLM")

                        except Exception as e:
                            print(f"Failed to rebuild LLM: {e}")
                            raise HTTPException(
                                status_code=400,
                                detail="Session expired. Please upload your documents again.",
                            )

                    # Update the session cache with rebuilt objects
                    updated_session_data = cached_data.copy()
                    updated_session_data["retriever"] = retriever
                    updated_session_data["llm"] = llm
                    session_manager.set_session(session_id, updated_session_data)
                    print("Updated session cache with rebuilt objects")

                # Verify we have working objects
                if not retriever or not llm:
                    print("Session missing required objects after rebuild attempt")
                    raise HTTPException(
                        status_code=400,
                        detail="Session incomplete. Please upload your documents again.",
                    )

                print("Successfully restored session objects")
            else:
                # Session not found in Redis
                raise HTTPException(
                    status_code=400,
                    detail="Session not found. Please upload your documents again.",
                )

        # If no cached retriever or this is a new document, set up everything
        if not retriever:
            print("Setting up new resources for document query")
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
            all_images = []

            for file in files:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(await file.read())
                    temp_path = temp_file.name
                    temp_paths.append(temp_path)
                # File is now closed and ready to be read by loaders

                # Use enhanced unified document processing for both text and images
                with open(temp_path, "rb") as f:
                    file_content = f.read()

                documents, images = extract_documents_and_images_from_file_unified(
                    file_content, file.filename
                )

                # Add file source information to metadata
                for doc in documents:
                    if not hasattr(doc, "metadata") or doc.metadata is None:
                        doc.metadata = {}
                    doc.metadata["source_filename"] = file.filename

                all_documents.extend(documents)
                all_images.extend(images)

            # Ensure we have documents for vector search (create fallbacks if needed)
            resilient_documents = ensure_documents_for_vector_search(
                all_documents, all_images, "uploaded_files"
            )

            # Split all documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            chunks = text_splitter.split_documents(resilient_documents)

            # Create embeddings
            embeddings = load_embeddings_model(
                provider=embedding_model.provider, model_id=embedding_model.model_id
            )

            # Create vector store in a temp directory that persists for the session
            vector_dir = tempfile.mkdtemp()
            vector_store = Chroma.from_documents(
                documents=chunks, embedding=embeddings, persist_directory=vector_dir
            )
            # Create a basic retriever without enhanced filtering to avoid async issues
            retriever = vector_store.as_retriever(
                search_kwargs={"k": settings.RAG_NUM_CHUNKS}
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
            session_manager.set_session(
                session_id,
                {
                    "retriever": retriever,
                    "llm": llm,
                    "vector_dir": vector_dir,
                    "temp_paths": temp_paths,
                    "file_names": [file.filename for file in files],  # Cache file names
                    "images": all_images,  # Cache extracted images for follow-up vision analysis
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

        # Translate the rephrased question if needed for display purposes
        # try:
        #     translated_rephrased_question = await translate_text_if_needed(
        #         rephrased_question, session, current_user, llm
        #     )
        # except Exception as e:
        #     print(f"Translation of rephrased question failed: {e}")
        #     translated_rephrased_question = rephrased_question  # Fallback to original
        translated_rephrased_question = rephrased_question

        # Retrieve relevant context
        docs = retriever.get_relevant_documents(rephrased_question)

        # LLM-based relevance filtering for vector search
        if docs:
            print(
                f"🔍 LLM filtering enabled - analyzing {len(docs)} retrieved chunks for relevance to question..."
            )

            filtered_docs = []
            for i, doc in enumerate(docs):
                print(f"Analyzing chunk {i+1}/{len(docs)} for relevance...")

                relevance_check = invoke_llm(
                    llm,
                    settings.VERADOC_RELEVANCE_FILTER_PROMPT_TEMPLATE,
                    {
                        "chunk": doc.page_content or "",
                        "question": rephrased_question,
                    },
                )

                if "No relevant information found" not in relevance_check:
                    print(f"✅ Chunk {i+1} is relevant")
                    filtered_docs.append(doc)
                else:
                    print(
                        f"❌ Chunk {i+1} is not relevant - excluding from context and citations"
                    )

            print(
                f"📊 Relevance filtering: {len(filtered_docs)}/{len(docs)} chunks are relevant"
            )
            docs = filtered_docs

        context = "\n\n".join([doc.page_content for doc in docs])

        # For follow-up questions, restore images from cached session data
        if is_follow_up and not all_images:
            print(
                f"DEBUG: Follow-up question detected, all_images is empty (length: {len(all_images)}), checking cached images"
            )
            cached_data = session_manager.get_session(session_id)
            print(f"DEBUG: Cached data retrieved: {bool(cached_data)}")
            if cached_data:
                cached_images = cached_data.get("images", [])
                if cached_images:
                    print(f"DEBUG: Found {len(cached_images)} cached images in session")
                    all_images.extend(cached_images)
                else:
                    print(
                        "DEBUG: No cached images found, attempting to re-extract from temp files"
                    )
                    # Fallback: try to re-extract from temp files if images weren't cached
                    temp_paths = cached_data.get("temp_paths", [])
                    print(f"DEBUG: Temp paths in cache: {temp_paths}")
                    if temp_paths:
                        print(
                            "Re-extracting images from cached temp files for follow-up question"
                        )
                        for temp_path in temp_paths:
                            print(f"DEBUG: Checking if temp file exists: {temp_path}")
                            if os.path.exists(temp_path):
                                try:
                                    print(f"DEBUG: Reading temp file: {temp_path}")
                                    with open(temp_path, "rb") as f:
                                        file_content = f.read()
                                    print(
                                        f"DEBUG: File content length: {len(file_content)}"
                                    )
                                    _, images = (
                                        extract_documents_and_images_from_file_unified(
                                            file_content, os.path.basename(temp_path)
                                        )
                                    )
                                    print(
                                        f"DEBUG: Extracted {len(images)} images from {temp_path}"
                                    )
                                    all_images.extend(images)
                                except Exception as e:
                                    print(
                                        f"Error re-extracting images from {temp_path}: {e}"
                                    )
                                    import traceback

                                    traceback.print_exc()
                            else:
                                print(f"DEBUG: Temp file does not exist: {temp_path}")
                    else:
                        print("DEBUG: No temp_paths found in cached data")
            else:
                print("DEBUG: No cached data found for session")
            print(f"Restored {len(all_images)} images for follow-up question")

        # Decide whether to attempt vision analysis
        from app.services.vision_service import VisionService

        vision_enabled = VisionService.is_vision_enabled(llm)

        # Check if any of the retrieved docs are vision fallbacks
        has_vision_fallbacks = any(
            doc.metadata.get("is_vision_fallback", False) for doc in docs
        )

        # Debug: surface the decision variables so logs show why vision may be skipped
        print(
            f"DEBUG: vision_enabled={vision_enabled}, has_vision_fallbacks={has_vision_fallbacks}, all_images_count={len(all_images)}"
        )

        # FIRST: Try to answer based on text analysis only
        text_only_context = context  # Keep original text context
        vision_analysis_performed = False

        # Get user language and create language instruction (use preferred_language)
        user_language = getattr(current_user, "preferred_language", None) or "en"
        language_name = settings.SUPPORTED_LANGUAGES.get(user_language, "English")
        language_instruction = f"Respond in this language: {language_name}."

        print(f"DEBUG: language_instruction = {language_instruction}")

        # Generate initial answer with text-only context
        print("Generating initial answer with text-only context...")
        initial_answer = invoke_llm(
            llm,
            settings.CHATBOT_KB_QA_PROMPT_TEMPLATE,
            {
                "context": text_only_context,
                "question": rephrased_question,
                "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                "language_instruction": language_instruction,
            },
        )
        print(f"Initial text-only answer: {initial_answer[:200]}...")

        # Check if the text-only answer indicates information wasn't found
        text_answer_insufficient = (
            settings.LLM_INSUFFICIENT_INFO_PHRASE in initial_answer
        )

        print(f"Text answer insufficient: {text_answer_insufficient}")

        # SECOND: Only run vision analysis if text answer seems insufficient AND vision is available
        if text_answer_insufficient and vision_enabled and all_images:
            print(
                f"Text analysis insufficient, attempting vision analysis for {len(all_images)} images"
            )
            try:
                # Convert base64 images to the format expected by VisionService
                vision_images = []
                for img_b64 in all_images:
                    vision_images.append(
                        {
                            "image_data": img_b64,
                            "metadata": {"source": "uploaded_files"},
                        }
                    )

                vision_result = VisionService.safe_vision_analysis(
                    llm=llm,
                    prompt_template=settings.CHATBOT_VISION_PROMPT_TEMPLATE,
                    variables={
                        "image_count": len(all_images),
                        "source_files": "uploaded_files",
                        "question": rephrased_question,
                        "context": text_only_context,
                        "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                        "language_instruction": language_instruction,
                    },
                    images=vision_images,
                )

                print("Vision analysis result:", vision_result[:200])

                # Use combined analysis for documents with vision content
                final_context = VisionService.combine_text_and_vision_analysis(
                    text_analysis=text_only_context,
                    vision_analysis=vision_result,
                    combination_strategy="comprehensive",
                )
                context = final_context
                vision_analysis_performed = True
                print(f"Enhanced context with vision analysis: {len(context)} chars")
                print(f"Enhanced context: {context}")

            except Exception as e:
                print(f"Vision analysis failed, using text-only: {e}")
        elif not text_answer_insufficient:
            print(
                "Text analysis appears sufficient, skipping vision analysis to save costs"
            )
        else:
            print(
                "Vision analysis not available or no images found, using text-only answer"
            )

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

        # Generate the final answer - use vision-enhanced context if available, otherwise use initial text answer
        try:
            print("Generating final answer for document query...")
            if vision_analysis_performed:
                # Regenerate answer with vision-enhanced context
                answer_content = invoke_llm(
                    llm,
                    settings.CHATBOT_KB_QA_PROMPT_TEMPLATE,
                    {
                        "context": context,
                        "question": rephrased_question,
                        "insufficient_info_phrase": settings.LLM_INSUFFICIENT_INFO_PHRASE,
                        "language_instruction": language_instruction,
                    },
                )
                print(f"Got vision-enhanced response: {answer_content[:100]}...")
            else:
                # Use the initial text-only answer
                answer_content = initial_answer
                print(f"Using text-only response: {answer_content[:100]}...")

            # Translate the answer if needed
            # try:
            #     answer_content = await translate_text_if_needed(
            #         answer_content, session, current_user, llm
            #     )
            # except Exception as e:
            #     print(f"Translation of answer failed: {e}")
            #     # Keep original answer if translation fails

        except Exception as e:
            print(f"Error generating answer: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating answer: {str(e)}"
            )

        print("Response:", answer_content[:100])
        print("Sources:", len(sources))

        # Get file names for logging
        if files:
            document_names = [file.filename for file in files]
        else:
            # For follow-up questions, get from cache
            cached_data = session_manager.get_session(session_id)
            document_names = cached_data.get("file_names", []) if cached_data else []

        # After generating the answer and before returning:
        # Ensure sources metadata is serializable
        serializable_sources = []
        for s in sources:
            try:
                # Try to serialize the metadata to ensure it's valid
                json.dumps(s["metadata"])
                serializable_sources.append(s["metadata"])
            except (TypeError, ValueError) as e:
                print(f"WARNING: Source metadata not serializable, skipping: {e}")
                # Create a serializable version
                serializable_metadata = {}
                for key, value in s["metadata"].items():
                    try:
                        json.dumps(value)
                        serializable_metadata[key] = value
                    except (TypeError, ValueError):
                        serializable_metadata[key] = str(value)
                serializable_sources.append(serializable_metadata)

        record_llm_interaction(
            session=session,
            user_id=current_user.id,
            functionality="chatbot",
            input_data={
                "question": question,
                "rephrased_question": rephrased_question,
                "documents": document_names,  # Use the variable instead of direct access
            },
            output_data=answer_content,
            metadata={
                "session_id": session_id,
                "is_follow_up": is_follow_up,
                "sources": serializable_sources,
                "vision_analysis_performed": vision_analysis_performed,
                "text_answer_insufficient": text_answer_insufficient,
            },
        )

        # Replace the internal insufficient info phrase with a user-friendly message
        if settings.LLM_INSUFFICIENT_INFO_PHRASE in answer_content:
            answer_content = "I'm sorry, but I couldn't find enough information in the provided documents to answer your question. The documents may not contain the specific details you're looking for, or the question might be about content not present in the uploaded files."

        return {
            "answer": answer_content,
            "sources": sources,
            "session_id": session_id,
            "rephrased_question": translated_rephrased_question,
        }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Error querying document: {str(e)}"
        )

    finally:
        # Only clean up temp files if not cached
        if (
            temp_paths
            and not is_follow_up
            and not session_manager.get_session(session_id)
        ):
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
        cached_data = session_manager.get_session(session_id)
        llm = None

        if is_follow_up and cached_data:
            print(f"Using cached LLM for session {session_id}")
            # Check if LLM needs rebuilding
            if not session_manager.session_needs_rebuild(cached_data, "llm"):
                llm = cached_data.get("llm")
            else:
                print("LLM needs rebuilding due to deserialization")

        # If no cached LLM, get a new one
        if not llm:
            print("Setting up new LLM for text query")
            # Get the default LLM model
            llm = get_default_llm(session, current_user)
            print("Default LLM model retrieved")
            # Cache the LLM
            session_manager.set_session(session_id, {"llm": llm, "type": "text_query"})
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
            # Get user language and create language instruction (use preferred_language)
            user_language = getattr(current_user, "preferred_language", None) or "en"
            language_name = settings.SUPPORTED_LANGUAGES.get(user_language, "English")
            language_instruction = f"Respond in this language: {language_name}."

            print(f"DEBUG: language_instruction = {language_instruction}")

            answer_content = invoke_llm(
                llm,
                qa_prompt_template,
                {
                    "question": rephrased_question,
                    "language_instruction": language_instruction,
                },
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
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")


# Add a cleanup task that runs periodically
@router.on_event("startup")
async def startup_event():
    async def cleanup_sessions():
        while True:
            await asyncio.sleep(3600)  # 60 minutes
            session_manager.cleanup_expired_sessions()
            print("Session cache cleanup performed")

    asyncio.create_task(cleanup_sessions())


# Assistant Intent Detection Models
class AssistantIntentRequest(BaseModel):
    message: str
    file_names: Optional[List[str]] = None


class AssistantIntentStep(BaseModel):
    action: str
    description: str


class AssistantIntentParameters(BaseModel):
    custom_instructions: Optional[str] = None
    search_mode: Optional[str] = "vector"
    consult_docs: Optional[bool] = True


class AssistantIntentResponse(BaseModel):
    primary_intent: str
    suggestion_type: Optional[str] = None
    is_multistep: bool = False
    steps: List[AssistantIntentStep] = []
    parameters: AssistantIntentParameters = AssistantIntentParameters()
    confidence: float
    reasoning: str


@router.post("/assistant/detect-intent", response_model=AssistantIntentResponse)
async def detect_assistant_intent(
    request: AssistantIntentRequest,
    current_user: CurrentUser,
    session: SessionDep,
) -> AssistantIntentResponse:
    """
    Use LLM to detect user intent for assistant mode requests.
    Analyzes the message and file information to determine appropriate actions.
    """
    try:
        print("DEBUG: Starting intent detection")
        # Prepare the prompt with user message and file context
        file_context = ""
        if request.file_names:
            file_context = f"\n\nUploaded files: {', '.join(request.file_names)}"
            # Add file type hints
            file_types = []
            for filename in request.file_names:
                if filename.lower().endswith(".pdf"):
                    file_types.append("PDF document")
                elif filename.lower().endswith((".docx", ".doc")):
                    file_types.append("Word document")
                elif filename.lower().endswith((".xlsx", ".xls", ".csv")):
                    file_types.append("spreadsheet")
                elif filename.lower().endswith((".txt", ".md")):
                    file_types.append("text document")
                else:
                    file_types.append("document")
            if file_types:
                file_context += f"\nFile types: {', '.join(set(file_types))}"

        print(f"DEBUG: File context: {file_context}")
        prompt = f"""Analyze this user request and determine the appropriate action.

User request: {request.message}
File context: {file_context}

Return a JSON object with:
- primary_intent: "generate", "review", "compare", "match", or "chatbot"
- suggestion_type: "outline", "checklist", "topics", "form_template", or null
- is_multistep: true or false
- steps: array of actions
- parameters: object with custom_instructions, search_mode, consult_docs
- confidence: 0.0-1.0
- reasoning: explanation

Example: {{"primary_intent": "generate", "suggestion_type": "outline", "is_multistep": true, "steps": [{{"action": "suggest_outline", "description": "Generate outline"}}, {{"action": "run_generate", "description": "Generate report"}}], "parameters": {{"custom_instructions": "about canned sardines"}}, "confidence": 0.9, "reasoning": "User wants to generate content with outline first"}}"""
        print(f"DEBUG: Prompt prepared, length: {len(prompt)}")

        # Get LLM for intent detection
        llm = get_default_llm(session, current_user)
        print(f"DEBUG: LLM retrieved: {type(llm)}")

        # Call LLM for intent detection
        print("DEBUG: Calling invoke_llm")
        try:
            import asyncio

            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, invoke_llm, llm, prompt, None)
            print("DEBUG: LLM call completed successfully")
        except Exception as e:
            print(f"DEBUG: LLM call failed: {type(e).__name__}: {str(e)}")
            raise

        print("LLM intent detection response:", response)

        # Parse the JSON response
        try:
            # Extract JSON from the response (LLM might add extra text)
            response_text = response.strip()
            # Look for JSON object in the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                intent_data = json.loads(json_str)
            else:
                # Fallback if no JSON found
                intent_data = {
                    "primary_intent": "chatbot",
                    "suggestion_type": None,
                    "is_multistep": False,
                    "steps": [{"action": "chat", "description": "Have a conversation"}],
                    "parameters": {},
                    "confidence": 0.5,
                    "reasoning": "Could not parse LLM response, defaulting to chat",
                }

            # Validate and structure the response
            validated_response = AssistantIntentResponse(
                primary_intent=intent_data.get("primary_intent", "chatbot"),
                suggestion_type=intent_data.get("suggestion_type"),
                is_multistep=intent_data.get("is_multistep", False),
                steps=[
                    AssistantIntentStep(**step) for step in intent_data.get("steps", [])
                ],
                parameters=AssistantIntentParameters(
                    **intent_data.get("parameters", {})
                ),
                confidence=min(1.0, max(0.0, intent_data.get("confidence", 0.5))),
                reasoning=intent_data.get("reasoning", "Intent detected by LLM"),
            )

            return validated_response

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # Fallback for parsing errors
            print(f"DEBUG: JSON parsing error: {str(e)}")
            return AssistantIntentResponse(
                primary_intent="chatbot",
                suggestion_type=None,
                is_multistep=False,
                steps=[
                    AssistantIntentStep(
                        action="chat", description="Have a conversation"
                    )
                ],
                parameters=AssistantIntentParameters(),
                confidence=0.3,
                reasoning=f"Failed to parse LLM response: {str(e)}",
            )

    except Exception as e:
        # Final fallback
        print(
            f"DEBUG: Final exception in intent detection: {type(e).__name__}: {str(e)}"
        )
        import traceback

        traceback.print_exc()
        return AssistantIntentResponse(
            primary_intent="chatbot",
            suggestion_type=None,
            is_multistep=False,
            steps=[
                AssistantIntentStep(action="chat", description="Have a conversation")
            ],
            parameters=AssistantIntentParameters(),
            confidence=0.1,
            reasoning=f"Error in intent detection: {str(e)}",
        )
