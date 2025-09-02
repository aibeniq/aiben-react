FROM python:3.10

ENV PYTHONUNBUFFERED=1

# Create non-root user for OpenShift compatibility (will often be ignored in OpenShift which injects a random UID)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app/

#argument for whether to install huggingface
ARG INSTALL_HUGGINGFACE=true

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

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

COPY ./scripts /app/scripts

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

COPY ./app /app/app

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Ensure pip is available in the virtual environment for runtime ML installations
# Use uv pip install (not uv add) to avoid lockfile issues in OpenShift
RUN uv pip install pip

# Create writable directories for OpenShift arbitrary UID
RUN mkdir -p /tmp/uv-cache /tmp/pip-cache && \
    chmod 777 /tmp/uv-cache /tmp/pip-cache
# HuggingFace cache workaround for OpenShift arbitrary UID
ENV HF_HOME=/tmp/huggingface-cache
ENV TRANSFORMERS_CACHE=/tmp/huggingface-cache
RUN mkdir -p /tmp/huggingface-cache && chmod 0777 /tmp/huggingface-cache

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