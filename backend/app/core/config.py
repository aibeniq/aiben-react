import os
import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

"""
Should I put this in here or the .env file?

🏗️ This file (config.py) should contain:
- Default values with type annotations
- Validation logic and business rules
- Computed fields and derived values
- Configuration schema and structure
- Static business logic (prompt templates, etc.)

📁 The .env file should contain:
- Environment-specific values (URLs, domains, hosts)
- Secrets and credentials (API keys, passwords, tokens)
- Deployment-specific settings (database connection info)
- Runtime overrides for the defaults defined here
"""


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    # Document processing parameters
    DOCUMENT_CHUNK_SIZE: int = 1000
    DOCUMENT_CHUNK_OVERLAP: int = 200

    # Default embedding model configuration
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Default LLM model configuration
    DEFAULT_LLM_MODEL: str = "gpt-4o-mini"

    # Application configuration (can be overridden in .env)
    PROJECT_NAME: str = "aibenIQ"
    STACK_NAME: str = "aibeniq"

    # LLM Provider configuration
    ENABLED_LLM_PROVIDERS: str = "openai,aws"

    # External service configuration
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    AWS_REGION: str = "eu-north-1"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    SENTRY_DSN: HttpUrl | None = None
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: EmailStr | None = None

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    @computed_field
    @property
    def llm_providers(self) -> list[str]:
        """Return list of enabled LLM providers"""
        return [provider.strip() for provider in self.ENABLED_LLM_PROVIDERS.split(",")]

    # LLM Templates
    REPORT_GENIE_PROMPT_TEMPLATE: str = """
    REFERENCE INFORMATION:
    {context}

    TASK:
    Based on the reference information above, write a clear and comprehensive section for a research participation consent form. The section to create is: {question}

    The content should:
    1. Be written in plain language (8th-grade reading level)
    2. Include all legally required elements for this section
    3. Follow standard consent form conventions
    4. Be concise yet thorough
    5. Use second-person perspective (addressing "you" - the participant)

    FORMAT OUTPUT AS A PROPERLY FORMATTED CONSENT FORM SECTION with an appropriate heading and content.

    SECTION CONTENT:
    """

    VERADOC_CONTEXT_PROMPT_TEMPLATE: str = """
    CONTEXT:
    {context}
    
    INSTRUCTION: 
    What necessary information from the context above should be kept in mind when answering the following question? {question} 
    ONLY INCLUDE POLICY INFORMATION THAT WOULD BE SPECIFICALLY PERTINENT TO THE QUESTION -- do NOT just repeat general requirements.
    
    ANSWER:
    According to the policy context, the following should be kept in mind when answering the question:
    """

    # VERADOC_QA_PROMPT_TEMPLATE: str = """
    # Read the following document and answer the following question clearly and concisely in 100 words or less.
    #
    # SAMPLE DOCUMENT: {document_text}
    #
    # QUESTION: {question}
    #
    # Keep the following RELEVANT REQUIREMENTS in mind when answering the question:
    # {question_context}
    #
    # ANSWER:
    # """

    VERADOC_QA_PROMPT_TEMPLATE: str = """
        Read the following document and answer the question below clearly and concisely in 100 words or less.

        When answering, assess whether the document provides *explicit and verifiable evidence* that the relevant requirements are fully met. Do **not** assume compliance based on general statements or references (e.g., to Good Clinical Practice or regulatory standards) unless the document clearly explains how the requirements are operationalized.

        If the document does not contain sufficient detail to confirm that a requirement is met, state that the information is insufficient, even if the requirement is mentioned.

        SAMPLE DOCUMENT:
        {document_text}

        QUESTION:
        {question}

        RELEVANT REQUIREMENTS:
        {question_context}

        ANSWER:
    """

    VERADOC_FINAL_PROMPT_TEMPLATE: str = """
    According to policy, an acceptable document must have all of the elements described in the following questions.
    Read the following question-and-answer pairs about a certain proposal and determine whether or not it conforms to the policy.
    
    Remember: if any single element is missing from the proposal, it automatically means that the entire proposal does NOT conform to policy.
    If the plan does not conform to policy, explain why not.
    
    {qa_pairs}
    
    Based on the question-and-answer pairs above, does the plan follow policy?
    """

    FORMCONNECT_DIGITIZED_PROMPT_TEMPLATE: str = """
    Here is a template of the fields that I want you to extract from this document: {template}
    Here is the full text of a document: {document_text}
    Fill out the template based on the fields you can find.
    """

    FORMCONNECT_HANDWRITTEN_PROMPT_TEMPLATE: str = """
    Here is a template of the fields that I want you to extract from this image: {template}

    I'm sending you an image with handwritten content.

    For each field in the template, try to locate and extract the corresponding value from the image.
    Pay special attention to handwritten text and ensure accuracy in your extraction.

    Return your results as a JSON object matching the template structure.
    """

    FORMCONNECT_COMPARISON_PROMPT_TEMPLATE: str = """
    I am going to show you information extracted from multiple documents:

    {documents_str}

    Please analyze all the documents and identify any fields that have different values across documents.

    Create a markdown table with the following format:
    1. First column should be titled "FIELD" and contain the field name
    2. Each additional column should have the document name as header (e.g., "Document 1", "Document 2")
    3. Include ONLY fields where there are discrepancies between documents

    After the table, please:
    1. For each discrepancy, suggest which value is most likely correct and why
    2. Provide a summary of how consistent the documents are overall

    Example format:
    ```markdown
    | FIELD | Document 1 | Document 2 | ... |
    |-------|------------|------------|-----|
    | Name  | John Smith | J. Smith   | ... |
    | Date  | 2023-01-01 | 2023-01-15 | ... |
    ```

    ONLY return the Markdown table -- do NOT return any other text. 
    Also, do NOT add tick marks like ``` and the label 'markdown': just give the actual markdown table content as raw text.
    However, if there are no discrepancies, please state that all fields match across documents.
    """

    CHATBOT_REPHRASING_PROMPT_TEMPLATE: str = """
    You are an AI that rephrases the user's latest question to incorporate relevant context from the conversation history.
    
    CONVERSATION HISTORY:
    {chat_history}
    
    CURRENT QUESTION: {question}
    
    INSTRUCTIONS:
    1. Analyze the conversation history and the current question.
    2. Rewrite the current question to be self-contained, incorporating any relevant context.
    3. The rephrased question should be answerable without needing to see the conversation history.
    4. Return ONLY the rephrased question, nothing else.
    5. If the current question is already self-contained and doesn't reference anything from the history, return it unchanged.
    
    REPHRASED QUESTION:
    """

    CHATBOT_KB_QA_PROMPT_TEMPLATE: str = """
    You are a helpful assistant that answers questions based on the provided context.
    
    CONTEXT:
    {context}
    
    QUESTION: {question}
    
    INSTRUCTIONS:
    1. Answer the question based ONLY on the information provided in the CONTEXT.
    2. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer this question."
    3. Be concise and to the point.
    4. Don't make up information or use knowledge outside the provided context.
    
    ANSWER:
    """

    CHATBOT_GENERAL_QA_PROMPT_TEMPLATE: str = """
    You are a helpful AI assistant. Answer the following question to the best of your knowledge.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    QUESTION: {question}

    ANSWER:
    """

    # TwinCheck prompt templates
    TWINCHECK_ANALYSIS_PROMPT_TEMPLATE: str = """
    You are comparing two documents using their diff output:
    - Document 1: {doc1_name}
    - Document 2: {doc2_name}
    
    In the diff output below:
    - Lines starting with '- ' are in Document 1 but not in Document 2 (deletions)
    - Lines starting with '+ ' are in Document 2 but not in Document 1 (additions)
    - Lines starting with '? ' indicate changes in whitespace or small changes
    - Lines with no prefix are common to both documents
    
    Diff output:
    {diff_text}
    
    Please analyze how these documents differ specifically regarding: "{topic}"
    
    Provide a clear, detailed analysis of the differences between the two documents regarding this topic.
    Refer to specific sections of the documents where relevant differences exist.
    If there are no differences related to this topic, state that clearly.
    """

    TWINCHECK_SUMMARY_PROMPT_TEMPLATE: str = """
    You are comparing two documents using their diff output:
    - Document 1: {doc1_name}
    - Document 2: {doc2_name}
    
    In the diff output below:
    - Lines starting with '- ' are in Document 1 but not in Document 2 (deletions)
    - Lines starting with '+ ' are in Document 2 but not in Document 1 (additions)
    - Lines starting with '? ' indicate changes in whitespace or small changes
    - Lines with no prefix are common to both documents
    
    Diff output:
    {diff_text}
    
    The user is particularly interested in these topics:
    {topics}
    
    Please provide a comprehensive summary of all major differences between the two documents. 
    Focus on structural, content, and semantic differences. 
    Highlight the most important changes and explain their potential implications.
    Be clear, concise, and informative.
    """

    REPLICATE_API_TOKEN: str | None = os.getenv("REPLICATE_API_TOKEN")

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self

    @model_validator(mode="after")
    def _validate_default_embedding_model(self) -> Self:
        """Validate that the configured default embedding model is available."""
        # Import here to avoid circular import
        from app.services.embeddings import EmbeddingService

        if not EmbeddingService.is_valid_model_id(self.DEFAULT_EMBEDDING_MODEL):
            available_models = ", ".join(EmbeddingService.get_model_ids())
            raise ValueError(
                f"Invalid DEFAULT_EMBEDDING_MODEL '{self.DEFAULT_EMBEDDING_MODEL}'. "
                f"Available models: {available_models}"
            )

        return self


settings = Settings()  # type: ignore
