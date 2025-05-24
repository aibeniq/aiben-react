import enum
import uuid
from typing import List, Dict, Any, Optional
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import LargeBinary, Column, PrimaryKeyConstraint, UniqueConstraint, Enum as SQLAlchemyEnum
from datetime import datetime

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


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
    knowledge_bases: list["KnowledgeBase"] = Relationship(back_populates="owner", cascade_delete=True)


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
    embedding_model_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="embeddingmodel.id"
    )
    # New property to store file paths or URLs
    #file_paths: Optional[List[str]] = Field(default=None, sa_column_kwargs={"nullable": True})


# Properties to receive on KnowledgeBase creation
class KnowledgeBaseCreate(KnowledgeBaseBase):
    embedding_model_id: Optional[uuid.UUID] = None

# Properties to receive on KnowledgeBase update
class KnowledgeBaseUpdate(KnowledgeBaseBase):
    title: str | None = Field(default=None, min_length=1, max_length=255, unique=True)  # type: ignore
    description: str | None = Field(default=None, max_length=255)
    removed_file_ids: List[str] = Field(default_factory=list)  # List of file IDs to be removed
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
    data: bytes | None = Field(default=None, sa_column=LargeBinary)
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
    embedding_model_id: Optional[uuid.UUID] = None
    embedding_model_name: Optional[str] = Field(default=None)


class KnowledgeBasesPublic(SQLModel):
    data: list[KnowledgeBasePublic]
    count: int


# "Source" referes to a document in a knowledge base
class Source(SQLModel, table=True):
    __tablename__ = "sources"
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    source_data_id: uuid.UUID = Field(
        foreign_key="source-data.id", nullable=False
    )
    knowledge_base_id: uuid.UUID = Field(
        foreign_key="knowledge-bases.id", 
        nullable=False, 
        ondelete="CASCADE",
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", 
        nullable=False, 
        ondelete="CASCADE"
    )
    name: str = Field(max_length=255)
    date_created: datetime = Field(default_factory=datetime.utcnow)

# This stores the actual file data, not just the metadata
class SourceData(SQLModel, table=True):
    __tablename__ = "source-data"
    id: uuid.UUID = Field(primary_key=True)
    data: bytes = Field(sa_column=LargeBinary)
    file_hash: str = Field(max_length=64)  # SHA-256 hash is 64 characters
    
# Request model for FormConnect
class FormConnectRequest(SQLModel):
    fields: str

# Response model for FormConnect
class FormConnectResponse(SQLModel):
    results: Dict[str, Any]  # Accept any dictionary structure

# Form, i.e., list of form fields for FormConnect functionality
class FormConnectForm(SQLModel, table=True):
    __tablename__ = "forms"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)
    fields: str = Field(nullable=False)  # Store fields as a JSON string
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)  # Add owner_id column
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)
   
# Request model for VeraDoc
class VeraDocRequest(SQLModel):
    questions: str

# Response model for VeraDoc
class VeraDocResponse(SQLModel):
    results: Dict[str, Any]  # Accept any dictionary structure

# Form, i.e., list of questions for VeraDoc functionality
class VeraDocChecklist(SQLModel, table=True):
    __tablename__ = "questions"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, nullable=False)
    description: str | None = Field(default=None, max_length=255)
    questions: str = Field(nullable=False)  # Store questions as a JSON string
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)  # Add owner_id column
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)

class VeraDocRagQA(VeraDocRequest):
    question: str
    answer: str
    context: Optional[str] = None

class VeraDocRagResult(VeraDocRequest):
    final_evaluation: str
    qa_pairs: List[VeraDocRagQA]

class VeraDocRagResponse(VeraDocRequest):
    results: VeraDocRagResult

class RagChecklistRequest(VeraDocRequest):
    knowledge_base_id: str
    questions: str

# Enum for model providers
class ModelProvider(str, enum.Enum):
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"
    OLLAMA = "ollama"
    REPLICATE = "replicate"
    # Add other providers as needed

# Define a SQLAlchemy type for the enum
ModelProviderType = SQLAlchemyEnum(
    ModelProvider, 
    name="modelprovider",
    create_constraint=True,
    validate_strings=True,
    native_enum=True,
    values_callable=lambda x: [e.value for e in x]  # Use enum values instead of names
)

# Update the EmbeddingModel table
class EmbeddingModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)  # Human-readable name
    model_id: str  # Model identifier (e.g., "all-MiniLM-L6-v2" or "text-embedding-3-large")
    provider: ModelProvider = Field(
        default=ModelProvider.HUGGINGFACE,
        sa_column=Column(ModelProviderType, nullable=False)
    )
    description: str = Field(default="")
    is_default: bool = Field(default=False)
    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)

# Update create and update models
class EmbeddingModelCreate(SQLModel):
    name: str
    model_id: str
    provider: ModelProvider = ModelProvider.HUGGINGFACE
    description: str = ""
    is_default: bool = False

class EmbeddingModelUpdate(SQLModel):
    name: Optional[str] = None
    model_id: Optional[str] = None
    provider: Optional[ModelProvider] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None

class EmbeddingModelValidate(SQLModel):
    model_id: str
    provider: ModelProvider

class EmbeddingModelPublic(EmbeddingModel):
    pass

class EmbeddingModelsPublic(SQLModel):
    data: List[EmbeddingModelPublic]
    count: int

# Add new models for LLM settings

class LlmModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)  # Human-readable name
    model_id: str  # Model identifier (e.g., "gpt-4o-mini" or "llama3")
    provider: ModelProvider = Field(
        default=ModelProvider.OPENAI,
        sa_column=Column(ModelProviderType, nullable=False)
    )
    description: str = Field(default="")
    is_default: bool = Field(default=False)
    owner_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")
    date_created: datetime = Field(default_factory=datetime.utcnow)
    date_modified: datetime = Field(default_factory=datetime.utcnow)

class LlmModelCreate(SQLModel):
    name: str
    model_id: str
    provider: ModelProvider = ModelProvider.OPENAI
    description: str = ""
    is_default: bool = False

class LlmModelUpdate(SQLModel):
    name: Optional[str] = None
    model_id: Optional[str] = None
    provider: Optional[ModelProvider] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None

class LlmModelPublic(LlmModel):
    pass

class LlmModelsPublic(SQLModel):
    data: List[LlmModelPublic]

class LlmModelsValidate(SQLModel):
    model_id: str
    provider: ModelProvider

# Request model for ReportGenie
class ReportGenieRequest(SQLModel):
    knowledge_base_id: str
    sections: str

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