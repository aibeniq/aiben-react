import uuid
from typing import Any, List

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlmodel import func, select

import zipfile
import io

from app.api.deps import CurrentUser, SessionDep
from app.models import KnowledgeBase, KnowledgeBaseCreate, KnowledgeBasePublic, KnowledgeBasesPublic, KnowledgeBaseUpdate, Message

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


@router.get("/", response_model=KnowledgeBasesPublic)
def read_knowledge_bases(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve knowledge bases.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(KnowledgeBase)
        count = session.exec(count_statement).one()
        statement = select(KnowledgeBase).offset(skip).limit(limit)
        knowledge_bases = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(KnowledgeBase)
            .where(KnowledgeBase.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(KnowledgeBase)
            .where(KnowledgeBase.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        knowledge_bases = session.exec(statement).all()

    return KnowledgeBasesPublic(data=knowledge_bases, count=count)


@router.get("/{id}", response_model=KnowledgeBasePublic)
def read_knowledge_base(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get knowledge base by ID.
    """
    knowledge_base = session.get(KnowledgeBase, id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    if not current_user.is_superuser and (knowledge_base.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return knowledge_base


@router.post("/", response_model=KnowledgeBasePublic)
def create_knowledge_base(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    knowledge_base_in: KnowledgeBaseCreate = Depends(),
    #title: str,
    #description: str | None = None,
    files: List[UploadFile] = File(...),
) -> Any:
    """
    Create new knowledge base with compressed file data.
    """
    # Compress the uploaded files into a zip archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in files:
            file_content = file.file.read()
            zip_file.writestr(file.filename, file_content)
    zip_buffer.seek(0)

    # Create the knowledge base using the KnowledgeBaseCreate schema
    knowledge_base = KnowledgeBase(
        title=knowledge_base_in.title,
        description=knowledge_base_in.description,
        owner_id=current_user.id,
        data=zip_buffer.read(),  # Save the compressed data in the `data` column
    )
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)
    return knowledge_base


@router.put("/{id}", response_model=KnowledgeBasePublic)
def update_knowledge_base(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    knowledge_base_in: KnowledgeBaseUpdate,
) -> Any:
    """
    Update a knowledge base.
    """
    knowledge_base = session.get(KnowledgeBase, id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    if not current_user.is_superuser and (knowledge_base.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = knowledge_base_in.model_dump(exclude_unset=True)
    knowledge_base.sqlmodel_update(update_dict)
    session.add(knowledge_base)
    session.commit()
    session.refresh(knowledge_base)
    return knowledge_base


@router.delete("/{id}")
def delete_knowledge_base(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a knowledge base.
    """
    knowledge_base = session.get(KnowledgeBase, id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    if not current_user.is_superuser and (knowledge_base.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(knowledge_base)
    session.commit()
    return Message(message="Knowledge base deleted successfully")