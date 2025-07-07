import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from app.api.main import api_router
from app.core.config import settings
from app.core.app_state import app_state
from app.services.vectordb.main import VectorDBService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Initialize vector database service
    try:
        logger.info("Initializing vector database service")
        app_state.vector_db_service = VectorDBService()  # type: ignore
        logger.info("Vector database service initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing vector database service: {e}")
        raise

    try:
        yield  # before yield = startup, after yield = shutdown
    finally:
        logger.info("Closing vector database service")
        if app_state.vector_db_service and hasattr(
            app_state.vector_db_service, "client"
        ):
            try:
                app_state.vector_db_service.client.close()
                logger.info("Vector database service closed")
            except Exception as e:
                logger.error(f"Error closing vector database service: {e}")
        else:
            logger.info("Vector database service was not initialized, nothing to close")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
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
