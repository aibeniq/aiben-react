import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlmodel import func, select, delete

import zipfile
import io
import os

from app.api.deps import CurrentUser, SessionDep
from app.models import KnowledgeBase, KnowledgeBaseCreate, KnowledgeBasePublic, KnowledgeBasesPublic, KnowledgeBaseUpdate, Message, Source, SourceData

import hashlib

from app.services.knowledgebases import KnowledgeBaseService

import tempfile

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

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
    
    # Get all sources for this knowledge base
    sources = session.exec(
        select(Source).where(Source.knowledge_base_id == id)
    ).all()

    # Construct the response model
    knowledge_base_public = KnowledgeBasePublic(
        **knowledge_base.model_dump(),  # Copy all fields from the KnowledgeBase object
        files=[
            {
                "id": str(source.source_data_id),  # Use source_data_id as the file ID
                "name": source.name  # Use the source name as file name
            }
            for source in sources
        ]
    )
    return knowledge_base_public


@router.post("/", response_model=KnowledgeBasePublic)
def create_knowledge_base(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    knowledge_base_in: KnowledgeBaseCreate = Depends(),
    files: List[UploadFile] = File(...),
) -> Any:
    """
    Create new knowledge base with a compressed folder with the Chroma VectorDB.
    """

    # Check if a knowledge base with this title already exists for this user
    existing_kb = session.exec(
        select(KnowledgeBase).where(
            KnowledgeBase.title == knowledge_base_in.title,
            KnowledgeBase.owner_id == current_user.id
        )
    ).first()

    print("Checking for existing knowledge base")

    if existing_kb:
        raise HTTPException(
            status_code=409,  # Using 409 Conflict for duplicate resource
            detail=f"A knowledge base with the title '{knowledge_base_in.title}' already exists"
        )
    
    # Initialize variables for Chroma
    documents = []

    # Process each file
    for file in files:
        print(f"Received file: {file}")
        print(f"Type of file: {type(file)}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            temp_file.write(file.file.read())  # Write the file content to the temporary file
            temp_file_path = temp_file.name 

        # Use TextLoader to load the file content
        text_loader = TextLoader(temp_file_path, encoding="utf-8")
        loaded_documents = text_loader.load()

        # Append loaded documents to the list
        documents.extend(loaded_documents)

         # Reset the file pointer before passing to create_source_entries
        file.file.seek(0)  

    print("Splitting documents...")

    # Split documents into chunks using RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    splits = text_splitter.split_documents(documents)

    print("Initializing embeddings...")

    # Initialize HuggingFace embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Creating Chroma VectorDB...")

    # Create Chroma VectorDB from the document splits
    Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory="./chroma_db")

    print("Zipping Chroma database...")

    # Compress the Chroma database directory into a zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, filenames in os.walk("./chroma_db"):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                arcname = os.path.relpath(file_path, "./chroma_db")  # Preserve directory structure
                zip_file.write(file_path, arcname)
    zip_buffer.seek(0)

    print("Validating knowledge base...")

    # Use model_validate to create and validate the knowledge base
    knowledge_base = KnowledgeBase.model_validate(
        knowledge_base_in,
        update={
            "owner_id": current_user.id,
            "data": zip_buffer.read()
        }
    )

    print("Adding knowledge base to session...")

    session.add(knowledge_base)

    session.flush()  # This ensures the knowledge_base.id is available

    # Process each file
    for file in files:
        print(f"Received file: {file}")
        print(f"Type of file: {type(file)}")

        KnowledgeBaseService.create_source_entries(
            session=session,
            current_user=current_user,
            knowledge_base_id=knowledge_base.id,
            file=file
        )

    session.commit()
    session.refresh(knowledge_base)
    return knowledge_base


@router.put("/{id}", response_model=KnowledgeBasePublic)
def update_knowledge_base(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    knowledge_base_in: KnowledgeBaseUpdate = Depends(),
    files: Optional[List[UploadFile]] = None,
) -> Any:
    """
    Update a knowledge base.
    """
    print("Now updating knowledge base...")
    if knowledge_base_in.removed_file_ids is None:
        knowledge_base_in.removed_file_ids = []
    print("Source IDs to remove:", knowledge_base_in.removed_file_ids)
    knowledge_base = session.get(KnowledgeBase, id)
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    if not current_user.is_superuser and (knowledge_base.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    update_dict = knowledge_base_in.model_dump(exclude_unset=True)
    knowledge_base.sqlmodel_update(update_dict)

    # Retrieve the compressed folder from the database
    if files or knowledge_base_in.removed_file_ids:
        print("Retrieving existing VectorDB...")
        zip_buffer = io.BytesIO(knowledge_base.data)
        with zipfile.ZipFile(zip_buffer, "r") as zip_file:
            zip_file.extractall("./chroma_db")

         # Load the existing Chroma VectorDB
        print("Loading existing Chroma VectorDB...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        chroma_vector_database = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

        # Process new files (if any)
        if files:
            print("Adding new files to VectorDB...")
            documents = []
            for file in files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                    temp_file.write(file.file.read())
                    temp_file_path = temp_file.name

                # Use TextLoader to load the file content
                text_loader = TextLoader(temp_file_path, encoding="utf-8")
                loaded_documents = text_loader.load()
                documents.extend(loaded_documents)

                # Reset the file pointer before passing to create_source_entries
                file.file.seek(0)

                # Add source entries for the new files
                KnowledgeBaseService.create_source_entries(
                    session=session,
                    current_user=current_user,
                    knowledge_base_id=knowledge_base.id,
                    file=file
                )

            # Add the new documents to the VectorDB
            chroma_vector_database.add_documents(documents)

        # Handle file deletions
        if knowledge_base_in.removed_file_ids is not None:
        #if len(knowledge_base_in.removed_file_ids) > 0 and knowledge_base_in.removed_file_ids[0] != "00000000-0000-0000-0000-000000000000":
            print("Removing files from VectorDB...")
            sources_to_remove = session.exec(
                select(Source).where(Source.source_data_id.in_(knowledge_base_in.removed_file_ids))
            ).all()

            print("Sources to remove:", sources_to_remove)

            for source in sources_to_remove:
                chroma_vector_database.delete(ids=[str(source.source_data_id)])

            # Delete entries from the Source table
            session.exec(
                delete(Source)
                .where(Source.source_data_id.in_(knowledge_base_in.removed_file_ids))
            )

            # Delete entries from the SourceData table
            session.exec(
                delete(SourceData)
                .where(SourceData.id.in_(knowledge_base_in.removed_file_ids))
            )

        # Zip the updated VectorDB
        print("Zipping updated VectorDB...")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, filenames in os.walk("./chroma_db"):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    arcname = os.path.relpath(file_path, "./chroma_db")
                    zip_file.write(file_path, arcname)
        zip_buffer.seek(0)

        # Update the knowledge base data in the database
        print("Updating knowledge base data in the database...")
        knowledge_base.data = zip_buffer.read()

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