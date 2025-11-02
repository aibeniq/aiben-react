from typing import List
import uuid
import hashlib
import tempfile
import os
from fastapi import UploadFile, HTTPException
from sqlmodel import select, Session, delete
from app.models import Source, SourceData, EmbeddingModel, KnowledgeBase
from app.api.deps import CurrentUser
from io import BytesIO
import zipfile
import logging
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from app.core.config import settings


logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    @staticmethod
    def create_source_entries(
        *,
        session: Session,
        current_user: CurrentUser,
        knowledge_base_id: uuid.UUID,
        file: UploadFile,
    ) -> None:
        """
        Create source and source_data entries for a single file.

        Args:
            session: Database session
            current_user: Current authenticated user
            knowledge_base_id: ID of parent knowledge base
            file: Uploaded file
        """
        from app.services.page_counter import PageCounter
        
        # file.file.seek(0)
        file_content = file.file.read()

        file_hash = hashlib.sha256(file_content).hexdigest()

        # COUNT PAGES FOR THIS FILE
        page_count = PageCounter.count_pages_from_bytes(file_content, file.filename)

        # Check if this file hash already exists
        existing_source_data = session.exec(
            select(SourceData).where(SourceData.file_hash == file_hash)
        ).first()

        if existing_source_data:
            # Create only a new source entry using existing source_data
            source = Source(
                source_data_id=existing_source_data.id,
                owner_id=current_user.id,
                name=file.filename,
                knowledge_base_id=knowledge_base_id,
                page_count=page_count,
            )
            session.add(source)
        else:

            # Compress the file content into .zip format using temporary file
            # for memory efficiency with large files
            temp_zip_path = None
            try:
                temp_zip_fd, temp_zip_path = tempfile.mkstemp(suffix=".zip")
                os.close(temp_zip_fd)  # Close file descriptor, but keep path
                
                with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
                    zip_file.writestr(file.filename, file_content)
                
                # Read compressed content from file
                with open(temp_zip_path, "rb") as zip_read_file:
                    compressed_content = zip_read_file.read()
                    
                # Check file size - warn if very large
                file_size_mb = len(compressed_content) / 1024 / 1024
                if file_size_mb > 100:  # Warn for files > 100MB
                    print(f"Warning: Large compressed file {file.filename}: {file_size_mb:.1f}MB")

            except Exception as e:
                # Clean up temporary file on error
                if temp_zip_path and os.path.exists(temp_zip_path):
                    try:
                        os.unlink(temp_zip_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Could not clean up temp ZIP file: {cleanup_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error compressing file {file.filename}: {str(e)}"
                )
            finally:
                # Always clean up temporary file
                if temp_zip_path and os.path.exists(temp_zip_path):
                    try:
                        os.unlink(temp_zip_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Could not clean up temp ZIP file: {cleanup_error}")

            # Create new source_data entry
            source_data_id = uuid.uuid4()
            source_data = SourceData(
                id=source_data_id, data=compressed_content, file_hash=file_hash
            )
            session.add(source_data)
            session.flush()

            # Create new source entry
            source = Source(
                source_data_id=source_data_id,
                owner_id=current_user.id,
                name=file.filename,
                knowledge_base_id=knowledge_base_id,
                page_count=page_count,
            )
            session.add(source)

        file.file.seek(0)

    @staticmethod
    def recalculate_total_pages(session: Session, knowledge_base_id: uuid.UUID) -> None:
        """Recalculate total pages for a knowledge base."""
        from sqlalchemy.sql import func
        
        total_pages = session.exec(
            select(func.sum(Source.page_count)).where(
                Source.knowledge_base_id == knowledge_base_id
            )
        ).one() or 0
        
        kb = session.get(KnowledgeBase, knowledge_base_id)
        if kb:
            kb.total_pages = total_pages
            session.add(kb)

    @staticmethod
    def get_source_by_id(session: Session, source_id: uuid.UUID) -> Source | None:
        """Get a source by id."""
        try:
            return session.exec(select(Source).where(Source.id == source_id)).first()
        except Exception as e:
            logger.error(f"Error retrieving source {source_id}: {str(e)}")
            raise

    @staticmethod
    def delete_source(session: Session, source_id: uuid.UUID) -> Source | None:
        """Delete a source."""
        try:
            source_to_delete = session.exec(
                select(Source).where(Source.id == source_id)
            ).first()

            if not source_to_delete:
                logger.info(f"Source {source_id} not found")
                return None

            source_data_id = source_to_delete.source_data_id

            session.delete(source_to_delete)

            if source_data_id:
                other_references = session.exec(
                    select(Source).where(Source.source_data_id == source_data_id)
                ).all()

                # delete source_data if it is not referenced by any other source
                if not other_references:
                    KnowledgeBaseService._delete_source_data(session, source_data_id)

            return source_to_delete

        except Exception as e:
            logger.error(f"Error deleting source {source_id}: {str(e)}")
            raise

    @staticmethod
    def _delete_source_data(
        session: Session, source_data_id: uuid.UUID
    ) -> SourceData | None:
        """Delete a source_data."""
        try:
            source_data_to_delete = session.exec(
                select(SourceData).where(SourceData.id == source_data_id)
            ).first()

            if not source_data_to_delete:
                logger.info(f"SourceData {source_data_id} not found")
                return None

            session.delete(source_data_to_delete)
            return source_data_to_delete

        except Exception as e:
            logger.error(f"Error deleting source_data {source_data_id}: {str(e)}")
            raise


# TODO: Move this to embeddings.py
def get_embedding_model(session: Session, current_user: CurrentUser):
    """Get the current default embedding model from the database."""
    print("Now determining which embedding model to use...")

    # Try to get the default model
    if current_user.default_embedding_model:
        default_model = session.get(
            EmbeddingModel, current_user.default_embedding_model
        )
        return {"model_id": default_model.model_id, "provider": default_model.provider}
    else:
        from app.models import ModelProvider

        return {"model_id": "all-MiniLM-L6-v2", "provider": ModelProvider.HUGGINGFACE}


def estimate_tokens_for_embedding(text: str) -> int:
    """
    Estimate tokens in text for embedding models using cl100k_base encoding.
    This is the same encoding used by OpenAI's text-embedding models.
    """
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        # Fallback to rough estimation if tiktoken fails
        return len(text) // 4


def chunk_documents_for_embedding(
    documents: List[Document], max_tokens_per_chunk: int = None
) -> List[List[Document]]:
    """
    Split documents into chunks that fit within embedding model token limits.

    Args:
        documents: List of Document objects to chunk
        max_tokens_per_chunk: Maximum tokens per chunk (defaults to config setting)

    Returns:
        List of document chunks, where each chunk is a list of documents
    """
    if max_tokens_per_chunk is None:
        max_tokens_per_chunk = settings.EMBEDDING_MAX_TOKENS_PER_REQUEST

    chunks = []
    current_chunk = []
    current_tokens = 0

    print(
        f"Chunking {len(documents)} documents with max {max_tokens_per_chunk:,} tokens per chunk"
    )

    for doc in documents:
        # Estimate tokens for this document's content
        doc_tokens = estimate_tokens_for_embedding(doc.page_content)

        # If this single document exceeds the limit, split it further
        if doc_tokens > max_tokens_per_chunk:
            print(
                f"⚠️  Document exceeds token limit ({doc_tokens:,} tokens), splitting further..."
            )

            # If we have accumulated docs, add them as a chunk first
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_tokens = 0

            # Split this large document into smaller pieces
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=max_tokens_per_chunk
                * 3,  # Rough character estimate (4 chars per token)
                chunk_overlap=200,
            )
            split_docs = text_splitter.split_documents([doc])

            # Group the split documents into token-limited chunks
            for split_doc in split_docs:
                split_tokens = estimate_tokens_for_embedding(split_doc.page_content)

                if current_tokens + split_tokens > max_tokens_per_chunk:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = [split_doc]
                    current_tokens = split_tokens
                else:
                    current_chunk.append(split_doc)
                    current_tokens += split_tokens
        else:
            # Check if adding this document would exceed the limit
            if current_tokens + doc_tokens > max_tokens_per_chunk:
                # Start a new chunk
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [doc]
                current_tokens = doc_tokens
            else:
                # Add to current chunk
                current_chunk.append(doc)
                current_tokens += doc_tokens

    # Add the last chunk if it has documents
    if current_chunk:
        chunks.append(current_chunk)

    print(f"✅ Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks
