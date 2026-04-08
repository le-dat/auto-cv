# Architecture

## System Overview

CV Optimizer uses a multi-agent LangGraph workflow orchestrated by FastAPI, with async job processing via ARQ/Redis.

## Tech Stack

### Backend

| Layer | Technology |
|-------|------------|
| API | FastAPI (async, OpenAPI auto-docs) |
| Workflow | LangGraph (multi-agent state machine) |
| LLM | LangChain `BaseChatModel` (OpenAI / Groq / Anthropic) |
| Vector store | FAISS (local, CPU) |
| Job queue | ARQ (Redis-backed, async-native) |
| Database | PostgreSQL + asyncpg |
| ORM | SQLAlchemy 2.0 async |
| Cache | Redis |
| PDF parsing | PyMuPDF |
| DOCX parsing | python-docx |
| Settings | pydantic-settings |

### Frontend

| Layer | Technology |
|-------|------------|
| Framework | React 18 + Vite |
| Language | TypeScript (strict) |
| State | Zustand |
| HTTP | Axios |
| Styling | TailwindCSS (dark theme) |
| Routing | React Router DOM |
| File upload | react-dropzone |
| Forms | React Hook Form + Zod |
| Markdown | react-markdown |
| Icons | Lucide React |

## Project Structure

```
auto-cv2/                          # Monorepo (FE + BE)
│
├── backend/                       # FastAPI backend
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── routes/
│   │   │   │   ├── jobs.py        # POST /jobs, GET /jobs/{id}
│   │   │   │   ├── admin.py       # FAISS rebuild trigger
│   │   │   │   └── health.py
│   │   │   ├── router.py
│   │   │   └── middleware/
│   │   │       ├── auth.py
│   │   │       ├── rate_limit.py
│   │   │       └── exception_handler.py
│   │   ├── agents/
│   │   │   ├── state.py           # WorkflowState TypedDict
│   │   │   ├── workflow.py         # LangGraph builder
│   │   │   └── nodes/
│   │   │       ├── parse_node.py
│   │   │       ├── validate_node.py
│   │   │       ├── context_node.py
│   │   │       ├── match_node.py
│   │   │       ├── rewrite_node.py
│   │   │       └── format_node.py
│   │   ├── core/
│   │   │   ├── config.py           # pydantic-settings
│   │   │   ├── llm_factory.py      # Provider factory
│   │   │   ├── exceptions.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   │   ├── schemas.py          # Pydantic v2 schemas
│   │   │   └── db_models.py
│   │   ├── repositories/
│   │   │   └── job_repository.py   # Abstract + InMemory + Postgres
│   │   ├── services/
│   │   │   ├── parser/             # ParserStrategy pattern
│   │   │   ├── context/            # ContextProvider pattern
│   │   │   ├── matcher.py
│   │   │   └── rewriter.py
│   │   ├── knowledge/              # .md files for LLM context
│   │   │   ├── skills/
│   │   │   └── ats_keywords.md
│   │   ├── workers/
│   │   │   ├── cv_worker.py
│   │   │   └── arq_settings.py
│   │   └── main.py                 # FastAPI lifespan
│   ├── tests/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── fe/                            # React frontend
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css               # Tailwind + dark theme
│   │   ├── lib/
│   │   │   └── api.ts              # Axios client + API functions
│   │   ├── store/
│   │   │   └── jobStore.ts         # Zustand store
│   │   ├── hooks/
│   │   │   └── usePolling.ts       # Job status polling hook
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx      # File/text upload form
│   │   │   └── ResultsPage.tsx     # Poll + display results
│   │   ├── components/
│   │   │   ├── layout/Header.tsx
│   │   │   ├── upload/FileDropzone.tsx
│   │   │   └── results/ScoreDisplay.tsx
│   │   └── types/
│   │       └── api.ts              # TypeScript types matching BE schemas
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── .env.example
│
├── docs/
└── CLAUDE.md
```

## Core Patterns

### Parser Strategy

Every input format implements `ParserStrategy`. `ParserService` auto-detects format and delegates. Adding a new format requires only one new class + one registry entry.

### Context Providers

Pluggable `ContextProvider` protocol. Active providers configured via `CONTEXT_PROVIDERS` env var — no code change to add/remove. Providers: FAISS, DB, HTTP, Markdown.

### Repository Pattern

Services depend on `AbstractJobRepository`. `InMemoryJobRepository` used in all tests — no DB needed. `PostgresJobRepository` used in production.

### LLM Abstraction

All services accept `BaseChatModel` — never a concrete class. Enables mock injection in tests and provider switching via factory.

## Security

- Never commit `.env` files
- File size and type validated at API boundary
- Redis pool shared via lifespan, not per-request
- Auth middleware on admin routes

## Extension Guide

- **New input format**: 1 class + 1 registry line + env update
- **New context provider**: 1 class + 1 factory entry + env update
- **New knowledge data**: drop `.md` file into `app/knowledge/`

## Docker

```bash
# Backend
cd backend && docker compose up --build

# Frontend (dev)
cd fe && npm install && npm run dev
```

Requires PostgreSQL and Redis containers for backend.
