import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce request size limits and prevent DoS attacks.
    Rejects requests that exceed the configured maximum size.
    """

    def __init__(self, app: ASGIApp, max_size: int = 500 * 1024 * 1024):  # 500MB default
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    logger.warning(
                        f"Request size {size} bytes exceeds limit {self.max_size} bytes "
                        f"for {request.method} {request.url.path}"
                    )
                    return Response(
                        content="Request too large",
                        status_code=413,
                        media_type="text/plain"
                    )
            except ValueError:
                # Invalid content-length header, let it pass through
                # The application will handle it appropriately
                pass

        return await call_next(request)