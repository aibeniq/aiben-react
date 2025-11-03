import uuid
from typing import Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    LanguageUpdate,
    VisionAnalysisUpdate,
    PdfParsingPreferenceUpdate,
    UserStatus,
)
from app.utils.email_utils import (
    generate_new_account_email,
    send_email,
    generate_admin_approval_email,
    send_admin_approval_email,
    generate_approval_token,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/supported-languages")
def get_supported_languages() -> Any:
    """Get the list of supported languages for translation."""
    return {"languages": settings.SUPPORTED_LANGUAGES}


@router.put("/me/language", response_model=User)
def update_language(
    language_update: LanguageUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update current user language preference."""

    # Validate the language code
    if language_update.preferred_language not in settings.SUPPORTED_LANGUAGES:
        supported_codes = list(settings.SUPPORTED_LANGUAGES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Language not supported. Choose from: {', '.join(supported_codes)}",
        )

    # Update user's language preference
    user = session.get(User, current_user.id)
    user.preferred_language = language_update.preferred_language
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.put("/me/vision-analysis", response_model=User)
def update_vision_analysis_setting(
    vision_update: VisionAnalysisUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update current user's vision analysis preference."""

    # Update user's vision analysis preference
    user = session.get(User, current_user.id)
    user.vision_analysis_enabled = vision_update.vision_analysis_enabled
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.put("/me/pdf-parsing-preference", response_model=UserPublic)
def update_pdf_parsing_preference(
    parsing_update: PdfParsingPreferenceUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Update current user's PDF parsing preference."""

    # Validate mode
    valid_modes = ["enhanced", "basic"]
    if parsing_update.pdf_parsing_preference not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid parsing mode. Must be one of: {', '.join(valid_modes)}",
        )

    # Update user's PDF parsing preference
    user = session.get(User, current_user.id)
    user.pdf_parsing_preference = parsing_update.pdf_parsing_preference
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(
    session: SessionDep,
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=Message)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        if user.status == UserStatus.PENDING:
            raise HTTPException(status_code=400, detail="Registration pending approval")
        else:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system",
            )

    # Create user in pending state
    user_create = UserCreate.model_validate(user_in)
    user_create.status = UserStatus.PENDING
    user_create.is_active = False  # Ensure pending users can't log in
    user = crud.create_user(session=session, user_create=user_create)

    # Generate approval token
    approval_token = generate_approval_token(str(user.email), str(user.id))

    # Send admin notification email
    if settings.emails_enabled and settings.REQUIRE_ADMIN_APPROVAL:
        send_admin_approval_email(
            user_email=user.email,
            user_name=user.full_name or user.email,
            approval_token=approval_token,
        )

    return Message(message="Registration submitted. Awaiting admin approval.")


@router.post("/approve-registration/{token}", response_model=Message)
def approve_registration(token: str, session: SessionDep) -> Any:
    """
    Approve a pending user registration.
    Admin-only endpoint (accessed via email link).
    """
    from app.utils.email_utils import verify_approval_token

    # Verify and decode token
    user_data = verify_approval_token(token)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Get pending user
    user = session.get(User, user_data["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.status != UserStatus.PENDING:
        raise HTTPException(status_code=400, detail="User already processed")

    # Activate user
    user.status = UserStatus.ACTIVE
    user.is_active = True
    user.approved_date = datetime.utcnow()
    # Optional: track which admin approved
    # user.approved_by = current_admin_user.id

    session.add(user)
    session.commit()

    # Send welcome email to user
    if settings.emails_enabled:
        from app.utils.email_utils import send_registration_approved_email

        send_registration_approved_email(
            email_to=user.email, full_name=user.full_name or user.email
        )

    # Return success page or redirect
    return Message(message=f"User {user.email} has been successfully approved.")


@router.post("/reject-registration/{token}", response_model=Message)
def reject_registration(token: str, session: SessionDep) -> Any:
    """Reject and delete a pending registration."""
    from app.utils.email_utils import verify_approval_token

    user_data = verify_approval_token(token)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = session.get(User, user_data["user_id"])
    if user and user.status == UserStatus.PENDING:
        session.delete(user)
        session.commit()
        return Message(message="Registration rejected and user deleted")

    raise HTTPException(status_code=400, detail="Invalid request")


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
