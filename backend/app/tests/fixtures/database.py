"""
Database fixtures for testing database operations and models.
"""

import pytest
from sqlmodel import Session
from app.models import User, KnowledgeBase
from app.core.security import get_password_hash


@pytest.fixture
def test_user(db: Session):
    """Create a test user in the database."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        # Reset lockout fields to ensure clean state
        existing_user.failed_login_attempts = 0
        existing_user.locked_until = None
        db.commit()
        db.refresh(existing_user)
        return existing_user

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_superuser(db: Session):
    """Create a test superuser in the database."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "admin@example.com").first()
    if existing_user:
        return existing_user

    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_knowledge_base(db: Session, test_user):
    """Create a test knowledge base in the database."""
    # Check if knowledge base already exists
    existing_kb = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.title == "Test Knowledge Base",
            KnowledgeBase.owner_id == test_user.id,
        )
        .first()
    )
    if existing_kb:
        return existing_kb

    from datetime import datetime

    kb = KnowledgeBase(
        title="Test Knowledge Base",
        description="A test knowledge base for automated testing",
        owner_id=test_user.id,
        date_created=datetime.utcnow(),
        date_modified=datetime.utcnow(),
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


@pytest.fixture
def test_inactive_user(db: Session):
    """Create an inactive test user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "inactive@example.com").first()
    if existing_user:
        return existing_user

    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("inactivepassword"),
        is_active=False,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def multiple_users(db: Session):
    """Create multiple test users for testing user-related operations."""
    users = []
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            hashed_password=get_password_hash(f"password{i}"),
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        users.append(user)
    db.commit()
    for user in users:
        db.refresh(user)
    return users
