import signal
import sys
import asyncio
import sentry_sdk
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.main import api_router
from app.core.config import settings
from app.core.db import engine
import logging


def custom_generate_unique_id(route: APIRoute) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    else:
        return route.name


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

# Startup diagnostics (one-time) for CORS configuration
logging.getLogger(__name__).info(
    "CORS configured: %s (FRONTEND_HOST=%s)",
    settings.all_cors_origins,
    settings.FRONTEND_HOST,
)
logging.getLogger(__name__).info(
    "Middleware stack: %s",
    [m.cls.__name__ for m in app.user_middleware],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


# Global flag for graceful shutdown
_shutdown_event = asyncio.Event()


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logging.getLogger(__name__).info(
        f"Received signal {signum}, initiating graceful shutdown..."
    )
    _shutdown_event.set()


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logging.getLogger(__name__).info("AIBeniq Backend starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources during shutdown."""
    logging.getLogger(__name__).info("AIBeniq Backend shutting down gracefully...")
    # Close database connections
    engine.dispose()
    logging.getLogger(__name__).info("Database connections closed.")


@app.get(f"{settings.API_V1_STR}/utils/cors-origins", tags=["utils"])
async def get_cors_origins():
    """Runtime inspection of CORS configuration (non-sensitive)."""
    return {
        "allowed_origins": settings.all_cors_origins,
        "frontend_host": settings.FRONTEND_HOST,
        "cors_middleware_present": any(
            getattr(m, "cls", None).__name__ == "CORSMiddleware"
            for m in app.user_middleware
        ),
    }


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
