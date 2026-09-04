# AibenIQ

> **Archived:** This repository is no longer actively maintained. It is retained
> for reference only; no support, security fixes, or compatibility updates are
> planned.

AibenIQ is an explainable, auditable AI workspace for document-intensive work.
It uses structured workflows and human review to turn collections of reference
documents into reviewable answers, analyses, and drafted content. Outputs are
grounded in selected knowledge bases and include source citations so users can
verify the supporting material.

## What it does

### Ask

Query uploaded documents or a reusable knowledge base with natural language.
AibenIQ uses semantic retrieval to produce focused answers and links each
answer to its source material for verification.

### Review

Evaluate a document against a checklist and a reference knowledge base. Each
checklist item includes a summary, detailed evaluation, and the source context
used to reach it, supporting review workflows such as policy or compliance
assessment.

### Generate

Create a document from multiple source records using a customizable outline.
Each generated section is paired with its supporting sources. Drafts can be
reviewed, refined, copied, or exported in DOCX and CSV formats.

### Compare

Compare multiple documents or versions against a list of topics. Documents do
not need to share a template: AibenIQ reports a summary of differences and
topic-by-topic details for transparent review.

### Match

Check whether specific fields agree across documents in different formats.
This supports rapid detection of discrepancies in data such as transaction
metadata, including information captured from handwritten documents.

## Designed for accountable AI

- **Grounded and inspectable:** Answers use the selected reference data, with
  source links available for review instead of broad web search.
- **Human-in-the-loop:** Workflows expose intermediate inputs and outputs so
  reviewers can validate and iteratively refine results.
- **Reusable knowledge bases:** Create purpose-specific collections of source
  documents and update them by adding or replacing files rather than retraining
  a model.
- **Flexible model deployment:** Use supported API-based providers or local
  models through Ollama or Hugging Face when data must remain in your
  environment.

## Architecture

The application includes a FastAPI backend, PostgreSQL database, Chroma vector
store, and a React/TypeScript frontend. Docker Compose provides the local stack.
Model integrations include AWS Bedrock, OpenAI, Replicate, Ollama, and optional
Hugging Face models.

## Repository layout

| Path | Purpose |
| --- | --- |
| `backend/` | FastAPI application, data models, API routes, and automated tests |
| `frontend/` | React/Vite web application and Playwright tests |
| `docs/guides/` | Template-era development and deployment guides |
| `docs/reference/` | Technical reference and release history |
| `docs/archive/implementation-notes/` | Historical implementation notes |
| `archive/manual-tests/` | Preserved standalone test scripts and fixtures, not part of CI |
| `archive/` | Historical fixtures, generated data, and retired configuration |
| `scripts/archive/` | Preserved maintenance and diagnostic utilities |

## Quick launch (development reference)

This project is archived. Do not deploy it without an independent security
review. For a local reference environment:

1. Copy `.env.example` to `.env`, then replace all placeholder secrets,
   passwords, and environment-specific settings. Keep `.env` untracked.
2. Create Docker's external Traefik network:

   ```bash
   docker network create traefik-public
   ```

3. Start the backend and its dependencies:

   ```bash
   docker compose up --build -d backend
   ```

4. Start the frontend development server:

   ```bash
   cd frontend
   npm ci
   npm run dev
   ```

5. Open `http://localhost:5173`.

See [backend/README.md](backend/README.md) and the historical
[development guide](docs/guides/development.md) for further details.

## License

This project is licensed under the [MIT License](LICENSE).
