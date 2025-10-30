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
    from app.models import User, UserStatus
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
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        if not existing_user:
            superuser = User(
                email=settings.FIRST_SUPERUSER,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_active=True,
                is_superuser=True,
                status=UserStatus.ACTIVE,  # Ensure user is active
            )
            session.add(superuser)
            session.commit()
        else:
            # Update existing user to ensure it's active
            if existing_user.status != UserStatus.ACTIVE:
                existing_user.status = UserStatus.ACTIVE
                existing_user.is_active = True
                existing_user.is_superuser = True
                session.commit()

        login_data = {
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        # The endpoint sets a cookie, TestClient will automatically include it in subsequent requests
        # No need to return Authorization headers since cookies are handled automatically
        return {}
    finally:
        if created_session:
            session.close()
