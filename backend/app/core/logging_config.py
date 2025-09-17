"""
Logging configuration for the FastAPI application.
Ensures proper structured logging and prevents log corruption.
"""

import logging
import logging.config
import sys
from typing import Dict, Any

from app.core.config import settings


def get_logging_config() -> Dict[str, Any]:
    """
    Returns logging configuration dictionary optimized for Docker containers.
    Ensures atomic log writes and proper formatting.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "structured": {
                "format": "%(asctime)s | %(levelname)8s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "structured",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "level": "INFO",
            },
            "error": {
                "formatter": "structured",
                "class": "logging.StreamHandler",
                "stream": sys.stderr,
                "level": "ERROR",
            },
        },
        "root": {
            "level": "INFO" if settings.ENVIRONMENT == "production" else "DEBUG",
            "handlers": ["default"],
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["error"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "app": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }


def setup_logging() -> None:
    """
    Set up logging configuration for the application.
    This should be called once at application startup.
    """
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Get the root logger and ensure it's configured properly
    logger = logging.getLogger("app")
    logger.info("Logging configuration initialized successfully")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name of the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"app.{name}")
