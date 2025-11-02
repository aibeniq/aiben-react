import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.middleware.upload_middleware import UploadProgressMiddleware
from app.middleware.https_redirect import HTTPSRedirectMiddleware


# Initialize logging configuration early
setup_logging()

print("DEBUG: After setup_logging()", flush=True)


def custom_generate_unique_id(route: APIRoute) -> str:
    # Handle routes without tags (like rate limiter endpoints)
    if route.tags and len(route.tags) > 0:
        return f"{route.tags[0]}-{route.name}"
    else:
        return route.name

print("DEBUG: After custom_generate_unique_id()", flush=True)


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

print("DEBUG: After sentry init", flush=True)

# Create FastAPI app
print("DEBUG: About to create FastAPI app", flush=True)
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

print("DEBUG: After FastAPI creation", flush=True)

# NOTE: HTTPS redirect is disabled when using a reverse proxy (Traefik, nginx)
# The proxy should handle HTTPS redirection instead
# Uncomment below if running without a reverse proxy:
# if settings.ENVIRONMENT != "local":
#     app.add_middleware(HTTPSRedirectMiddleware)
#     print("DEBUG: Added HTTPS redirect middleware", flush=True)

# Add trusted host middleware for production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["aiben.io", "*.aiben.io", "demo.aiben.io"]
    )
    print("DEBUG: Added TrustedHost middleware", flush=True)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Explicit methods
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Accept-Language",
            "X-Request-ID",
            "X-Upload-ID",
        ],  # Specific headers only
        expose_headers=["Content-Range", "X-Total-Count", "X-Upload-Progress"],  # Only needed headers
        max_age=600,  # Reduce cache time from 3600 to 600 seconds
    )

print("DEBUG: After CORS middleware", flush=True)

# Add upload progress middleware for multipart form monitoring
print("DEBUG: About to add upload middleware", flush=True)
app.add_middleware(UploadProgressMiddleware)
print("DEBUG: After upload middleware", flush=True)

print("DEBUG: After test middleware", flush=True)

# Add error handlers to ensure CORS headers on all responses
@app.exception_handler(413)
async def payload_too_large_handler(request: Request, exc):
    """Handle 413 Payload Too Large errors with CORS headers"""
    from fastapi.responses import JSONResponse
    
    response = JSONResponse(
        status_code=413,
        content={
            "detail": "File size too large. Maximum upload size is 1GB.",
            "error": "PAYLOAD_TOO_LARGE"
        }
    )
    
    # Add CORS headers manually to error response
    origin = request.headers.get("origin")
    if origin and origin in settings.all_cors_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Accept-Language, X-Request-ID, X-Upload-ID"
    
    return response

# Add security headers middleware for production
if settings.ENVIRONMENT != "local":
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        response = await call_next(request)
        
        # HSTS - Force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # XSS protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy - disable unnecessary browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response
    
    print("DEBUG: Added security headers middleware", flush=True)

app.include_router(api_router, prefix=settings.API_V1_STR)

print("DEBUG: After include_router - APP FULLY INITIALIZED", flush=True)
