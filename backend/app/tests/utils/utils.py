import random
import string

from fastapi.testclient import TestClient

from app.core.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient, db_session=None) -> dict[str, str]:
    from sqlmodel import select
    from app.models import User
    from app.core.security import get_password_hash

    # Use provided session or create a new one
    session = db_session
    created_session = False
    if session is None:
        from app.core.db import engine
        from sqlmodel import Session

        session = Session(engine)
        created_session = True

    try:
        # Ensure superuser exists in database
        existing_user = session.exec(
            select(User).where(User.email == "admin@example.com")
        ).first()
        if not existing_user:
            superuser = User(
                email="admin@example.com",
                hashed_password=get_password_hash(
                    "minglemongles"
                ),  # Use the correct password from settings
                is_active=True,
                is_superuser=True,
            )
            session.add(superuser)
            session.commit()

        login_data = {
            "username": "admin@example.com",  # Use test superuser email
            "password": "minglemongles",  # Use the correct password
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        # The endpoint sets a cookie, TestClient will automatically include it in subsequent requests
        # No need to return Authorization headers since cookies are handled automatically
        return {}
    finally:
        if created_session:
            session.close()
