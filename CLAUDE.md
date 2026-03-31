# CLAUDE.md — CV Optimizer

> [ [Spec](docs/spec-doc.md) ] [ [Architecture](docs/architecture.md) ] [ [Plan](docs/project-plan.md) ] [ [Status](docs/project-status.md) ] [ [Changelog](docs/changelog.md) ]

> Claude reads this at the start of every session for core rules and tech stack.

---

## 1. Project Overview

**Product:** CV Optimizer — AI-powered CV rewriting service that optimizes resumes for job descriptions
**Core mechanic:** Submit CV + JD → async job → rewritten CV optimized for JD + match report
**Links:** [Detailed Specification](docs/spec-doc.md) | [System Architecture](docs/architecture.md)

---

## 2. Repository Structure

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── routes/
│   │   │   ├── jobs.py          # POST /jobs, GET /jobs/{id}
│   │   │   ├── admin.py          # FAISS rebuild trigger
│   │   │   └── health.py
│   │   ├── router.py
│   │   └── middleware/
│   │       ├── auth.py
│   │       ├── rate_limit.py
│   │       └── exception_handler.py
│   ├── agents/
│   │   ├── state.py              # WorkflowState TypedDict
│   │   ├── workflow.py            # LangGraph builder
│   │   └── nodes/
│   │       ├── parse_node.py
│   │       ├── validate_node.py
│   │       ├── context_node.py
│   │       ├── match_node.py
│   │       ├── rewrite_node.py
│   │       └── format_node.py
│   ├── core/
│   │   ├── config.py              # pydantic-settings
│   │   ├── llm_factory.py         # Provider factory
│   │   ├── exceptions.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── schemas.py             # Pydantic v2 schemas
│   │   └── db_models.py
│   ├── repositories/
│   │   └── job_repository.py      # Abstract + InMemory + Postgres
│   ├── services/
│   │   ├── parser/                # ParserStrategy pattern
│   │   ├── context/               # ContextProvider pattern
│   │   ├── matcher.py
│   │   └── rewriter.py
│   ├── knowledge/                 # .md files for LLM context
│   │   ├── skills/
│   │   └── ats_keywords.md
│   ├── workers/
│   │   ├── cv_worker.py
│   │   └── arq_settings.py
│   └── main.py                    # FastAPI lifespan
├── tests/
├── Dockerfile
└── docker-compose.yml
```

---

## 3. Core Logic

Detailed in [Project Specification](docs/spec-doc.md).

The CV Optimizer uses a LangGraph multi-agent workflow:
1. **parse** → extract structured CV/JD data from raw files/text
2. **validate** → Pydantic validation of extracted data
3. **context** → load knowledge docs + dynamic context (FAISS, DB, HTTP)
4. **match** → score skill match, identify gaps, generate suggestions
5. **rewrite** → rewrite CV using context + match analysis
6. **format** → assemble final result

Jobs are async: `POST /api/v1/jobs` returns `202`, worker processes via ARQ/Redis, poll `GET /api/v1/jobs/{id}`.

---

## 4. System Architecture

Detailed in [Architecture Design](docs/architecture.md).

### Core Coding Patterns

- **Parser Strategy**: `ParserStrategy` Protocol — add new format with one class + one registry line
- **Context Providers**: `ContextProvider` Protocol — pluggable via `CONTEXT_PROVIDERS` env var, zero code change
- **Repository Pattern**: `AbstractJobRepository` — `InMemoryJobRepository` for tests, `PostgresJobRepository` for prod
- **LLM Abstraction**: All services accept `BaseChatModel` — never concrete class, enables mock injection

---

## 5. Environment Variables

```bash
# LLM
llm_provider=openai                    # openai | groq | claude
openai_api_key=
openai_model=gpt-4o-mini
groq_api_key=
groq_model=llama3-70b-8192
anthropic_api_key=
claude_model=claude-3-5-haiku-20241022

# Infrastructure
database_url=postgresql+asyncpg://user:pass@localhost/cvoptimizer
redis_url=redis://localhost:6379

# Input
max_file_size_mb=10
allowed_input_types=["pdf", "docx", "txt", "text", "md"]

# Context providers (enable/disable via this list)
context_providers=["markdown", "faiss"]
context_top_k=5
knowledge_dir=app/knowledge
knowledge_max_docs=10
db_context_enabled=false
http_context_url=

