import sentry_sdk
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness probe.
    Returns 200 if the application is running.
    """
    return {"status": "healthy", "service": "aibeniq-backend"}


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes readiness probe.
    Verifies database connectivity and returns 200 if ready to serve traffic.
    """
    try:
        # Test database connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Database connection failed: {str(e)}"
        )
