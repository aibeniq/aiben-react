## Frontend

Stack: React + TypeScript + Vite, TanStack Router + Query, Chakra UI.

### Local Dev

```bash
cd frontend
npm install
npm run dev
```

Runs outside Docker (recommended). API base configured via `VITE_API_URL`.

### Code Layout

- src/routes : pages
- src/components : shared components
- src/client : generated OpenAPI client

### Generate API Client

```bash
./scripts/generate-client.sh  # from repo root
```

### E2E Tests (Playwright)

```bash
docker compose up -d --wait backend
npx playwright test
```
