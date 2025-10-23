"""
Tests for rate limiting and account lockout functionality.
"""

import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.middleware.rate_limit import LoginRateLimiter
from app.utils.account_lockout import (
    check_account_lockout,
    record_failed_login,
    reset_failed_login_attempts,
    get_lockout_remaining_time,
)


class TestLoginRateLimiter:
    """Test rate limiting functionality."""

    @pytest.fixture
    def rate_limiter(self):
        """Create a fresh rate limiter instance for each test."""
        return LoginRateLimiter()

    @pytest.mark.asyncio
    async def test_rate_limit_allows_under_threshold(self, rate_limiter):
        """Test that requests under the threshold are allowed."""
        identifier = "test_user"

        # Should allow 4 attempts (under the default max of 5)
        for i in range(4):
            await rate_limiter.check_rate_limit(identifier)

        # Verify no exception was raised
        assert len(rate_limiter.attempts[identifier]) == 4

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_over_threshold(self, rate_limiter):
        """Test that requests over the threshold are blocked."""
        identifier = "test_user"

        # First 5 attempts should succeed
        for i in range(5):
            await rate_limiter.check_rate_limit(identifier)

        # 6th attempt should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await rate_limiter.check_rate_limit(identifier)

        assert exc_info.value.status_code == 429
        assert "Too many login attempts" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_rate_limit_clears_old_attempts(self, rate_limiter):
        """Test that old attempts are cleared after the time window."""
        identifier = "test_user"

        # Add some old attempts manually
        cutoff = datetime.now() - timedelta(minutes=20)
        rate_limiter.attempts[identifier] = [cutoff, cutoff, cutoff]

        # New attempt should clear old ones
        await rate_limiter.check_rate_limit(identifier)

        # Should only have 1 attempt (the new one)
        assert len(rate_limiter.attempts[identifier]) == 1

    @pytest.mark.asyncio
    async def test_clear_attempts(self, rate_limiter):
        """Test clearing attempts for an identifier."""
        identifier = "test_user"

        # Add some attempts
        for i in range(3):
            await rate_limiter.check_rate_limit(identifier)

        # Clear attempts
        rate_limiter.clear_attempts(identifier)

        # Verify attempts were cleared
        assert identifier not in rate_limiter.attempts

    @pytest.mark.asyncio
    async def test_cleanup_old_entries(self, rate_limiter):
        """Test cleanup of old entries."""
        identifier = "test_user"

        # Add some very old attempts
        old_time = datetime.now() - timedelta(hours=25)
        rate_limiter.attempts[identifier] = [old_time, old_time]

        # Run cleanup
        rate_limiter.cleanup_old_entries(hours=24)

        # Verify old entries were removed
        assert identifier not in rate_limiter.attempts


class TestAccountLockout:
    """Test account lockout functionality."""

    def test_check_account_not_locked(self, db, test_user):
        """Test that account is not locked initially."""
        assert check_account_lockout(test_user) is False

    def test_record_failed_login_increments_counter(self, db, test_user):
        """Test that failed login attempts are recorded."""
        initial_attempts = test_user.failed_login_attempts

        record_failed_login(db, test_user)

        assert test_user.failed_login_attempts == initial_attempts + 1

    def test_account_locks_after_threshold(self, db, test_user):
        """Test that account locks after 5 failed attempts."""
        # Record 5 failed attempts
        for i in range(5):
            record_failed_login(db, test_user)

        # Account should be locked
        assert check_account_lockout(test_user) is True
        assert test_user.locked_until is not None
        assert test_user.locked_until > datetime.now()

    def test_reset_failed_login_attempts(self, db, test_user):
        """Test resetting failed login attempts."""
        # Add some failed attempts
        for i in range(3):
            record_failed_login(db, test_user)

        # Reset
        reset_failed_login_attempts(db, test_user)

        # Verify reset
        assert test_user.failed_login_attempts == 0
        assert test_user.locked_until is None

    def test_get_lockout_remaining_time(self, db, test_user):
        """Test getting remaining lockout time."""
        # Lock the account
        for i in range(5):
            record_failed_login(db, test_user)

        # Get remaining time
        remaining = get_lockout_remaining_time(test_user)

        # Should be close to 1 hour (3600 seconds)
        assert 3500 < remaining <= 3600

    def test_get_lockout_remaining_time_not_locked(self, db, test_user):
        """Test getting remaining time when not locked."""
        remaining = get_lockout_remaining_time(test_user)
        assert remaining == 0
