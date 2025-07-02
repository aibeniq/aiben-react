import uuid
import logging
from datetime import datetime, timezone
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlmodel import func, select
from sqlalchemy.sql import func

from app.api.deps import CurrentUser, SessionDep, VectorDBDep
from app.services.knowledgebases import KnowledgeBaseService
from app.models import (
    KnowledgeBase,
    KnowledgeBaseCreate,
    KnowledgeBasePublic,
    KnowledgeBasesPublic,
    KnowledgeBaseUpdate,
    Message,
    Source,
    EmbeddingModel,
)

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=KnowledgeBasesPublic)
def read_knowledge_bases(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve knowledge bases with additional metadata: Number of Sources, Date Created, and Date Modified.
    """
    # Base query to count sources and retrieve metadata
    query = (
        session.query(
            KnowledgeBase,
            func.count(Source.id).label("number_of_sources"),
            KnowledgeBase.date_created,
            KnowledgeBase.date_modified,
        )
        .join(Source, Source.knowledge_base_id == KnowledgeBase.id, isouter=True)
        .group_by(KnowledgeBase.id)
    )

    # Apply filters based on user permissions
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(KnowledgeBase)
        count = session.exec(count_statement).one()
        query = query.offset(skip).limit(limit)
    else:
        count_statement = (
            select(func.count())
            .select_from(KnowledgeBase)
            .where(KnowledgeBase.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        query = (
            query.filter(KnowledgeBase.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )

    # Execute the query
    results = query.all()

    # Format the response
    knowledge_bases = []
    for kb in results:
        # Get embedding model name if it exists
        embedding_model_name = None
        if kb.KnowledgeBase.embedding_model_id:
            model = session.get(EmbeddingModel, kb.KnowledgeBase.embedding_model_id)
            if model:
                embedding_model_name = model.name

        kb_public = KnowledgeBasePublic(
            id=kb.KnowledgeBase.id,
            owner_id=kb.KnowledgeBase.owner_id,
            title=kb.KnowledgeBase.title,
            description=kb.KnowledgeBase.description,
            files=[],  # Files can be populated separately if needed
            number_of_sources=kb.number_of_sources,
            date_created=kb.date_created,
            date_modified=kb.date_modified,
            embedding_model_id=kb.KnowledgeBase.embedding_model_id,
            embedding_model_name=embedding_model_name,
        )
        knowledge_bases.append(kb_public)

    return KnowledgeBasesPublic(data=knowledge_bases, count=count)


@router.get("/{id}", response_model=KnowledgeBasePublic)
def read_knowledge_base(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> KnowledgeBasePublic:
    """Get knowledge base by ID."""

    # get knowledge base
    knowledge_base = KnowledgeBaseService.get_by_id(session=session, id=id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    # Get embedding model name if it exists
    embedding_model_name = None
    if knowledge_base.embedding_model_id:
        model = session.get(EmbeddingModel, knowledge_base.embedding_model_id)
        if model:
            embedding_model_name = model.name

    # Get all sources for this knowledge base
    sources = session.exec(select(Source).where(Source.knowledge_base_id == id)).all()

    files = []
    for source in sources:
        # Only include metadata, not the actual file content
        files.append(
            {
                "id": str(source.source_data_id),
                "name": source.name,
                "date_created": source.date_created,
                # Don't include data_base64 here
            }
        )

    # Construct the response model
    knowledge_base_public = KnowledgeBasePublic(
        **knowledge_base.model_dump(),
        files=files,
        embedding_model_name=embedding_model_name,
    )
    return knowledge_base_public


@router.post("/", response_model=KnowledgeBasePublic)
def create_knowledge_base(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    vectordb_service: VectorDBDep,
    knowledge_base_in: KnowledgeBaseCreate = Depends(),
    files: List[UploadFile] = File(...),
) -> Any:
    """Create new knowledge base."""

    # check if a knowledge base with this title already exists for this user
    existing_kb = KnowledgeBaseService.get_by_title(
        session=session,
        title=knowledge_base_in.title,
        owner_id=current_user.id,
    )

    if existing_kb:
        raise HTTPException(
            status_code=409,
            detail=f"A knowledge base with the title '{knowledge_base_in.title}' already exists",
        )

    # create knowledge base
    knowledge_base = KnowledgeBaseService.create_knowledge_base(
        session=session,
        knowledge_base_in=knowledge_base_in,
        current_user=current_user,
    )

    # add sources to knowledge base
    for file in files:
        # Reset the file pointer before passing to create_source_entries
        file.file.seek(0)

        # add source to knowledge base
        source = KnowledgeBaseService.add_source(
            session=session,
            current_user=current_user,
            knowledge_base_id=knowledge_base.id,
            file=file,
        )

        # add source to vector database
        vectordb_service.add_file(
            file=file,
            knowledge_base_id=knowledge_base.id,
            user_id=current_user.id,
            source_id=source.id,
        )

    # return knowledge base
    session.commit()
    session.refresh(knowledge_base)
    return knowledge_base


@router.put("/{id}", response_model=KnowledgeBasePublic)
def update_knowledge_base(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    vectordb_service: VectorDBDep,
    id: uuid.UUID,
    knowledge_base_in: KnowledgeBaseUpdate = Depends(),
    files: Optional[List[UploadFile]] = None,
) -> KnowledgeBasePublic:
    """Update a knowledge base."""

    # get knowledge base and validate permissions
    knowledge_base = KnowledgeBaseService.get_by_id(session=session, id=id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    if not current_user.is_superuser and knowledge_base.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # update basic knowledge base properties
    update_dict = knowledge_base_in.model_dump(
        exclude_unset=True, exclude={"removed_file_ids"}
    )
    knowledge_base.sqlmodel_update(update_dict)

    # handle file operations
    try:
        # add new files
        if files:
            logger.info(f"Adding {len(files)} new files to knowledge base {id}")
            for file in files:
                source = KnowledgeBaseService.add_source(
                    session=session,
                    current_user=current_user,
                    knowledge_base_id=knowledge_base.id,
                    file=file,
                )
                vectordb_service.add_file(
                    file=file,
                    knowledge_base_id=knowledge_base.id,
                    user_id=current_user.id,
                    source_id=source.id,
                )

        # remove files
        if knowledge_base_in.removed_file_ids:
            logger.info(
                f"Removing {len(knowledge_base_in.removed_file_ids)} files from knowledge base {id}"
            )
            for source_id in knowledge_base_in.removed_file_ids:
                source = KnowledgeBaseService.delete_source_by_id(
                    session=session,
                    source_id=source_id,
                    knowledge_base_id=knowledge_base.id,
                )
                vectordb_service.delete_source(source_id=source.id)

    except ValueError as e:
        logger.error(f"Validation error updating knowledge base {id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error updating vector database for knowledge base {id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=f"Error updating vector database: {str(e)}"
        )

    # update date modified and return
    knowledge_base.date_modified = datetime.now(timezone.utc)
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)

    return knowledge_base


@router.delete("/{id}", response_model=Message)
def delete_knowledge_base(
    session: SessionDep,
    current_user: CurrentUser,
    vectordb_service: VectorDBDep,
    id: uuid.UUID,
) -> Message:
    """
    Delete a knowledge base.
    """
    knowledge_base = KnowledgeBaseService.get_by_id(session=session, id=id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    if not current_user.is_superuser and knowledge_base.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # delete knowledge base
    KnowledgeBaseService.delete_knowledge_base(
        session=session, knowledge_base_id=knowledge_base.id
    )

    # delete chunks from vector database
    vectordb_service.delete_knowledge_base(knowledge_base_id=knowledge_base.id)

    return Message(message="Knowledge base deleted successfully")
