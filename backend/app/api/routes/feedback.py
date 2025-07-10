import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlmodel import select, func

from app.api.deps import SessionDep, CurrentUser
from app.models import (
    Feedback,
    FeedbackCreate,
    FeedbackUpdate,
    FeedbackPublic,
    FeedbacksPublic,
    FeedbackAdminUpdate,
    FeedbackImage,
    FeedbackImageResponse,
    FeedbackType,
    FeedbackStatus,
    Message,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackPublic)
async def create_feedback(
    session: SessionDep,
    current_user: CurrentUser,
    title: str = Form(..., min_length=1, max_length=255),
    description: str = Form(..., min_length=1, max_length=2000),
    feedback_type: FeedbackType = Form(...),
    images: list[UploadFile] | None = File(None),
) -> FeedbackPublic:
    """Create a new feedback submission with optional images."""

    # create feedback object
    feedback_data = FeedbackCreate(
        title=title,
        description=description,
        feedback_type=feedback_type,
        has_images=bool(images),
    )

    # create feedback in database
    feedback = Feedback(**feedback_data.model_dump(), user_id=current_user.id)

    session.add(feedback)
    session.commit()
    session.refresh(feedback)

    # handle image uploads if provided
    if images:
        for image_file in images:
            # validate file type
            if not image_file.content_type or not image_file.content_type.startswith(
                "image/"
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {image_file.filename} is not a valid image",
                )

            # read file data
            image_data = await image_file.read()

            # validate file size (10MB limit)
            if len(image_data) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {image_file.filename} is too large. Maximum size is 10MB",
                )

            # create feedback image
            feedback_image = FeedbackImage(
                feedback_id=feedback.id,
                filename=image_file.filename or "unknown.jpg",
                content_type=image_file.content_type,
                data=image_data,
                file_size=len(image_data),
            )

            session.add(feedback_image)

        session.commit()

    feedback_with_images = session.exec(
        select(Feedback).where(Feedback.id == feedback.id)
    ).one()

    # return feedback with image count
    return FeedbackPublic(
        **feedback_with_images.model_dump(),
        image_count=(
            len(feedback_with_images.images) if feedback_with_images.images else 0
        ),
    )


@router.get("/", response_model=FeedbacksPublic)
async def get_feedbacks(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    feedback_type: str | None = None,
    status: str | None = None,
) -> FeedbacksPublic:
    """Get feedback submissions with optional filtering."""

    # build base query
    base_query = select(Feedback).where(Feedback.user_id == current_user.id)

    # apply filters
    if feedback_type:
        try:
            feedback_type_enum = FeedbackType(feedback_type)
            base_query = base_query.where(Feedback.feedback_type == feedback_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid feedback type. Must be one of: {[t.value for t in FeedbackType]}",
            )

    if status:
        try:
            status_enum = FeedbackStatus(status)
            base_query = base_query.where(Feedback.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[s.value for s in FeedbackStatus]}",
            )

    # get total count by building the same query conditions
    count_query = select(func.count()).where(Feedback.user_id == current_user.id)

    if feedback_type:
        try:
            feedback_type_enum = FeedbackType(feedback_type)
            count_query = count_query.where(
                Feedback.feedback_type == feedback_type_enum
            )
        except ValueError:
            pass  # already validated above

    if status:
        try:
            status_enum = FeedbackStatus(status)
            count_query = count_query.where(Feedback.status == status_enum)
        except ValueError:
            pass  # already validated above

    total_count = session.exec(count_query).one()

    # apply pagination
    feedbacks = session.exec(base_query.offset(skip).limit(limit)).all()

    # convert to public models with image counts
    feedback_publics = []
    for feedback in feedbacks:
        feedback_publics.append(
            FeedbackPublic(
                **feedback.model_dump(),
                image_count=len(feedback.images) if feedback.images else 0,
            )
        )

    return FeedbacksPublic(data=feedback_publics, count=total_count)


@router.get("/{feedback_id}", response_model=FeedbackPublic)
async def get_feedback(
    session: SessionDep,
    current_user: CurrentUser,
    feedback_id: uuid.UUID,
) -> FeedbackPublic:
    """Get a specific feedback submission."""
    feedback = session.get(Feedback, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # check if user owns this feedback or is admin
    if feedback.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this feedback"
        )

    return FeedbackPublic(
        **feedback.model_dump(),
        image_count=len(feedback.images) if feedback.images else 0,
    )


@router.put("/{feedback_id}", response_model=FeedbackPublic)
async def update_feedback(
    session: SessionDep,
    current_user: CurrentUser,
    feedback_id: uuid.UUID,
    feedback_update: FeedbackUpdate,
) -> FeedbackPublic:
    """Update a feedback submission."""
    feedback = session.get(Feedback, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # check if user owns this feedback
    if feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this feedback"
        )

    # only allow updates if feedback is still open
    if feedback.status.value != FeedbackStatus.OPEN:
        raise HTTPException(
            status_code=400, detail="Cannot update feedback that is not open"
        )

    # update fields
    update_data = feedback_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)

    feedback.date_modified = datetime.now(timezone.utc)

    session.add(feedback)
    session.commit()
    session.refresh(feedback)

    return FeedbackPublic(
        **feedback.model_dump(),
        image_count=len(feedback.images) if feedback.images else 0,
    )


