"""
Content retrieval utilities for knowledge base operations.
"""

import logging
import tempfile
import zipfile
import os
import shutil
from io import BytesIO
from typing import List, Optional, Tuple
from sqlmodel import Session, select
from app.models import KnowledgeBase, Source, SourceData, EmbeddingModel
from app.services.embeddings import load_embeddings_model
from app.services.knowledgebases import get_embedding_model
from app.services.retrievers import create_ensemble_retriever
from app.services.document_utils import extract_text_from_file_unified
from langchain_community.vectorstores import Chroma
import base64

logger = logging.getLogger(__name__)


async def retrieve_knowledge_base_content(
    session: Session,
    current_user,
    knowledge_base_id: str,
    search_mode: str,
    query: str = "",
    chroma_db=None,
) -> Tuple[str, str]:
    """
    Retrieve content from knowledge base using either vector search or full scan.

    Args:
        session: Database session
        current_user: Current user object
        knowledge_base_id: ID of the knowledge base
        search_mode: "vector" or "full_scan"
        query: Query string for vector search (ignored for full_scan)
        chroma_db: ChromaDB instance for vector search

    Returns:
        tuple: (content_string, instruction_string)
    """
    try:
        import uuid

        # Convert string UUID to UUID object if needed
        if isinstance(knowledge_base_id, str):
            try:
                kb_uuid = uuid.UUID(knowledge_base_id)
            except ValueError:
                logger.error(
                    f"Invalid UUID format for knowledge_base_id: {knowledge_base_id}"
                )
                return "", ""
        else:
            kb_uuid = knowledge_base_id

        # Get the knowledge base - SAME AS CHATBOT
        kb = session.get(KnowledgeBase, kb_uuid)
        if not kb:
            logger.warning(
                f"Knowledge base {knowledge_base_id} not found or not accessible"
            )
            return "", ""

        if search_mode == "full_scan":
            # Get all documents from knowledge base - SIMILAR TO CHATBOT'S FULL TEXT APPROACH
            logger.info(
                f"Full scan mode: Looking for sources in KB {kb_uuid} for user {current_user.id}"
            )
            sources = session.exec(
                select(Source).where(
                    Source.knowledge_base_id == kb_uuid,
                    Source.owner_id == current_user.id,
                )
            ).all()

            logger.info(f"Found {len(sources)} sources in knowledge base")

            if sources:
                kb_content_parts = []
                for source in sources:
                    # Get the actual document content
                    logger.info(f"Processing source: {source.name} (ID: {source.id})")
                    source_data = session.get(SourceData, source.source_data_id)
                    if source_data and source_data.data:
                        logger.info(
                            f"Found source data for {source.name}, size: {len(source_data.data)} bytes"
                        )
                        try:
                            content = ""

                            # Handle different storage formats
                            if source_data.data.startswith(b"PK"):  # ZIP file
                                logger.info(
                                    f"Extracting content from ZIP file: {source.name}"
                                )
                                zip_data = BytesIO(source_data.data)
                                with zipfile.ZipFile(zip_data, "r") as zip_file:
                                    file_info = zip_file.infolist()[0]
                                    raw_file_content = zip_file.read(file_info.filename)
                                    # Use proper text extraction for the file
                                    try:
                                        content = extract_text_from_file_unified(
                                            raw_file_content, file_info.filename
                                        )
                                        logger.info(
                                            f"Successfully extracted text from ZIP content: {len(content)} characters"
                                        )
                                    except Exception as extract_error:
                                        logger.warning(
                                            f"Could not extract text from ZIP content for {source.name}: {extract_error}"
                                        )
                                        # Fallback to simple UTF-8 decoding for text files
                                        try:
                                            content = raw_file_content.decode("utf-8")
                                        except UnicodeDecodeError:
                                            logger.warning(
                                                f"Could not decode ZIP content as UTF-8 for {source.name}"
                                            )
                                            continue
                            else:
                                # Try proper document text extraction first
                                logger.info(
                                    f"Attempting text extraction from {source.name} ({len(source_data.data)} bytes)"
                                )
                                try:
                                    content = extract_text_from_file_unified(
                                        source_data.data, source.name
                                    )
                                    logger.info(
                                        f"Successfully extracted text using document utils: {len(content)} characters"
                                    )
                                except Exception as extract_error:
                                    logger.warning(
                                        f"Document text extraction failed for {source.name}: {extract_error}"
                                    )
                                    # Fallback to UTF-8 decoding for plain text files
                                    try:
                                        content = source_data.data.decode("utf-8")
                                        logger.info(
                                            f"Fallback UTF-8 decoding successful: {len(content)} characters"
                                        )
                                    except UnicodeDecodeError as decode_error:
                                        logger.error(
                                            f"Could not decode content for {source.name}: {decode_error}"
                                        )
                                        logger.info(
                                            f"File appears to be binary data that requires specialized extraction"
                                        )
                                        continue

                            if content and content.strip():
                                kb_content_parts.append(
                                    f"Document: {source.name}\n{content}"
                                )
                                logger.info(
                                    f"Added content for {source.name}: {len(content)} characters"
                                )
                            else:
                                logger.warning(
                                    f"No extractable text content found in {source.name}"
                                )

                        except Exception as e:
                            logger.error(
                                f"Unexpected error processing source {source.name}: {e}"
                            )
                            import traceback

                            logger.debug(f"Full traceback: {traceback.format_exc()}")
                            continue

                if kb_content_parts:
                    full_content = "\n\n" + "=" * 80 + "\n\n".join(kb_content_parts)

                    # Check if content exceeds reasonable limits and potentially needs chunking
                    max_content_size = (
                        100000  # Conservative limit for knowledge base content
                    )

                    if len(full_content) > max_content_size:
                        logger.warning(
                            f"Knowledge base content is very large ({len(full_content)} chars), truncating to avoid context issues"
                        )

                        # Truncate but try to end at a reasonable boundary
                        truncated_content = full_content[:max_content_size]

                        # Find the last complete document boundary
                        last_boundary = truncated_content.rfind("=" * 80)
                        if (
                            last_boundary > max_content_size // 2
                        ):  # Only use if we keep at least half the content
                            truncated_content = truncated_content[:last_boundary]

                        content = (
                            truncated_content
                            + f"\n\n[Content truncated - showing first {len(truncated_content)} characters of {len(full_content)} total]"
                        )
                        instruction = "Use the following reference documents (content may be truncated due to size) to inform your generation:"
                    else:
                        content = full_content
                        instruction = "Use ALL the following reference documents to inform your generation:"

                    logger.info(
                        f"Retrieved {len(kb_content_parts)} documents from full scan"
                    )
                    return content, instruction
                else:
                    logger.warning(
                        "No content could be extracted from knowledge base sources in full_scan mode"
                    )
                    logger.info(
                        f"Processed {len(sources)} sources but none yielded extractable content"
                    )
                    return "", ""
            else:
                logger.warning("No sources found in knowledge base for full_scan mode")
                logger.info(
                    f"Knowledge base {kb_uuid} exists but contains no sources for user {current_user.id}"
                )
                return "", ""

        elif search_mode == "vector":
            # Set up ChromaDB for vector search - EXACT SAME PATTERN AS CHATBOT
            if not chroma_db:
                logger.info("Setting up ChromaDB for vector search")

                # Create temporary directory for ChromaDB extraction - SAME AS CHATBOT
                temp_dir = tempfile.mkdtemp()

                try:
                    # Extract the zipped ChromaDB into the temp directory - SAME AS CHATBOT
                    if kb.storage_type == "file" and kb.file_path:
                        if os.path.exists(kb.file_path):
                            with zipfile.ZipFile(kb.file_path, "r") as zip_ref:
                                zip_ref.extractall(temp_dir)
                        else:
                            logger.error(
                                f"Knowledge base file not found: {kb.file_path}"
                            )
                            return "", ""
                    elif kb.data:
                        with zipfile.ZipFile(BytesIO(kb.data), "r") as zip_ref:
                            zip_ref.extractall(temp_dir)
                    else:
                        logger.error("Knowledge base has no vector database data")
                        return "", ""

                    # Get embedding model - SAME LOGIC AS CHATBOT
                    if kb.embedding_model_id:
                        embedding_model = session.get(
                            EmbeddingModel, kb.embedding_model_id
                        )
                        if embedding_model:
                            model_id = embedding_model.model_id
                            provider = embedding_model.provider
                            logger.info(
                                f"Using KB's embedding model: {model_id} ({provider})"
                            )
                        else:
                            # Fallback to user's default - SAME AS CHATBOT
                            embedding_info = get_embedding_model(session, current_user)
                            model_id = embedding_info["model_id"]
                            provider = embedding_info["provider"]
                            logger.info(
                                f"KB embedding model not found, using default: {model_id}"
                            )
                    else:
                        embedding_info = get_embedding_model(session, current_user)
                        model_id = embedding_info["model_id"]
                        provider = embedding_info["provider"]
                        logger.info(f"Using default embedding model: {model_id}")

                    # Load embeddings and ChromaDB - SAME AS CHATBOT
                    embeddings = load_embeddings_model(
                        provider=provider, model_id=model_id
                    )
                    chroma_db = Chroma(
                        persist_directory=temp_dir, embedding_function=embeddings
                    )

                    logger.info("ChromaDB initialized successfully for vector search")

                except Exception as e:
                    logger.error(f"Error setting up ChromaDB: {e}")
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return "", ""

            # Create enhanced retriever and get documents - WITH SMART FILTERING
            try:
                from app.services.enhanced_retrieval import SmartRetrieverFactory

                retriever = SmartRetrieverFactory.create_general_document_retriever(
                    chroma_db=chroma_db,
                    search_kwargs={"k": 8},
                )

                docs = retriever.get_relevant_documents(query)

                if docs:
                    content = "\n\n".join(
                        [
                            f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
                            for doc in docs[:5]  # Limit to top 5 results
                        ]
                    )
                    instruction = "Use the following relevant reference documents to inform your generation:"
                    logger.info(f"Retrieved {len(docs)} documents from vector search")

                    # Clean up temp directory
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except:
                        pass

                    return content, instruction
                else:
                    logger.warning("No relevant documents found in vector search")
                    # Clean up temp directory
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except:
                        pass
                    return "", ""

            except Exception as e:
                logger.error(f"Error in vector search: {e}")
                # Clean up temp directory
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except:
                    pass
                return "", ""

        # If we get here, no content was found
        logger.warning("No content found in knowledge base")
        return "", ""

    except Exception as e:
        logger.error(f"Failed to retrieve knowledge base content: {str(e)}")
        import traceback

        traceback.print_exc()
        return "", ""
