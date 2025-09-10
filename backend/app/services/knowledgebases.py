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

            # Compress the file content into .zip format
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(file.filename, file_content)
            compressed_content = zip_buffer.getvalue()

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
