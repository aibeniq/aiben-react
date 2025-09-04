import logging
import os
import re

from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init(db_engine: Engine) -> None:
    try:

        # Debug: Print connection details (mask password for security)
        logger.info(f"POSTGRES_SERVER: {os.environ.get('POSTGRES_SERVER', 'NOT SET')}")
        logger.info(f"POSTGRES_PORT: {os.environ.get('POSTGRES_PORT', 'NOT SET')}")
        logger.info(f"POSTGRES_USER: {os.environ.get('POSTGRES_USER', 'NOT SET')}")
        logger.info(f"POSTGRES_DB: {os.environ.get('POSTGRES_DB', 'NOT SET')}")
        password = os.environ.get("POSTGRES_PASSWORD", "NOT SET")
        logger.info(
            f"POSTGRES_PASSWORD: {'*' * len(password) if password != 'NOT SET' else 'NOT SET'}"
        )

        # Also print the final database URI (with masked password)
        db_uri = str(settings.SQLALCHEMY_DATABASE_URI)
        if "postgresql://" in db_uri:
            # Mask password in URI for logging
            masked_uri = re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", db_uri)
            logger.info(f"Database URI: {masked_uri}")

        with Session(db_engine) as session:
            # Try to create session to check if DB is awake
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
