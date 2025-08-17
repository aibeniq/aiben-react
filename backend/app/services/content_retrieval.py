"""
Content retrieval utilities for knowledge base operations.
"""

import logging
from typing import List, Optional, Tuple
from sqlmodel import Session, select
from app.models import KnowledgeBase, Source, SourceData
from app.services.embeddings import load_embeddings_model
from app.services.knowledgebases import get_embedding_model
from app.services.retrievers import create_ensemble_retriever
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
        # Get the knowledge base
        kb = session.exec(
            select(KnowledgeBase).where(
                KnowledgeBase.id == knowledge_base_id,
                KnowledgeBase.owner_id == current_user.id,
            )
        ).first()

        if not kb:
            logger.warning(
                f"Knowledge base {knowledge_base_id} not found or not accessible"
            )
            return "", ""

        if search_mode == "full_scan":
            # Get all documents from knowledge base
            sources = session.exec(
                select(Source).where(
                    Source.knowledge_base_id == knowledge_base_id,
                    Source.owner_id == current_user.id,
                )
            ).all()

            if sources:
                kb_content_parts = []
                for source in sources:
                    # Get the actual document content
                    source_data = session.get(SourceData, source.source_data_id)
                    if source_data and source_data.data:
                        try:
                            # Decode the document content
                            content = source_data.data.decode("utf-8")
                            kb_content_parts.append(
                                f"Document: {source.name}\n{content}"
                            )
                        except UnicodeDecodeError:
                            # Handle binary files or encoding issues
                            logger.warning(
                                f"Could not decode content for source {source.name}"
                            )
                            continue

                if kb_content_parts:
                    full_content = "\n\n" + "=" * 80 + "\n\n".join(kb_content_parts)
                    
                    # Check if content exceeds reasonable limits and potentially needs chunking
                    # This function returns content for use in prompts, so we need to be careful about size
                    max_content_size = 100000  # Conservative limit for knowledge base content
                    
                    if len(full_content) > max_content_size:
                        logger.warning(f"Knowledge base content is very large ({len(full_content)} chars), truncating to avoid context issues")
                        
                        # Truncate but try to end at a reasonable boundary
                        truncated_content = full_content[:max_content_size]
                        
                        # Find the last complete document boundary
                        last_boundary = truncated_content.rfind("=" * 80)
                        if last_boundary > max_content_size // 2:  # Only use if we keep at least half the content
                            truncated_content = truncated_content[:last_boundary]
                        
                        content = truncated_content + f"\n\n[Content truncated - showing first {len(truncated_content)} characters of {len(full_content)} total]"
                        instruction = "Use the following reference documents (content may be truncated due to size) to inform your generation:"
                    else:
                        content = full_content
                        instruction = "Use ALL the following reference documents to inform your generation:"
                        
                    return content, instruction

        elif search_mode == "vector":
            # Use vector search to get relevant documents
            if not chroma_db:
                logger.warning("ChromaDB not available for vector search")
                return "", ""

            # Get embedding model for the knowledge base
            embedding_info = get_embedding_model(session, current_user)
            if not embedding_info:
                logger.warning("No embedding model available")
                return "", ""

            # Load the embedding model
            embeddings = load_embeddings_model(
                provider=embedding_info["provider"], model_id=embedding_info["model_id"]
            )

            # Create ensemble retriever
            retriever = create_ensemble_retriever(
                knowledge_base_id=kb.id, embeddings=embeddings, k=8
            )

            # Get relevant documents
            docs = retriever.get_relevant_documents(query)
            if docs:
                content = "\n\n".join(
                    [
                        f"Source: {doc.metadata.get('source', 'Unknown')}\nContent: {doc.page_content}"
                        for doc in docs[:5]  # Limit to top 5 results
                    ]
                )
                instruction = "Use the following relevant reference documents to inform your generation:"
                return content, instruction

    except Exception as e:
        logger.warning(f"Failed to retrieve knowledge base content: {str(e)}")

    return "", ""
