"""
Rate limiting middleware for authentication endpoints to prevent brute force attacks.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict, Optional

from fastapi import HTTPException, Request


class LoginRateLimiter:
    """
    Rate limiter for login attempts to prevent brute force attacks.
    Tracks attempts by IP address and username.
    """

    def __init__(self):
        # Dictionary to track login attempts: {identifier: [timestamp, timestamp, ...]}
        self.attempts: DefaultDict[str, list[datetime]] = defaultdict(list)
        # Dictionary to track blocked identifiers: {identifier: unblock_time}
        self.blocked: DefaultDict[str, Optional[datetime]] = defaultdict(lambda: None)

    async def check_rate_limit(
        self,
        identifier: str,
        max_attempts: int = 5,
        window_minutes: int = 15,
    ) -> None:
        """
        Check if the identifier has exceeded rate limits.

        Args:
            identifier: Unique identifier (e.g., "ip:192.168.1.1" or "user:john@example.com")
            max_attempts: Maximum number of attempts allowed within the time window
            window_minutes: Time window in minutes for counting attempts

        Raises:
            HTTPException: If rate limit is exceeded (status 429)
        """
        now = datetime.now()

        # Check if identifier is currently blocked
        if self.blocked[identifier] and self.blocked[identifier] > now:
            remaining = int((self.blocked[identifier] - now).total_seconds())
            raise HTTPException(
                status_code=429,
                detail=f"Too many login attempts. Try again in {remaining} seconds.",
            )

        # Clean up old attempts outside the time window
        cutoff = now - timedelta(minutes=window_minutes)
        self.attempts[identifier] = [
            attempt for attempt in self.attempts[identifier] if attempt > cutoff
        ]

        # Check if attempt count exceeds the limit
        if len(self.attempts[identifier]) >= max_attempts:
            # Calculate block duration with exponential backoff
            attempt_count = len(self.attempts[identifier])
            block_minutes = min(
                60, window_minutes * (attempt_count // max_attempts)
            )  # Max 60 minutes
            self.blocked[identifier] = now + timedelta(minutes=block_minutes)

            raise HTTPException(
                status_code=429,
                detail=f"Too many login attempts. Account temporarily blocked for {block_minutes} minutes.",
            )

        # Record this attempt
        self.attempts[identifier].append(now)

    def clear_attempts(self, identifier: str) -> None:
        """
        Clear login attempts for an identifier (called on successful login).

        Args:
            identifier: The identifier to clear attempts for
        """
        if identifier in self.attempts:
            del self.attempts[identifier]
        if identifier in self.blocked:
            del self.blocked[identifier]

    def cleanup_old_entries(self, hours: int = 24) -> None:
        """
        Clean up old entries to prevent memory buildup.
        Should be called periodically (e.g., via scheduled task).

        Args:
            hours: Remove entries older than this many hours
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        # Clean attempts
        for identifier in list(self.attempts.keys()):
            self.attempts[identifier] = [
                attempt for attempt in self.attempts[identifier] if attempt > cutoff
            ]
            if not self.attempts[identifier]:
                del self.attempts[identifier]

        # Clean blocked entries
        now = datetime.now()
        for identifier in list(self.blocked.keys()):
            if self.blocked[identifier] and self.blocked[identifier] < now:
                del self.blocked[identifier]


# Global rate limiter instance
rate_limiter = LoginRateLimiter()


def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request, considering proxy headers.

    Args:
        request: FastAPI Request object

    Returns:
        Client IP address as string
    """
    # Check for X-Forwarded-For header (when behind a proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()

    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to direct client host
    return request.client.host if request.client else "unknown"
