# Deployment (Docker Compose)

Minimal production example (Traefik external recommended). Set required secrets in environment or `.env`.

```bash
docker compose -f docker-compose.yml up -d
```

Primary environment variables: SECRET_KEY, FIRST_SUPERUSER, FIRST_SUPERUSER_PASSWORD, POSTGRES_PASSWORD, BACKEND_CORS_ORIGINS.

CI/CD: GitHub Actions workflows can build & push images, then remote compose deploy.
