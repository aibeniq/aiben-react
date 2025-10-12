#!/usr/bin/env python3
"""
Utility script to manage account lockouts.
Useful for administrators to unlock accounts or check lockout status.
"""
import argparse
import sys
from datetime import datetime

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.models import User


def get_session():
    """Create database session."""
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    return Session(engine)


def list_locked_accounts():
    """List all currently locked accounts."""
    session = get_session()
    statement = select(User).where(User.locked_until.isnot(None))
    users = session.exec(statement).all()

    if not users:
        print("No locked accounts found.")
        return

    print(f"\n{'Email':<40} {'Failed Attempts':<20} {'Locked Until':<25}")
    print("-" * 85)

    for user in users:
        if user.locked_until and user.locked_until > datetime.now():
            status = user.locked_until.strftime("%Y-%m-%d %H:%M:%S")
        else:
            status = "Expired (will unlock on next attempt)"

        print(f"{user.email:<40} {user.failed_login_attempts:<20} {status:<25}")

    session.close()


def unlock_account(email: str):
    """Unlock a specific account by email."""
    session = get_session()
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        print(f"❌ User with email '{email}' not found.")
        session.close()
        return

    if user.failed_login_attempts == 0 and user.locked_until is None:
        print(f"✅ Account '{email}' is not locked.")
        session.close()
        return

    # Reset lockout
    user.failed_login_attempts = 0
    user.locked_until = None
    session.add(user)
    session.commit()

    print(f"✅ Account '{email}' has been unlocked.")
    print(f"   - Failed attempts reset to 0")
    print(f"   - Lockout expiration cleared")

    session.close()


def check_account_status(email: str):
    """Check the lockout status of a specific account."""
    session = get_session()
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        print(f"❌ User with email '{email}' not found.")
        session.close()
        return

    print(f"\nAccount Status for: {email}")
    print("-" * 60)
    print(f"Email: {user.email}")
    print(f"Active: {user.is_active}")
    print(f"Failed Login Attempts: {user.failed_login_attempts}")

    if user.locked_until:
        if user.locked_until > datetime.now():
            remaining = (user.locked_until - datetime.now()).total_seconds()
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            print(f"Locked Until: {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Status: 🔒 LOCKED (unlocks in {minutes}m {seconds}s)")
        else:
            print(f"Locked Until: {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')} (expired)")
            print(f"Status: ✅ Will unlock on next login attempt")
    else:
        print(f"Locked Until: None")
        print(f"Status: ✅ NOT LOCKED")

    session.close()


def unlock_all_expired():
    """Unlock all accounts where the lockout period has expired."""
    session = get_session()
    statement = select(User).where(
        User.locked_until.isnot(None),
        User.locked_until < datetime.now()
    )
    users = session.exec(statement).all()

    if not users:
        print("No expired locks found.")
        session.close()
        return

    count = 0
    for user in users:
        user.failed_login_attempts = 0
        user.locked_until = None
        session.add(user)
        count += 1

    session.commit()
    print(f"✅ Unlocked {count} account(s) with expired locks.")
    session.close()


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Manage account lockouts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all locked accounts
  python manage_lockouts.py --list

  # Check specific account status
  python manage_lockouts.py --check user@example.com

  # Unlock specific account
  python manage_lockouts.py --unlock user@example.com

  # Unlock all expired locks
  python manage_lockouts.py --unlock-expired
        """
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all currently locked accounts"
    )
    parser.add_argument(
        "--check",
        metavar="EMAIL",
        help="Check lockout status for specific account"
    )
    parser.add_argument(
        "--unlock",
        metavar="EMAIL",
        help="Unlock specific account by email"
    )
    parser.add_argument(
        "--unlock-expired",
        action="store_true",
        help="Unlock all accounts with expired locks"
    )

    args = parser.parse_args()

    # Require at least one action
    if not any([args.list, args.check, args.unlock, args.unlock_expired]):
        parser.print_help()
        sys.exit(1)

    try:
        if args.list:
            list_locked_accounts()
        if args.check:
            check_account_status(args.check)
        if args.unlock:
            unlock_account(args.unlock)
        if args.unlock_expired:
            unlock_all_expired()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