# Limits
max_concurrent_jobs=5
job_timeout_seconds=120
debug=false
log_level=INFO
```

---

## 6. Coding Patterns & Conventions

### Commit convention

```
feat: add new feature
fix: handle edge case
chore: update dependencies
test: add test coverage
docs: update documentation
```

### Python/FastAPI rules

- All services use async/await
- All services accept `BaseChatModel` (LangChain abstraction), never concrete LLM classes
- All services accept `AbstractJobRepository`, never SQLAlchemy directly
- All config via `settings` in `core/config.py` — never read `.env` directly
- Settings use `pydantic_settings.BaseSettings`
- All schemas use Pydantic v2 with `model_validate`

### Error handling pattern

```python
# Custom exceptions — always extend CVOptimizerError
class CVOptimizerError(Exception): pass
class ParseError(CVOptimizerError): pass
class ValidationError(CVOptimizerError): pass
class ContextError(CVOptimizerError): pass
class MatchError(CVOptimizerError): pass
class RewriteError(CVOptimizerError): pass
class JobNotFoundError(CVOptimizerError): pass
```

### Testing pattern

```python
# All tests use InMemoryJobRepository — no DB or Redis needed
@pytest.fixture
def repo(): return InMemoryJobRepository()

# Mock LLM injected via fixture
@pytest.fixture
def mock_llm():
    m = AsyncMock()
    m.ainvoke.return_value.content = '["Highlight cloud experience"]'
    return m

# Pass empty context in unit tests
result = await MatcherService(llm=mock_llm).match(cv, jd, context=[])
```

---

## 7. Testing & Quality

**Essential Commands:**

- `pytest tests/` — Run all tests
- `ruff check backend/` — Lint Python code

---

## 8. Security & Safety

Full checklist in [Architecture](docs/architecture.md).

- Never fabricate experience, skills, or achievements not in original CV
- Never commit `.env` — use `.env.example` only
- File size and type validated at API boundary before enqueuing
- All routes prefixed `/api/v1/`
- Redis pool created once in lifespan, shared via `app.state.redis`

---

## 9. Constraints & Rules (non-negotiable)

1. **Never** push directly to `main` — always feature branch + PR
2. **Never** commit `.env` or `.env.local` files
3. **Never** use `synchronize: true` in SQLAlchemy DataSource (production data loss risk)
4. **Never** delete migration files — always roll forward
5. **Never** fabricate experience, skills, or achievements not in original CV
6. **Always** use `/checkpoint` after completing a feature or ending a work session
7. **Always** update `docs/project-plan.md` via `/checkpoint` to track progress
8. Critical logic changes require a second pair of eyes (or explicit test coverage) before merge
9. All routes use `/api/v1/` prefix from day one
10. All services accept `BaseChatModel`, never concrete LLM class

---

## 10. Available Slash Commands

| Command | When to use |
| :--- | :--- |
| `/new-feature [name]` | Start any new feature (plans before coding) |
| `/commit` | Create a well-formatted git commit |
| `/pr` | Create a GitHub Pull Request |
| `/checkpoint` | Unified sync: update changelog + status + plan progress |
| `/generate-plan` | Create a detailed implementation plan |

---

## 11. Connected MCPs

| MCP | Purpose |
|-----|---------|
| `github` | Create issues, PRs, search code |

---

## 12. Architectural Decisions

| Decision | Reason |
|----------|--------|
| LangGraph for workflow orchestration | Multi-agent state machine with built-in retry and branching |
| ARQ + Redis for job queue | Async-native, simple, Redis-backed — required for job persistence |
| FAISS for vector similarity | Local CPU-first, cost-effective, persists to disk |
| Parser Strategy pattern | Add new format with one class + one registry line, zero other changes |
| Context Provider protocol | Pluggable context via env var — enable/disable providers without code changes |
| Repository pattern | `InMemoryJobRepository` for tests, `PostgresJobRepository` for prod |
| LLM factory abstraction | Switch providers via config, mock injection in tests |
| Markdown knowledge files | Claude reads `.md` files as document blocks — structured, no chunking |

---

## 13. Known Issues

| Issue | Workaround |
|-------|------------|
| FAISS index must be rebuilt via admin endpoint after initial setup | Call `POST /api/v1/admin/faiss/build` after first completed jobs |
| DB context provider disabled until past job data exists | Enable via `db_context_enabled=true` in `.env` |
