## Backend

Framework: FastAPI (async), SQLModel, PostgreSQL.

### Setup (local without Docker)

```bash
cd backend
uv sync
source .venv/bin/activate  # or on Windows: .venv\\Scripts\\activate
fastapi dev app/main.py
```

### Running in Docker Compose

Port 8000 exposed; hot reload enabled via override file.

### Key Directories

- app/api/ : route modules
- app/services/ : LLM + embeddings integration
- app/core/config.py : settings (ENVIRONMENT production/development/local)
- app/alembic/ : migrations

### Migrations

```bash
docker compose exec backend alembic revision --autogenerate -m "Message"
docker compose exec backend alembic upgrade head
```

### Tests

```bash
bash backend/scripts/test.sh
```

### LLM/Embedding Providers

Configured via config ENV vars (ENABLED_PROVIDERS). Background model pulls triggered on model create.

### Email Templates

MJML sources in `app/email-templates/src`; build to `build` with VS Code MJML extension.
