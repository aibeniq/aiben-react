"""
Global OpenAI Rate Limiter

This module provides a global rate limiter to coordinate all OpenAI API requests
across the application, preventing rate limit errors by proactively managing
token usage within OpenAI's rate limits.
"""

import time
import threading
from typing import Tuple, Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GlobalOpenAIRateLimiter:
    """
    Global rate limiter for OpenAI API requests.
    
    Coordinates all OpenAI requests to stay within rate limits by tracking
    token usage over a rolling time window and preventing requests that
    would exceed the limits.
    """
    
    def __init__(self, tokens_per_minute: int = 180000, requests_per_minute: int = 500):
        """
        Initialize the rate limiter with realistic limits based on typical OpenAI capacity.
        
        Args:
            tokens_per_minute: Realistic token limit (default 180k - 90% of typical 200k limit)
            requests_per_minute: Realistic request limit (default 500 - conservative but practical)
        """
        self.tokens_per_minute = tokens_per_minute
        self.requests_per_minute = requests_per_minute
        
        # Token tracking
        self.tokens_used = 0
        self.token_window_start = time.time()
        
        # Request tracking
        self.requests_made = 0
        self.request_window_start = time.time()
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info(f"🚦 Global OpenAI Rate Limiter initialized: {tokens_per_minute} TPM, {requests_per_minute} RPM")
    
    def can_make_request(self, estimated_tokens: int) -> Tuple[bool, float]:
        """
        Check if a request can be made without exceeding rate limits.
        
        Args:
            estimated_tokens: Estimated number of tokens the request will use
            
        Returns:
            Tuple of (can_proceed, wait_time_seconds)
        """
        with self.lock:
            current_time = time.time()
            
            # Reset token window if a minute has passed
            if current_time - self.token_window_start >= 60:
                self.tokens_used = 0
                self.token_window_start = current_time
                logger.debug("🔄 Token window reset")
            
            # Reset request window if a minute has passed
            if current_time - self.request_window_start >= 60:
                self.requests_made = 0
                self.request_window_start = current_time
                logger.debug("🔄 Request window reset")
            
            # Check token limits
            if self.tokens_used + estimated_tokens > self.tokens_per_minute:
                token_wait_time = 60 - (current_time - self.token_window_start)
                logger.warning(
                    f"🚫 Token limit would be exceeded: "
                    f"used={self.tokens_used}, estimated={estimated_tokens}, "
                    f"limit={self.tokens_per_minute}, wait={token_wait_time:.2f}s"
                )
                return False, max(0, token_wait_time)
            
            # Check request limits
            if self.requests_made >= self.requests_per_minute:
                request_wait_time = 60 - (current_time - self.request_window_start)
                logger.warning(
                    f"🚫 Request limit would be exceeded: "
                    f"made={self.requests_made}, limit={self.requests_per_minute}, "
                    f"wait={request_wait_time:.2f}s"
                )
                return False, max(0, request_wait_time)
            
            # Reserve the tokens and request slot
            self.tokens_used += estimated_tokens
            self.requests_made += 1
            
            logger.debug(
                f"✅ Request approved: tokens={self.tokens_used}/{self.tokens_per_minute}, "
                f"requests={self.requests_made}/{self.requests_per_minute}"
            )
            
            return True, 0
    
    def record_actual_usage(self, actual_tokens: int, estimated_tokens: int):
        """
        Update the token count with actual usage after request completion.
        
        Args:
            actual_tokens: Actual number of tokens used
            estimated_tokens: Previously estimated tokens
        """
        with self.lock:
            # Adjust for difference between estimate and actual
            adjustment = actual_tokens - estimated_tokens
            self.tokens_used += adjustment
            
            # Ensure we don't go negative due to overestimation
            self.tokens_used = max(0, self.tokens_used)
            
            if adjustment != 0:
                logger.debug(
                    f"📊 Token usage adjusted: estimated={estimated_tokens}, "
                    f"actual={actual_tokens}, adjustment={adjustment}, "
                    f"total_used={self.tokens_used}"
                )
    
    def get_current_usage(self) -> dict:
        """
        Get current usage statistics.
        
        Returns:
            Dictionary with current usage information
        """
        with self.lock:
            current_time = time.time()
            
            token_window_remaining = max(0, 60 - (current_time - self.token_window_start))
            request_window_remaining = max(0, 60 - (current_time - self.request_window_start))
            
            return {
                "tokens_used": self.tokens_used,
                "tokens_limit": self.tokens_per_minute,
                "tokens_available": max(0, self.tokens_per_minute - self.tokens_used),
                "token_window_remaining": token_window_remaining,
                "requests_made": self.requests_made,
                "requests_limit": self.requests_per_minute,
                "requests_available": max(0, self.requests_per_minute - self.requests_made),
                "request_window_remaining": request_window_remaining,
            }
    
    def wait_for_capacity(self, estimated_tokens: int, max_wait_time: float = None) -> bool:
        """
        Wait until there's capacity for the request.
        
        Args:
            estimated_tokens: Estimated tokens needed
            max_wait_time: Maximum time to wait in seconds (uses config default if None)
            
        Returns:
            True if capacity is available, False if max wait time exceeded or request impossible
        """
        if max_wait_time is None:
            from app.core.config import settings
            max_wait_time = settings.OPENAI_RATE_LIMIT_MAX_WAIT
        
        # NEW: Immediate rejection for requests larger than per-minute budget
        if estimated_tokens > self.tokens_per_minute:
            logger.error(
                f"❌ REJECTED: Request requires {estimated_tokens:,} tokens, "
                f"exceeds per-minute budget of {self.tokens_per_minute:,} tokens. "
                f"This request is IMPOSSIBLE to fulfill - must split into smaller chunks."
            )
            return False
        
        # NEW: Immediate rejection for requests larger than safe per-request limit
        from app.core.config import settings
        max_per_request = getattr(settings, 'OPENAI_MAX_TOKENS_PER_REQUEST', 80000)
        if estimated_tokens > max_per_request:
            logger.error(
                f"❌ REJECTED: Request requires {estimated_tokens:,} tokens, "
                f"exceeds per-request limit of {max_per_request:,} tokens. "
                f"Must split into smaller chunks."
            )
            return False
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            can_proceed, wait_time = self.can_make_request(estimated_tokens)
            
            if can_proceed:
                # We already reserved the slot in can_make_request, so return True
                return True
            
            if wait_time > 0:
                # Wait for the suggested time, but cap it at remaining max_wait_time
                actual_wait = min(wait_time, max_wait_time - (time.time() - start_time))
                if actual_wait > 0:
                    logger.info(f"⏳ Waiting {actual_wait:.2f}s for rate limit capacity...")
                    time.sleep(actual_wait)
            else:
                # Small delay to prevent busy waiting
                time.sleep(0.1)
        
        logger.error(f"❌ Max wait time ({max_wait_time}s) exceeded waiting for rate limit capacity")
        return False

    def estimate_multimodal_tokens(
        self, 
        text_content: str, 
        images: Optional[List[str]] = None, 
        model: str = "gpt-4o"
    ) -> int:
        """
        Estimate token consumption for multimodal requests (text + images).
        
        Args:
            text_content: The text portion of the request
            images: List of base64 encoded images (optional)
            model: The model being used
            
        Returns:
            Estimated total token consumption
        """
        try:
            from app.services.vision_tokens import calculate_multimodal_tokens
            
            if not images:
                # Text-only estimation: roughly 4 characters per token
                return max(len(text_content) // 4, 10)
            
            # Multimodal calculation including image tokens
            token_breakdown = calculate_multimodal_tokens(text_content, images, model)
            estimated_tokens = token_breakdown["total_tokens"]
            
            logger.debug(
                f"🖼️ Multimodal token estimate: text={token_breakdown['text_tokens']}, "
                f"images={token_breakdown['image_tokens']} ({token_breakdown['image_count']} images), "
                f"total={estimated_tokens}, model={model}"
            )
            
            return estimated_tokens
            
        except Exception as e:
            logger.warning(f"Error estimating multimodal tokens: {e}, using conservative fallback")
            # Conservative fallback for multimodal requests
            base_tokens = len(text_content) // 4
            image_tokens = len(images or []) * 1000  # Conservative estimate per image
            return max(base_tokens + image_tokens, 100)


# Global instance - shared across all OpenAI requests
# Using centralized configuration from settings
from app.core.config import settings

global_rate_limiter = GlobalOpenAIRateLimiter(
    tokens_per_minute=settings.OPENAI_TOKENS_PER_MINUTE, 
    requests_per_minute=settings.OPENAI_REQUESTS_PER_MINUTE
)


def estimate_tokens(text: str, response_buffer: int = 1000) -> int:
    """
    Estimate the number of tokens in a text string.
    
    Args:
        text: Input text
        response_buffer: Additional tokens to reserve for response
        
    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters for English text
    # This is conservative - actual tokenization may be different
    input_tokens = len(text) // 4
    total_tokens = input_tokens + response_buffer
    
    return max(100, total_tokens)  # Minimum 100 tokens


def get_rate_limiter_stats() -> dict:
    """
    Get current rate limiter statistics for monitoring.
    
    Returns:
        Dictionary with current usage statistics
    """
    return global_rate_limiter.get_current_usage()