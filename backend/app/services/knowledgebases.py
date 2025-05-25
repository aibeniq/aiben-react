from typing import List
import uuid
import hashlib
from fastapi import UploadFile
from sqlmodel import select, Session, delete
from app.models import Source, SourceData, EmbeddingModel, KnowledgeBase
from app.api.deps import CurrentUser
from io import BytesIO
import zipfile
import logging
import os
import tempfile
from langchain_chroma import Chroma
from app.services.embeddings import load_embeddings_model
import shutil
from datetime import datetime


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
        #file.file.seek(0)
        file_content = file.file.read()

        file_hash = hashlib.sha256(file_content).hexdigest()

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
                knowledge_base_id=knowledge_base_id
            )
            session.add(source)
        else:

            # Compress the file content into .zip format
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(file.filename, file_content)
            compressed_content = zip_buffer.getvalue()

            # Create new source_data entry
            source_data_id = uuid.uuid4()
            source_data = SourceData(
                id=source_data_id,
                data=compressed_content,
                file_hash=file_hash
            )
            session.add(source_data)
            session.flush()

            # Create new source entry
            source = Source(
                source_data_id=source_data_id,
                owner_id=current_user.id,
                name=file.filename,
                knowledge_base_id=knowledge_base_id
            )
            session.add(source)

        file.file.seek(0)
    
    @staticmethod
    def get_source_by_id(session: Session, source_id: uuid.UUID) -> Source | None:
        """Get a source by id."""
        try:
            return session.exec(
                select(Source).where(Source.id == source_id)
            ).first()
        except Exception as e:
            logger.error(f"Error retrieving source {source_id}: {str(e)}")
            raise
    
    @staticmethod
    def update_title(session: Session, knowledge_base_id: uuid.UUID, new_title: str) -> KnowledgeBase | None:
        """Update the title of a knowledge base.
        
        Args:
            session: SQLModel database session
            knowledge_base_id: UUID of the knowledge base to update
            new_title: New title for the knowledge base
            
        Returns:
            The updated knowledge base if successful, None if not found
            
        Raises:
            ValueError: If the new title is invalid
            RuntimeError: If there's a database error
        """
        try:
            if not new_title or not new_title.strip():
                raise ValueError("Title cannot be empty")
            
            if len(new_title) > 255:
                raise ValueError("Title exceeds maximum length of 255 characters")
            
            kb = session.exec(
                select(KnowledgeBase).where(KnowledgeBase.id == knowledge_base_id)
            ).first()
            
            if not kb:
                logger.info(f"Knowledge base {knowledge_base_id} not found")
                return None
            
            # Check for duplicate title
            existing_kb = session.exec(
                select(KnowledgeBase)
                .where(
                    (KnowledgeBase.title == new_title) & 
                    (KnowledgeBase.id != knowledge_base_id) &
                    (KnowledgeBase.owner_id == kb.owner_id)
                )
            ).first()
            
            if existing_kb:
                raise ValueError(f"A knowledge base with title '{new_title}' already exists")
            
            kb.title = new_title
            kb.date_modified = datetime.now(datetime.UTC)
            
            session.commit()
            return kb
            
        except ValueError as e:
            logger.warning(f"Validation error updating title for knowledge base {knowledge_base_id}: {str(e)}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating title for knowledge base {knowledge_base_id}: {str(e)}")
            raise RuntimeError(f"Failed to update knowledge base title: {str(e)}")
        
    
    @staticmethod
    def update_description(session: Session, knowledge_base_id: uuid.UUID, new_description: str) -> KnowledgeBase | None:
        """Update the description of a knowledge base.
        
        Args:
            session: SQLModel database session
            knowledge_base_id: UUID of the knowledge base to update
            new_description: New description for the knowledge base
            
        Returns:
            The updated knowledge base if successful, None if not found
            
        Raises:
            ValueError: If the new description is invalid
            RuntimeError: If there's a database error
        """
        try:            
            kb = session.exec(
                select(KnowledgeBase).where(KnowledgeBase.id == knowledge_base_id)
            ).first()
            
            if not kb:
                logger.info(f"Knowledge base {knowledge_base_id} not found")
                return None
            
            kb.description = new_description
            kb.date_modified = datetime.now(datetime.UTC)
            
            session.commit()
            return kb
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating description for knowledge base {knowledge_base_id}: {str(e)}")
            raise RuntimeError(f"Failed to update knowledge base description: {str(e)}")
            
    
    @staticmethod
    def delete_source(session: Session, source_id: uuid.UUID) -> Source | None:
        """
        Delete the source from the knowledge base and update the vector database.
        It will also delete the source_data from the database if no references to it remain.
        
        Args:
            session: SQLModel database session
            source_id: UUID of the source to delete
            
        Returns:
            The deleted source if successful, None if source not found
            
        Raises:
            ValueError: If the source or knowledge base is not found
            RuntimeError: If there's an error with the vector database operations
        """
        try:
            source_to_delete = session.exec(
                select(Source).where(Source.id == source_id)
            ).first()
            
            if not source_to_delete:
                logger.info(f"Source {source_id} not found")
                return None
                
            kb = session.exec(
                select(KnowledgeBase).where(KnowledgeBase.id == source_to_delete.knowledge_base_id)
            ).first()
            
            if not kb:
                logger.info(f"Knowledge base {source_to_delete.knowledge_base_id} not found")
                return None

            # delete from chroma database as well
            if kb.data:
                chroma_dir = tempfile.mkdtemp()
                try:
                    # extract chroma database
                    with zipfile.ZipFile(BytesIO(kb.data), 'r') as zip_ref:
                        zip_ref.extractall(chroma_dir)

                    if not kb.embedding_model:
                        raise ValueError("Knowledge base has no embedding model configured")
                        
                    embeddings, _, _ = load_embeddings_model(
                        provider=kb.embedding_model.provider,
                        model_id=kb.embedding_model.model_id
                    )

                    # initialize and update chroma database
                    chroma_vector_database = Chroma(persist_directory=chroma_dir, embedding_function=embeddings)
                    chroma_vector_database.delete(ids=[str(source_to_delete.source_data_id)])

                    # update knowledge base data
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for root, _, filenames in os.walk(chroma_dir):
                            for filename in filenames:
                                file_path = os.path.join(root, filename)
                                arcname = os.path.relpath(file_path, chroma_dir)
                                zip_file.write(file_path, arcname)
                    zip_buffer.seek(0)
                    kb.data = zip_buffer.read()

                except Exception as e:
                    logger.error(f"Error updating Chroma database: {str(e)}")
                    raise RuntimeError(f"Failed to update vector database: {str(e)}")
                finally:
                    shutil.rmtree(chroma_dir)

            session.delete(source_to_delete)
            
            # delete source_data if no references to it remain
            if source_to_delete.source_data_id:
                other_references = session.exec(
                    select(Source).where(Source.source_data_id == source_to_delete.source_data_id)
                ).all()
                
                if not other_references:
                    KnowledgeBaseService._delete_source_data(session, source_to_delete.source_data_id)
            
            session.commit()
            return source_to_delete
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting source {source_id}: {str(e)}")
            raise

    @staticmethod
    def _delete_source_data(session: Session, source_data_id: uuid.UUID) -> SourceData | None:
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
def get_embedding_model(session):
    """Get the current default embedding model from the database."""
    print("Now determining which embedding model to use...")
    
    # Try to get the default model
    default_model = session.exec(
        select(EmbeddingModel)
        .where(EmbeddingModel.is_default == True)
    ).first()
    
    # If no default model is found, fallback to a hardcoded value
    if not default_model:
        from app.models import ModelProvider
        return {
            "model_id": "all-MiniLM-L6-v2",
            "provider": ModelProvider.HUGGINGFACE
        }
    
    return {
        "model_id": default_model.model_id,
        "provider": default_model.provider
    }