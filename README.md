# AibenIQ

> **Archived:** This repository is no longer actively maintained. It is retained
> for reference only; no support, security fixes, or compatibility updates are
> planned.

## Security notice

Do not deploy this archived code without a complete independent security review.
Never commit credentials, API keys, database passwords, or environment-specific
configuration. Runtime configuration belongs in an untracked `.env` file or a
deployment secret manager.

The repository includes `.env.example` as a non-sensitive configuration
template. Copy it to `.env`, set the required values in a secure location, and
keep that file out of version control:

```bash
cp .env.example .env
```

Required secret values include `SECRET_KEY`, `FIRST_SUPERUSER_PASSWORD`,
`POSTGRES_PASSWORD`, and `REDIS_PASSWORD`. Configure production hostnames using
`TRUSTED_HOSTS` and `BACKEND_CORS_ORIGINS`; do not rely on repository defaults.

## Project overview

AibenIQ is a FastAPI and PostgreSQL backend with a React, TypeScript, and Vite
frontend. Docker Compose definitions and historical development material remain
in the repository for reference.

## License

This project is licensed under the [MIT License](LICENSE).