@router.delete("/{feedback_id}", response_model=Message)
async def delete_feedback(
    session: SessionDep,
    current_user: CurrentUser,
    feedback_id: uuid.UUID,
) -> Message:
    """Delete a feedback submission."""
    feedback = session.get(Feedback, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # check if user owns this feedback
    if feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this feedback"
        )

    # only allow deletion if feedback is still open
    if feedback.status.value != "open":
        raise HTTPException(
            status_code=400, detail="Cannot delete feedback that is not open"
        )

    session.delete(feedback)
    session.commit()

    return Message(message="Feedback deleted successfully")


@router.get("/{feedback_id}/images", response_model=list[FeedbackImageResponse])
async def get_feedback_images(
    session: SessionDep,
    current_user: CurrentUser,
    feedback_id: uuid.UUID,
) -> list[FeedbackImageResponse]:
    """Get all images for a specific feedback submission."""
    feedback = session.get(Feedback, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # check if user owns this feedback or is admin
    if feedback.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this feedback"
        )

    images = session.exec(
        select(FeedbackImage).where(FeedbackImage.feedback_id == feedback_id)
    ).all()

    return [
        FeedbackImageResponse(
            id=image.id,
            filename=image.filename,
            content_type=image.content_type,
            file_size=image.file_size,
            date_uploaded=image.date_uploaded,
        )
        for image in images
    ]


@router.get("/{feedback_id}/images/{image_id}")
async def get_feedback_image(
    session: SessionDep,
    current_user: CurrentUser,
    feedback_id: uuid.UUID,
    image_id: uuid.UUID,
) -> Response:
    """Get a specific image for a feedback submission."""

    feedback = session.get(Feedback, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # check if user owns this feedback or is admin
    if feedback.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Not authorized to view this feedback"
        )

    image = session.get(FeedbackImage, image_id)

    if not image or image.feedback_id != feedback_id:
        raise HTTPException(status_code=404, detail="Image not found")

    return Response(
        content=image.data,
        media_type=image.content_type,
        headers={"Content-Disposition": f"inline; filename={image.filename}"},
    )


# admin-only endpoints
@router.get("/admin/all", response_model=FeedbacksPublic)
async def get_all_feedbacks_admin(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    feedback_type: str | None = None,
    status: str | None = None,
    user_id: uuid.UUID | None = None,
) -> FeedbacksPublic:
    """Get all feedback submissions (admin only)."""
    from app.models import FeedbackType, FeedbackStatus

    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    # build base query
    base_query = select(Feedback)

    # apply filters
    if feedback_type:
        try:
            feedback_type_enum = FeedbackType(feedback_type)
            base_query = base_query.where(Feedback.feedback_type == feedback_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid feedback type. Must be one of: {[t.value for t in FeedbackType]}",
            )

    if status:
        try:
            status_enum = FeedbackStatus(status)
            base_query = base_query.where(Feedback.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[s.value for s in FeedbackStatus]}",
            )

    if user_id:
        base_query = base_query.where(Feedback.user_id == user_id)

    # get total count by building the same query conditions
    count_query = select(func.count())

    if feedback_type:
        try:
            feedback_type_enum = FeedbackType(feedback_type)
            count_query = count_query.where(
                Feedback.feedback_type == feedback_type_enum
            )
        except ValueError:
            pass  # already validated above

    if status:
        try:
            status_enum = FeedbackStatus(status)
            count_query = count_query.where(Feedback.status == status_enum)
        except ValueError:
            pass  # already validated above

    if user_id:
        count_query = count_query.where(Feedback.user_id == user_id)

    total_count = session.exec(count_query).one()

    # apply pagination
    feedbacks = session.exec(base_query.offset(skip).limit(limit)).all()

    # convert to public models with image counts
    feedback_publics = []
    for feedback in feedbacks:
        feedback_publics.append(
            FeedbackPublic(
                **feedback.model_dump(),
                image_count=len(feedback.images) if feedback.images else 0,
            )
        )

    return FeedbacksPublic(data=feedback_publics, count=total_count)


@router.put("/admin/{feedback_id}", response_model=FeedbackPublic)
async def update_feedback_admin(
    session: SessionDep,
    current_user: CurrentUser,
    feedback_id: uuid.UUID,
    admin_update: FeedbackAdminUpdate,
) -> FeedbackPublic:
    """Update feedback status and admin notes (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")

    feedback = session.get(Feedback, feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    # update admin fields
    update_data = admin_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)

    feedback.date_modified = datetime.now(timezone.utc)

    session.add(feedback)
    session.commit()
    session.refresh(feedback)

    return FeedbackPublic(
        **feedback.model_dump(),
        image_count=len(feedback.images) if feedback.images else 0,
    )
