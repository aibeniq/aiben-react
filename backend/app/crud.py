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


def initialize_default_embedding_models(session: Session):
    """Initialize default embedding models if they don't exist."""
    # List of default models to ensure exist (copied from modelselection.py)
    default_models = [
        {
            "name": "OpenAI Embeddings 3 Small (System Default)",
            "model_id": "text-embedding-3-small",
            "provider": ModelProvider.OPENAI,
            "description": "OpenAI's compact embedding model - system default for all users.",
        },
        {
            "name": "Amazon Titan 2.0",
            "model_id": "amazon.titan-embed-text-v2:0",
            "provider": ModelProvider.AWS,
            "description": "Amazon's Titan 2.0 embedding model for AWS Bedrock.",
        },
        {
            "name": "MiniLM-L6-v2",
            "model_id": "all-MiniLM-L6-v2",
            "provider": ModelProvider.HUGGINGFACE,
            "description": "A compact and efficient embedding model.",
        },
    ]

    def get_model_dimensions(model_id: str) -> int:
        """Get model dimensions based on known model specifications."""
        model_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
            "amazon.titan-embed-text-v2:0": 1024,
            "all-MiniLM-L6-v2": 384,
        }
        return model_dimensions.get(model_id, 768)

    for model_data in default_models:
        # Check if this default model already exists
        exists = session.exec(
            select(EmbeddingModel).where(
                EmbeddingModel.model_id == model_data["model_id"],
                EmbeddingModel.provider == model_data["provider"],
                EmbeddingModel.owner_id.is_(None),
            )
        ).first()
        if not exists:
            model = EmbeddingModel(
                name=model_data["name"],
                model_id=model_data["model_id"],
                provider=model_data["provider"],
                description=model_data["description"],
                dimensions=get_model_dimensions(model_data["model_id"]),
            )
            session.add(model)

    session.commit()


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user with default LLM and embedding model settings."""
    # Initialize default models to ensure they exist
    initialize_default_embedding_models(session)

    # Create the user object with password hash
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )

    # Get enabled providers from config
    enabled_llm_providers = settings.llm_providers
    enabled_embedding_providers = settings.embedding_providers

    # Set default LLM
    default_llm = None
    system_llms = session.exec(
        select(LlmModel).where(LlmModel.owner_id.is_(None))
    ).all()

    # If model selection is disabled, force the configured default
    if not settings.ENABLE_MODEL_SELECTION:
        for model in system_llms:
            if (
                model.model_id == settings.FORCE_DEFAULT_LLM
                and model.provider.value.lower() in enabled_llm_providers
            ):
                default_llm = model
                break
    else:
        # Normal logic - find first system LLM model with enabled provider
        for model in system_llms:
            if model.provider.value.lower() in enabled_llm_providers:
                default_llm = model
                break

    if default_llm:
        db_obj.default_llm = default_llm.id

    # Set default embedding model
    default_embedding = None
    system_embeddings = session.exec(
        select(EmbeddingModel).where(EmbeddingModel.owner_id.is_(None))
    ).all()

    # If model selection is disabled, force the configured default
    if not settings.ENABLE_MODEL_SELECTION:
        for model in system_embeddings:
            if (
                model.model_id == settings.FORCE_DEFAULT_EMBEDDING
                and model.provider.value.lower() in enabled_embedding_providers
            ):
                default_embedding = model
                break
    else:
        # Normal logic - find first system embedding model with enabled provider
        for model in system_embeddings:
            if model.provider.value.lower() in enabled_embedding_providers:
                default_embedding = model
                break

    if default_embedding:
        db_obj.default_embedding_model = default_embedding.id

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
