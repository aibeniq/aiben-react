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

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    # Document processing parameters
    DOCUMENT_CHUNK_SIZE: int = 1000
    DOCUMENT_CHUNK_OVERLAP: int = 200

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str
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
    
    VERADOC_QA_PROMPT_TEMPLATE: str = """
    Read the following document and answer the following question clearly and concisely in 100 words or less.
    
    SAMPLE DOCUMENT: {document_text}
    
    QUESTION: {question}
    
    Keep the following RELEVANT REQUIREMENTS in mind when answering the question:
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


settings = Settings()  # type: ignore
