from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import (
    Item,
    User,
    FormConnectForm,
    VeraDocChecklist,
    EmbeddingModel,
    LlmModel,
    ReportGenieOutline,
    LlmInteraction,
    TwinCheckTopicList,
    KnowledgeBase,
)
from app.tests.utils.user import authentication_token_from_email
from app.tests.utils.utils import get_superuser_token_headers

# Import fixtures from fixtures modules
from app.tests.fixtures import documents
from app.tests.fixtures.database import (
    test_user,
    test_superuser,
    test_knowledge_base,
    test_inactive_user,
    multiple_users,
)


@pytest.fixture(scope="function", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        # Delete tables in reverse dependency order to avoid foreign key violations
        # First, clear foreign key references in User table
        from sqlalchemy import update

        session.execute(
            update(User).values(default_llm=None, default_embedding_model=None)
        )
        session.execute(update(KnowledgeBase).values(embedding_model_id=None))

        statement = delete(LlmInteraction)
        session.execute(statement)
        statement = delete(TwinCheckTopicList)
        session.execute(statement)
        statement = delete(ReportGenieOutline)
        session.execute(statement)
        statement = delete(LlmModel)
        session.execute(statement)
        statement = delete(EmbeddingModel)
        session.execute(statement)
        statement = delete(FormConnectForm)
        session.execute(statement)
        statement = delete(VeraDocChecklist)
        session.execute(statement)
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return get_superuser_token_headers(client, db)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
