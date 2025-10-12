"""
HTTPS Redirect Middleware

This middleware enforces HTTPS in production environments by redirecting
all HTTP requests to HTTPS.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.requests import Request

from app.core.config import settings


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP requests to HTTPS in production.
    
    Only active when ENVIRONMENT is not "local" to allow local development
    over HTTP.
    
    NOTE: This middleware checks X-Forwarded-Proto header to handle cases
    where the app is behind a reverse proxy (like Traefik, nginx) that 
    terminates SSL. The proxy sets X-Forwarded-Proto to indicate the 
    original protocol used by the client.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Check if request is HTTP and redirect to HTTPS if in production.
        
        When behind a reverse proxy:
        - The request.url.scheme will be 'http' (proxy to backend)
        - But X-Forwarded-Proto will be 'https' (client to proxy)
        - We check X-Forwarded-Proto to avoid redirect loops
        
        Args:
            request: The incoming request
            call_next: The next middleware/route handler
            
        Returns:
            RedirectResponse to HTTPS URL or normal response
        """
        if settings.ENVIRONMENT == "production":
            # Check X-Forwarded-Proto header (set by reverse proxy)
            forwarded_proto = request.headers.get("x-forwarded-proto", "").lower()
            
            # If behind a proxy, trust X-Forwarded-Proto
            # Otherwise, check the request scheme directly
            if forwarded_proto:
                actual_scheme = forwarded_proto
            else:
                actual_scheme = request.url.scheme
            
            # Only redirect if the actual client request was HTTP
            if actual_scheme != "https":
                url = request.url.replace(scheme="https")
                return RedirectResponse(url, status_code=301)
        
        return await call_next(request)
