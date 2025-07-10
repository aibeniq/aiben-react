import uuid
from datetime import datetime
from typing import Any
from enum import Enum

from pydantic import EmailStr, field_validator, ValidationError
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import (
    JSON,
    LargeBinary,
    PrimaryKeyConstraint,
    UniqueConstraint,
    JSON,
)
from sqlmodel import Column, Field, Relationship, SQLModel

from app.core.config import settings
from app.services.embeddings import EmbeddingModelInfo, EmbeddingService


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
                f"Invalid embedding model ID '{v}'. Available models: "
                f"{', '.join(available_models)}"
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
                f"Invalid embedding model ID '{v}'. Available models: "
                f"{', '.join(available_models)}"
            )
        return v


# Properties to receive on KnowledgeBase creation
class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


# Properties to receive on KnowledgeBase update
class KnowledgeBaseUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255, unique=True)
    description: str | None = Field(default=None, max_length=255)
    removed_file_ids: list[str] | None = Field(
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
    files: list[dict[str, Any]] = Field(default_factory=list)
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
    data: bytes = Field(sa_type=LargeBinary)
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
    results: dict[str, Any]  # Accept any dictionary structure


class FormConnectDetailFeedback(SQLModel):
    feedback: str | None = None
    feedbackText: str | None = None
    feedbackDate: str | None = None


class FormConnectDetailResponse(SQLModel):
    id: str
    date_created: datetime
    fields: str
    file_names: list[str]
    results: dict[str, Any]
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
    results: dict[str, Any]  # Accept any dictionary structure


# Response model for VeraDoc detail endpoint
class VeraDocDetailFeedback(SQLModel):
    feedback: str | None = None
    feedbackText: str | None = None
    feedbackDate: str | None = None


class VeraDocDetailResults(SQLModel):
    final_evaluation: str
    qa_pairs: list[dict[str, Any]] = Field(default_factory=list)
    interaction_id: str


class VeraDocDetailResponse(SQLModel):
    id: str
    date_created: datetime
    document_name: str | None = None
    kb_name: str | None = None
    kb_id: str | None = None
    questions: str | None = None
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
    context: str | None = None


class VeraDocRagResult(VeraDocRequest):
    final_evaluation: str
    qa_pairs: list[VeraDocRagQA]
    interaction_id: str | None = None


class VeraDocRagResponse(VeraDocRequest):
    results: VeraDocRagResult


class RagChecklistRequest(VeraDocRequest):
    knowledge_base_id: str
    questions: str


# Request model for ReportGenie
class ReportGenieRequest(SQLModel):
    knowledge_base_id: str
    sections: str
    outline_id: str


# Metadata model for ReportGenie source citations
class ReportGenieSourceMetadata(SQLModel):
    source_id: str = ""  # Vector DB source ID
    url: str = ""  # Document URL
    title: str = ""  # Document title
    author: str = ""  # Document author


# Source citation model for ReportGenie
class ReportGenieSourceCitation(SQLModel):
    content: str
    metadata: ReportGenieSourceMetadata


# Section model for ReportGenie
class ReportGenieSection(SQLModel):
    title: str
    content: str
    source_citations: list[ReportGenieSourceCitation] = Field(default_factory=list)


# Results model for ReportGenie generation
class ReportGenieResults(SQLModel):
    full_report: str
    sections: list[ReportGenieSection] = Field(default_factory=list)


# Response model for ReportGenie generation endpoint
class ReportGenieResponse(SQLModel):
    results: ReportGenieResults


# History/summary model for ReportGenie list endpoint
class ReportGenieHistoryItem(SQLModel):
    id: str
    date_created: datetime
    title: str
    sections: str
    kb_id: str
    section_count: int
    kb_name: str
    outline_name: str
    has_feedback: bool
    feedback: dict[str, Any] | None = None
    user_name: str | None = None  # Only included when show_all=True


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
    source_citations: list[ReportGenieSourceCitation] = Field(default_factory=list)


class ReportGenieDetailFeedback(SQLModel):
    feedback: str | None = None
    feedbackText: str | None = None
    feedbackDate: str | None = None


class ReportGenieDetailResults(SQLModel):
    full_report: str
    sections: list[ReportGenieSection] = Field(default_factory=list)


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


class Tool(str, Enum):
    """Supported LLM functionalities."""

    CHATBOT = "chatbot"
    VERADOC = "veradoc"
    FORMCONNECT = "formconnect"
    REPORTGENIE = "reportgenie"
    TWINCHECK = "twincheck"


class ToolFeedback(str, Enum):
    """LLM interaction feedback options."""

    POSITIVE = "positive"
    NEGATIVE = "negative"


# Extra data types for ToolInteraction
class ToolInteractionExtraData(SQLModel):
    """Base class for LLM interaction extra data."""

    pass


class ReportGenieExtraData(ToolInteractionExtraData):
    """Extra data for ReportGenie interactions."""

    kb_name: str = ""
    kb_id: str = ""
    sections: str = ""
    outline_name: str = ""
    full_report: str = ""


class ChatbotExtraData(ToolInteractionExtraData):
    """Extra data for Chatbot interactions."""

    kb_name: str = ""
    kb_id: str = ""
    conversation_id: str | None = None


class VeradocExtraData(ToolInteractionExtraData):
    """Extra data for Veradoc interactions."""

    kb_name: str = ""
    kb_id: str = ""
    document_count: int = 0


class FormconnectExtraData(ToolInteractionExtraData):
    """Extra data for Formconnect interactions."""

    kb_name: str = ""
    kb_id: str = ""
    form_template_id: str = ""


class TwincheckExtraData(ToolInteractionExtraData):
    """Extra data for Twincheck interactions."""

    kb_name: str = ""
    kb_id: str = ""
    topic_list_id: str = ""


class ToolInteraction(SQLModel, table=True):
    """Records all interactions with LLM services for analytics and auditing."""

    __tablename__ = "tool_interactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=datetime.utcnow)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    functionality: Tool = Field(index=True)
    input_data: str | None = Field(default=None)  # Stores the input prompt/question
    output_data: str | None = Field(default=None)  # Stores the generated response
    extra_data: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSON)
    )  # For additional info (JSON)
    feedback: ToolFeedback | None = Field(default=None)
    feedback_text: str | None = Field(default=None)  # User's additional comments
    feedback_date: datetime | None = Field(default=None)  # When feedback was provided

    def get_typed_extra_data(self) -> ToolInteractionExtraData | None:
        """
        Get extra_data as a properly typed model based on functionality.

        Returns:
            Typed extra data model or None if no extra_data
        """
        if not self.extra_data:
            return None

        try:
            if self.functionality == Tool.REPORTGENIE:
                return ReportGenieExtraData(**self.extra_data)
            elif self.functionality == Tool.CHATBOT:
                return ChatbotExtraData(**self.extra_data)
            elif self.functionality == Tool.VERADOC:
                return VeradocExtraData(**self.extra_data)
            elif self.functionality == Tool.FORMCONNECT:
                return FormconnectExtraData(**self.extra_data)
            elif self.functionality == Tool.TWINCHECK:
                return TwincheckExtraData(**self.extra_data)
            else:
                # Fallback to base model for unknown functionalities
                return ToolInteractionExtraData()
        except ValidationError as e:
            # Log the validation error for debugging
            print(f"Validation error for {self.functionality}: {e}")
            return ToolInteractionExtraData()
        except Exception as e:
            # Log unexpected errors
            print(f"Unexpected error parsing extra_data for {self.functionality}: {e}")
            return ToolInteractionExtraData()

    def validate_reportgenie_data(self) -> tuple[bool, ReportGenieExtraData | None]:
        """
        Validate if extra_data can be parsed as ReportGenieExtraData.

        Returns:
            tuple: (is_valid, typed_data_or_none)
        """
        if not self.extra_data or self.functionality != Tool.REPORTGENIE:
            return False, None

        try:
            validated_data = ReportGenieExtraData(**self.extra_data)
            return True, validated_data
        except ValidationError as e:
            # Specific validation errors
            print(f"ReportGenie validation failed: {e}")
            return False, None
        except Exception as e:
            # Unexpected errors
            print(f"Unexpected error validating ReportGenie data: {e}")
            return False, None

    def is_valid_reportgenie_data(self) -> bool:
        """
        Check if this interaction has valid ReportGenie extra data.

        Returns:
            bool: True if data is valid ReportGenieExtraData
        """
        is_valid, _ = self.validate_reportgenie_data()
        return is_valid


# Request model for TwinCheck
class TwinCheckRequest(SQLModel):
    comparison_topics: str


# Response model for TwinCheck
class TwinCheckResponse(SQLModel):
    results: dict[str, Any]  # Accept any dictionary structure


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


class TwinCheckDetailFeedback(SQLModel):
    feedback: str | None = None
    feedbackText: str | None = None
    feedbackDate: str | None = None


class TwinCheckDetailResults(SQLModel):
    summary: str
    topic_analysis: list[dict[str, Any]] = Field(default_factory=list)
    interaction_id: str


class TwinCheckDetailResponse(SQLModel):
    id: str
    date_created: datetime
    document1_name: str
    document2_name: str
    comparison_topics: str
    results: TwinCheckDetailResults
    feedback: TwinCheckDetailFeedback
