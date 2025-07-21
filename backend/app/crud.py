import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserUpdate,
    LlmModel,
    EmbeddingModel,
    ModelProvider,
)
from app.core.config import settings


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user with default LLM and embedding model settings."""
    
    # Initialize default models first (ensure they exist in database)
    from app.api.routes.modelselection import initialize_default_models
    from app.api.routes.llms import initialize_default_llm_models
    
    initialize_default_models(session)
    initialize_default_llm_models(session)
    
    # Create the user object with password hash
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )

    # Get enabled providers from config
    enabled_llm_providers = settings.llm_providers
    enabled_embedding_providers = settings.embedding_providers

    # Set default LLM - specifically assign gpt-4o-mini from OpenAI
    default_llm = session.exec(
        select(LlmModel).where(
            LlmModel.model_id == "gpt-4o-mini",
            LlmModel.provider == ModelProvider.OPENAI,
            LlmModel.owner_id.is_(None)
        )
    ).first()

    if default_llm and "openai" in enabled_llm_providers:
        db_obj.default_llm = default_llm.id

    # Set default embedding model - specifically assign text-embedding-3-small from OpenAI
    default_embedding = session.exec(
        select(EmbeddingModel).where(
            EmbeddingModel.model_id == "text-embedding-3-small",
            EmbeddingModel.provider == ModelProvider.OPENAI,
            EmbeddingModel.owner_id.is_(None)
        )
    ).first()

    if default_embedding and "openai" in enabled_embedding_providers:
        db_obj.default_embedding_model = default_embedding.id
    else:
        # Fallback: try to find any OpenAI embedding model if the specific one isn't found
        if "openai" in enabled_embedding_providers:
            any_openai_embedding = session.exec(
                select(EmbeddingModel).where(
                    EmbeddingModel.provider == ModelProvider.OPENAI,
                    EmbeddingModel.owner_id.is_(None)
                )
            ).first()
            if any_openai_embedding:
                db_obj.default_embedding_model = any_openai_embedding.id
                print(f"Using fallback OpenAI embedding model: {any_openai_embedding.model_id}")
            else:
                print("Warning: No OpenAI embedding models found in database despite being enabled")

    # Save the user with default models
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
