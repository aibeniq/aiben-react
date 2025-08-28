# Development

Local stack:

```bash
docker compose --profile frontend watch
```

Key URLs:

- Frontend http://localhost:5173
- Backend http://localhost:8000
- Docs http://localhost:8000/docs
- Adminer http://localhost:8080
- Traefik http://localhost:8090

Swap to native dev server:

```bash
docker compose stop frontend
cd frontend && npm run dev
```

Backend native:

```bash
docker compose stop backend
cd backend && fastapi dev app/main.py
```

Pre-commit:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```
