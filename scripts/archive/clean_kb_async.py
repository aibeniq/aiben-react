# Clean async knowledge base creation implementation


@router.post("/", response_model=KnowledgeBaseCreateResponse)
async def create_knowledge_base(
    *,
    background_tasks: BackgroundTasks,
    session: SessionDep,
    current_user: CurrentUser,
    knowledge_base_in: KnowledgeBaseCreate = Depends(),
    files: List[UploadFile] = File(...),
) -> Any:
    """
    Create new knowledge base asynchronously with real-time progress tracking.
    Returns immediately with task_id for progress monitoring.
    """

    print(f"🚀 Starting async knowledge base creation with {len(files)} files")
    print("Received metadata:", knowledge_base_in)

    # Create progress tracking task immediately
    task_id = progress_tracker.create_task("Initializing knowledge base creation", 100)

    try:
        # Quick validation - check for existing knowledge base
        existing_kb = session.exec(
            select(KnowledgeBase).where(
                KnowledgeBase.title == knowledge_base_in.title,
                KnowledgeBase.owner_id == current_user.id,
            )
        ).first()

        if existing_kb:
            progress_tracker.fail_task(
                task_id,
                f"A knowledge base with the title '{knowledge_base_in.title}' already exists",
            )
            raise HTTPException(
                status_code=409,
                detail=f"A knowledge base with the title '{knowledge_base_in.title}' already exists",
            )

        # Create a placeholder knowledge base record immediately
        knowledge_base = KnowledgeBase(
            title=knowledge_base_in.title,
            description=knowledge_base_in.description,
            owner_id=current_user.id,
            embedding_model_id=knowledge_base_in.embedding_model_id,
            number_of_sources=0,  # Will be updated when processing completes
            total_pages=0,  # Will be updated when processing completes
        )
        session.add(knowledge_base)
        session.commit()
        session.refresh(knowledge_base)

        print(f"✅ Created placeholder knowledge base with ID: {knowledge_base.id}")
        progress_tracker.update_progress(
            task_id, 5, "Knowledge base record created, preparing files..."
        )

        # Convert files to serializable format for background processing
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append(
                {
                    "filename": file.filename,
                    "content": content,
                    "content_type": file.content_type,
                }
            )
            await file.seek(0)  # Reset file pointer

        print(f"📁 Prepared {len(file_data)} files for background processing")

        # Start background processing immediately
        background_tasks.add_task(
            process_knowledge_base_async,
            task_id=task_id,
            knowledge_base_id=knowledge_base.id,
            file_data=file_data,
            user_id=current_user.id,
            embedding_model_id=knowledge_base_in.embedding_model_id,
        )

        print(f"🔄 Started background processing for task {task_id}")

        # Return immediately with task_id for real-time progress tracking
        return KnowledgeBaseCreateResponse(
            knowledge_base=knowledge_base, task_id=task_id
        )

    except HTTPException:
        progress_tracker.fail_task(task_id, "Knowledge base creation failed")
        raise
    except Exception as e:
        progress_tracker.fail_task(task_id, f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error creating knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_knowledge_base_async(
    task_id: str,
    knowledge_base_id: uuid.UUID,
    file_data: List[dict],
    user_id: uuid.UUID,
    embedding_model_id: uuid.UUID,
):
    """
    Background task to process knowledge base creation with real-time progress tracking.
    """
    from app.core.db import engine
    from sqlmodel import Session
    from app.models import User
    from app.services.knowledgebases import chunk_documents_for_embedding
    from app.api.routes.knowledgebases import load_correct_embeddings_model, load_uploaded_file
    import tempfile
    import io
    import zipfile
    import shutil
    import asyncio

    print(f"🔄 Background processing started for task {task_id}")

    # Create a new session for background processing
    with Session(engine) as session:
        try:
            # Get the user and knowledge base
            user = session.get(User, user_id)
            knowledge_base = session.get(KnowledgeBase, knowledge_base_id)

            if not knowledge_base or not user:
                progress_tracker.fail_task(task_id, "Knowledge base or user not found")
                return

            progress_tracker.update_progress(
                task_id, 10, f"Starting file processing for {len(file_data)} files..."
            )

            # Process files
            all_documents = []
            failed_files = []

            for i, file_info in enumerate(file_data):
                try:
                    progress_pct = 10 + (i / len(file_data) * 30)  # 10% to 40%
                    progress_tracker.update_progress(
                        task_id,
                        int(progress_pct),
                        f"Processing file {i+1}/{len(file_data)}: {file_info['filename']}",
                    )

                    # Create a file-like object for processing
                    file_obj = io.BytesIO(file_info["content"])
                    file_obj.name = file_info["filename"]

                    # Create a mock UploadFile for compatibility
                    class MockUploadFile:
                        def __init__(self, file_obj, filename, content_type):
                            self.file = file_obj
                            self.filename = filename
                            self.content_type = content_type

                    mock_file = MockUploadFile(
                        file_obj, file_info["filename"], file_info["content_type"]
                    )
                    loaded_documents = load_uploaded_file(mock_file)
                    all_documents.extend(loaded_documents)
                    print(
                        f"✅ Processed {file_info['filename']}: {len(loaded_documents)} documents"
                    )

                except Exception as e:
                    failed_files.append(f"{file_info['filename']}: {str(e)}")
                    print(f"❌ Failed to process {file_info['filename']}: {e}")
                    continue

            if not all_documents:
                progress_tracker.fail_task(
                    task_id, "No documents could be processed from the uploaded files"
                )
                return

            progress_tracker.update_progress(
                task_id, 45, f"Splitting {len(all_documents)} documents..."
            )

            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.RAG_DOCUMENT_CHUNK_SIZE,
                chunk_overlap=settings.RAG_DOCUMENT_CHUNK_OVERLAP,
            )
            splits = text_splitter.split_documents(all_documents)
            print(f"Split into {len(splits)} chunks")

            progress_tracker.update_progress(
                task_id, 50, "Initializing embeddings model..."
            )

            # Load embeddings model
            embeddings, model_id, provider = load_correct_embeddings_model(
                session=session,
                current_user=user,
                embedding_model_id=embedding_model_id,
            )
            print(f"Using embedding model: {model_id}")

            # Chunk documents for embedding
            document_chunks = chunk_documents_for_embedding(
                splits, max_tokens_per_chunk=settings.EMBEDDING_MAX_TOKENS_PER_REQUEST
            )
            print(f"Split into {len(document_chunks)} chunks for embedding")

            # Create vector database with progress tracking
            chroma_dir = tempfile.mkdtemp()
            chroma_db = None

            for i, chunk in enumerate(document_chunks):
                progress_pct = 55 + (i / len(document_chunks) * 35)  # 55% to 90%
                progress_tracker.update_progress(
                    task_id,
                    int(progress_pct),
                    f"Creating embeddings: {i+1}/{len(document_chunks)}",
                )

                print(
                    f"Processing embedding chunk {i+1}/{len(document_chunks)} with {len(chunk)} documents"
                )

                if chroma_db is None:
                    chroma_db = Chroma.from_documents(
                        documents=chunk,
                        embedding=embeddings,
                        persist_directory=chroma_dir,
                    )
                else:
                    chroma_db.add_documents(documents=chunk)

                # Allow other tasks to run
                await asyncio.sleep(0.1)

            # Persist the database
            if chroma_db:
                chroma_db.persist()

            progress_tracker.update_progress(
                task_id, 92, "Compressing vector database..."
            )

            # Compress the database
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for root, _, filenames in os.walk(chroma_dir):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        arcname = os.path.relpath(file_path, chroma_dir)
                        zip_file.write(file_path, arcname)
            zip_buffer.seek(0)

            progress_tracker.update_progress(task_id, 95, "Saving to database...")

            # Update knowledge base with the results
            knowledge_base.vectordb = zip_buffer.getvalue()
            knowledge_base.number_of_sources = len(file_data) - len(failed_files)
            knowledge_base.total_pages = len(all_documents)

            session.add(knowledge_base)
            session.commit()

            # Clean up temporary directory
            if os.path.exists(chroma_dir):
                shutil.rmtree(chroma_dir)

            progress_tracker.update_progress(
                task_id, 100, "Knowledge base created successfully!"
            )

            print(
                f"✅ Successfully created knowledge base '{knowledge_base.title}' with {len(file_data)} files"
            )
            if failed_files:
                print(f"⚠️ Note: {len(failed_files)} files failed to process")

        except Exception as e:
            progress_tracker.fail_task(task_id, f"Error during processing: {str(e)}")
            logger.error(f"Background processing error: {str(e)}")
            print(f"❌ Background processing failed: {str(e)}")

            # Clean up on error - delete the placeholder knowledge base
            try:
                kb_to_delete = session.get(KnowledgeBase, knowledge_base_id)
                if kb_to_delete:
                    session.delete(kb_to_delete)
                    session.commit()
                    print(
                        f"🗑️ Cleaned up placeholder knowledge base {knowledge_base_id}"
                    )
            except Exception as cleanup_error:
                print(f"❌ Failed to clean up placeholder KB: {cleanup_error}")
