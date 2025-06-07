import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.api.deps import CurrentUser, SessionDep
from app.models import Source, SourceData, KnowledgeBase, SourceContentResponse
import zipfile
from io import BytesIO
import base64
import mimetypes

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/source/{source_id}", response_model=SourceContentResponse)
async def get_source_content(
    source_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> SourceContentResponse:
    """
    Retrieve a source file by ID.
    Only returns files that the user has access to (either owns or has permissions for).
    """
    try:
        # Find the source data
        source_data = session.get(SourceData, source_id)

        if not source_data:
            raise HTTPException(status_code=404, detail="Source file not found")

        # Check if current user has access to this file
        # Either through a source they own or a knowledge base they have access to
        source = session.exec(
            select(Source)
            .where(Source.source_data_id == source_id)
            .where(Source.owner_id == current_user.id)
        ).first()

        if not source and not current_user.is_superuser:
            # If not direct owner, check if they have access to any knowledge base containing this source
            kb_access = session.exec(
                select(KnowledgeBase)
                .join(Source, KnowledgeBase.id == Source.knowledge_base_id)
                .where(Source.source_data_id == source_id)
                .where(KnowledgeBase.owner_id == current_user.id)
            ).first()

            if not kb_access:
                raise HTTPException(
                    status_code=403,
                    detail="You don't have permission to access this file",
                )

        # Get source name from the first associated Source (just for display)
        file_source = session.exec(
            select(Source).where(Source.source_data_id == source_id)
        ).first()
        file_name = file_source.name if file_source else f"file-{source_id}.txt"

        # Extract the file content from the ZIP
        zip_data = BytesIO(source_data.data)
        with zipfile.ZipFile(zip_data, "r") as zip_file:
            # Get the first file in the archive
            file_info = zip_file.infolist()[0]
            file_content = zip_file.read(file_info.filename)

            # Determine content type
            content_type = (
                mimetypes.guess_type(file_name)[0] or "application/octet-stream"
            )

            # Base64 encode for transmission
            content_base64 = base64.b64encode(file_content).decode("utf-8")

            return {
                "id": str(source_id),
                "name": file_name,
                "data_base64": content_base64,
                "content_type": content_type,
            }

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving file: {str(e)}")
