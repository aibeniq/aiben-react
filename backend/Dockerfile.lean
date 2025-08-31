FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Install curl for health checks and other system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for OpenShift compatibility (will often be ignored in OpenShift which injects a random UID)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app/

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

# Copy lean dependencies configuration
COPY ./pyproject.lean.toml ./pyproject.toml

# Generate lock file for lean dependencies
RUN uv lock

# Install dependencies without ML packages
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

# Set environment variables for lean deployment
ENV ENABLE_PYTORCH=false
ENV RUNTIME_INSTALL_PYTORCH=false

COPY ./scripts /app/scripts

COPY ./alembic.ini /app/

COPY ./app /app/app

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Ensure pip is available in the virtual environment for runtime ML installations
# Use uv pip install (not uv add) to avoid lockfile issues in OpenShift
RUN uv pip install pip

# Create target directory with world-writable permissions for OpenShift arbitrary UID
RUN mkdir -p /tmp/python-packages/lib/python3.10/site-packages && \
    chmod -R 777 /tmp/python-packages && \
    mkdir -p /tmp/uv-cache /tmp/pip-cache && \
    chmod 777 /tmp/uv-cache /tmp/pip-cache

# Add target directory to Python path so installed packages are found
ENV PYTHONPATH="/tmp/python-packages/lib/python3.10/site-packages:${PYTHONPATH}"

# Add graceful shutdown and health check configuration
STOPSIGNAL SIGTERM

# Set graceful shutdown timeout
ENV GRACEFUL_TIMEOUT=30

# Add health check that matches OpenShift readiness probe
# Fix: HEALTHCHECK command must be on a single line
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 CMD curl -f http://localhost:8000/ready || exit 1

# Switch to non-root user
USER appuser

# Use FastAPI with single worker for OpenShift compatibility
CMD ["fastapi", "run", "--workers", "1", "app/main.py"]
