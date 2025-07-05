import enum
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import EmailStr, field_validator
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import (
    LargeBinary,
    Column,
    PrimaryKeyConstraint,
    UniqueConstraint,
    Enum as SQLAlchemyEnum,
    JSON,
)

from app.services.embeddings import EmbeddingModelInfo, EmbeddingService
from app.core.config import settings


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    default_embedding_model: str = Field(
        default_factory=lambda: EmbeddingService.get_default_model().id, max_length=100
    )
    default_llm: str = Field(
        default_factory=lambda: settings.DEFAULT_LLM_MODEL, max_length=100
    )

    @field_validator("default_embedding_model")
    @classmethod
    def validate_embedding_model(cls, v: str) -> str:
        if not EmbeddingService.is_valid_model_id(v):
            available_models = EmbeddingService.get_model_ids()
            raise ValueError(
                f"Invalid embedding model ID '{v}'. Available models: {', '.join(available_models)}"
            )
        return v


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    knowledge_bases: list["KnowledgeBase"] = Relationship(
        back_populates="owner", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# classes for Knowledge Bases
# Shared properties
class KnowledgeBaseBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    embedding_model_id: str = Field(
        default_factory=lambda: EmbeddingService.get_default_model().id, max_length=100
    )

    @field_validator("embedding_model_id")
    @classmethod
    def validate_embedding_model(cls, v: str) -> str:
        if not EmbeddingService.is_valid_model_id(v):
            available_models = EmbeddingService.get_model_ids()
            raise ValueError(
                f"Invalid embedding model ID '{v}'. Available models: {', '.join(available_models)}"
            )
        return v


# Properties to receive on KnowledgeBase creation
class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


# Properties to receive on KnowledgeBase update
class KnowledgeBaseUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255, unique=True)  # type: ignore
    description: str | None = Field(default=None, max_length=255)
    removed_file_ids: List[str] | None = Field(
        default=None
    )  # List of file IDs to be removed (optional)
    # Allow updating file paths
    # file_paths: Optional[List[str]] = None


# Then add a table constraint in KnowledgeBase
class KnowledgeBase(KnowledgeBaseBase, table=True):
    __tablename__ = "knowledge-bases"
    # Add a unique constraint across title and owner_id
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        UniqueConstraint("title", "owner_id", name="uq_knowledgebase_title_owner"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="knowledge_bases")
    date_created: datetime
    date_modified: datetime


# Properties to return via API, id is always required
class KnowledgeBasePublic(KnowledgeBaseBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    files: List[dict] = Field(default_factory=list)
    date_created: datetime
    date_modified: datetime
    number_of_sources: int = Field(default=0)
    embedding_model: EmbeddingModelInfo


class KnowledgeBasesPublic(SQLModel):
    data: list[KnowledgeBasePublic]
    count: int


# "Source" referes to a document in a knowledge base
class Source(SQLModel, table=True):
    __tablename__ = "sources"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    source_data_id: uuid.UUID = Field(foreign_key="source-data.id", nullable=False)
    knowledge_base_id: uuid.UUID = Field(
        foreign_key="knowledge-bases.id",
        nullable=False,
        ondelete="CASCADE",
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    name: str = Field(max_length=255)
    date_created: datetime = Field(default_factory=datetime.utcnow)


# This stores the actual file data, not just the metadata
class SourceData(SQLModel, table=True):
    __tablename__ = "source-data"
    id: uuid.UUID = Field(primary_key=True)
    data: bytes = Field(sa_column=LargeBinary)
    file_hash: str = Field(max_length=64)  # SHA-256 hash is 64 characters


# Response model for source content retrieval
class SourceContentResponse(SQLModel):
    id: str
    name: str
    data_base64: str
    content_type: str


# Request model for FormConnect
class FormConnectRequest(SQLModel):
    fields: str


# Response model for FormConnect
class FormConnectResponse(SQLModel):
    results: Dict[str, Any]  # Accept any dictionary structure


class FormConnectDetailFeedback(SQLModel):
    feedback: Optional[str] = None
    feedbackText: Optional[str] = None
    feedbackDate: Optional[str] = None


class FormConnectDetailResponse(SQLModel):
    id: str
    date_created: datetime
    fields: str
    file_names: List[str]
    results: Dict[str, Any]
    feedback: FormConnectDetailFeedback


# Form, i.e., list of form fields for FormConnect functionality
class FormConnectForm(SQLModel, table=True):
    __tablename__ = "forms"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)
    fields: str = Field(nullable=False)  # Store fields as a JSON string
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )  # Add owner_id column
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


# Request model for VeraDoc
class VeraDocRequest(SQLModel):
    questions: str


# Response model for VeraDoc
class VeraDocResponse(SQLModel):
    results: Dict[str, Any]  # Accept any dictionary structure


# Response model for VeraDoc detail endpoint
class VeraDocDetailFeedback(SQLModel):
    feedback: Optional[str] = None
    feedbackText: Optional[str] = None
    feedbackDate: Optional[str] = None


class VeraDocDetailResults(SQLModel):
    final_evaluation: str
    qa_pairs: List[Dict[str, Any]] = Field(default_factory=list)
    interaction_id: str


class VeraDocDetailResponse(SQLModel):
    id: str
    date_created: datetime
    document_name: Optional[str] = None
    kb_name: Optional[str] = None
    kb_id: Optional[str] = None
    questions: Optional[str] = None
    results: VeraDocDetailResults
    feedback: VeraDocDetailFeedback


