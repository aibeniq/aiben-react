import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.middleware.upload_middleware import UploadProgressMiddleware


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

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

print("DEBUG: After FastAPI creation", flush=True)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],  # Expose all headers to the client
        max_age=3600,  # Cache preflight requests for 1 hour
    )

print("DEBUG: After CORS middleware", flush=True)

# Add upload progress middleware for multipart form monitoring
app.add_middleware(UploadProgressMiddleware)

print("DEBUG: After upload middleware", flush=True)

app.include_router(api_router, prefix=settings.API_V1_STR)

print("DEBUG: After include_router - APP FULLY INITIALIZED", flush=True)
