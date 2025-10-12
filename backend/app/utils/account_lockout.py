"""
Account lockout utilities for preventing brute force attacks.
"""
from datetime import datetime, timedelta
from sqlmodel import Session

from app.models import User


def check_account_lockout(user: User) -> bool:
    """
    Check if a user account is currently locked.

    Args:
        user: User model instance

    Returns:
        True if account is locked, False otherwise
    """
    if user.locked_until and user.locked_until > datetime.now():
        return True
    return False


def record_failed_login(session: Session, user: User) -> None:
    """
    Record a failed login attempt and lock account if threshold is exceeded.

    Args:
        session: Database session
        user: User model instance
    """
    user.failed_login_attempts += 1

    # Lock account after 5 failed attempts
    if user.failed_login_attempts >= 5:
        # Lock for 1 hour
        user.locked_until = datetime.now() + timedelta(hours=1)

    session.add(user)
    session.commit()
    session.refresh(user)


def reset_failed_login_attempts(session: Session, user: User) -> None:
    """
    Reset failed login attempts counter on successful login.

    Args:
        session: Database session
        user: User model instance
    """
    user.failed_login_attempts = 0
    user.locked_until = None
    session.add(user)
    session.commit()
    session.refresh(user)


def get_lockout_remaining_time(user: User) -> int:
    """
    Get remaining lockout time in seconds.

    Args:
        user: User model instance

    Returns:
        Remaining lockout time in seconds, 0 if not locked
    """
    if user.locked_until and user.locked_until > datetime.now():
        return int((user.locked_until - datetime.now()).total_seconds())
    return 0