# Form, i.e., list of questions for VeraDoc functionality
class VeraDocChecklist(SQLModel, table=True):
    __tablename__ = "questions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)
    questions: str = Field(nullable=False)  # Store questions as a JSON string
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False
    )  # Add owner_id column
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


class VeraDocRagQA(VeraDocRequest):
    question: str
    answer: str
    context: Optional[str] = None


class VeraDocRagResult(VeraDocRequest):
    final_evaluation: str
    qa_pairs: List[VeraDocRagQA]
    interaction_id: Optional[str] = None


class VeraDocRagResponse(VeraDocRequest):
    results: VeraDocRagResult


class RagChecklistRequest(VeraDocRequest):
    knowledge_base_id: str
    questions: str


# Enum for LLM providers (embeddings handled by embedding service)
class LlmProvider(str, enum.Enum):
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    OLLAMA = "ollama"
    REPLICATE = "replicate"
    AWS = "aws"
    # Add other providers as needed


# Define a SQLAlchemy type for the enum
LlmProviderType = SQLAlchemyEnum(
    LlmProvider,
    name="llmprovider",
    create_constraint=True,
    validate_strings=True,
    native_enum=True,
    values_callable=lambda x: [e.value for e in x],  # Use enum values instead of names
)


class LlmModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)  # Human-readable name
    model_id: str  # Model identifier (e.g., "gpt-4o-mini" or "llama3")
    provider: LlmProvider = Field(
        default=LlmProvider.OPENAI,
        sa_column=Column(LlmProviderType, nullable=False),
    )
    description: str = Field(default="")
    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


class LlmModelCreate(SQLModel):
    name: str
    model_id: str
    provider: LlmProvider = LlmProvider.OPENAI
    description: str = ""


class LlmModelUpdate(SQLModel):
    name: Optional[str] = None
    model_id: Optional[str] = None
    provider: Optional[LlmProvider] = None
    description: Optional[str] = None


class LlmModelPublic(LlmModel):
    pass


class LlmModelsPublic(SQLModel):
    data: List[LlmModelPublic]


class LlmModelsValidate(SQLModel):
    model_id: str
    provider: LlmProvider


# Request model for ReportGenie
class ReportGenieRequest(SQLModel):
    knowledge_base_id: str
    sections: str
    outline_id: str


# Response model for ReportGenie
class ReportGenieResponse(SQLModel):
    results: Dict[str, Any]  # Accept any dictionary structure


# Form for saving outlines
class ReportGenieOutline(SQLModel, table=True):
    __tablename__ = "reportgenie_outlines"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)
    sections: str = Field(nullable=False)  # Store sections outline as a string
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


class ReportGenieSection(SQLModel):
    title: str
    content: str
    source_citations: List[Dict[str, Any]] = Field(default_factory=list)


class ReportGenieDetailFeedback(SQLModel):
    feedback: Optional[str] = None
    feedbackText: Optional[str] = None
    feedbackDate: Optional[str] = None


class ReportGenieDetailResults(SQLModel):
    full_report: str
    sections: List[Dict[str, Any]] = Field(default_factory=list)


class ReportGenieDetailResponse(SQLModel):
    id: str
    date_created: datetime
    kb_name: str
    kb_id: str
    sections: str
    results: ReportGenieDetailResults
    feedback: ReportGenieDetailFeedback


class DocxRequest(SQLModel):
    content: str


class LlmInteraction(SQLModel, table=True):
    """Records all interactions with LLM services for analytics and auditing."""

    __tablename__ = "llm_interactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    functionality: str = Field(
        index=True
    )  # 'chatbot', 'veradoc', 'formconnect', 'reportgenie'
    input_data: str = Field(default=None)  # Stores the input prompt/question
    output_data: str = Field(default=None)  # Stores the generated response
    extra_data: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )  # For additional info (JSON)
    feedback: Optional[str] = Field(default=None)  # 'correct' or 'incorrect'
    feedback_text: Optional[str] = Field(default=None)  # User's additional comments
    feedback_date: Optional[datetime] = Field(
        default=None
    )  # When feedback was provided


# Request model for TwinCheck
class TwinCheckRequest(SQLModel):
    comparison_topics: str


# Response model for TwinCheck
class TwinCheckResponse(SQLModel):
    results: Dict[str, Any]  # Accept any dictionary structure


# Table for saved comparison topic sets
class TwinCheckTopicList(SQLModel, table=True):
    __tablename__ = "twincheck_comparisons"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)
    topics: str = Field(nullable=False)  # Store topics as a newline-separated string
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)


class TwinCheckRequest(SQLModel):
    comparison_topics: str


class TwinCheckDetailFeedback(SQLModel):
    feedback: Optional[str] = None
    feedbackText: Optional[str] = None
    feedbackDate: Optional[str] = None


class TwinCheckDetailResults(SQLModel):
    summary: str
    topic_analysis: List[Dict[str, Any]] = Field(default_factory=list)
    interaction_id: str


class TwinCheckDetailResponse(SQLModel):
    id: str
    date_created: datetime
    document1_name: str
    document2_name: str
    comparison_topics: str
    results: TwinCheckDetailResults
    feedback: TwinCheckDetailFeedback
