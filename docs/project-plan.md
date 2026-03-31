# Project Plan — CV Optimizer

Generated: 2026-03-31
Target: Milestone 1 — MVP

## Project Type
**AI Product** — FastAPI + LangGraph + OpenAI/Anthropic/Groq + FAISS + ARQ/Redis + PostgreSQL

## Gap Analysis

| Area | Status | Gap |
|------|--------|-----|
| Project structure | ❌ Nonexistent | `backend/` dir must be created from scratch |
| Env config | ⚠️ Generic template | `.env.example` is a wrong stack (Next.js/Clerk/Supabase) — must replace |
| LangGraph nodes | ❌ Not implemented | 6 nodes defined in spec — all need coding |
| Parser strategies | ❌ Not implemented | PDF, DOCX, Text — all need coding |
| Context providers | ❌ Not implemented | FAISS, Markdown, DB, HTTP — all need coding |
| ARQ worker | ❌ Not implemented | Worker is spec'd but not wired |
| Docker | ⚠️ Spec'd only | docker-compose.yml needs writing |

## 🛠 Automation Recommendations (New Commands)

- [x] **Command**: `/new-feature.md` — Reason: implementing new features (parsers, context providers, nodes) follows consistent patterns; a command that reads the spec and scaffolds the right files will prevent drift
- [x] **Command**: `/dev-setup.md` — Reason: local dev requires PostgreSQL + Redis + env vars; one command to validate/start infra saves hours of debugging
- [x] **Agent**: `cv-worker-agent.md` — Reason: LangGraph nodes follow a strict pattern (canonical example + test template); an agent ensures consistent quality across all 6 nodes

---

## Phase 0 — Project Scaffolding (~1 hour)

### Step 1: Create backend directory structure
- Run: `mkdir -p backend/app/{api/v1/{routes,middleware},agents/nodes,core,models,repositories,services/{parser,context},knowledge/skills,workers} backend/tests/{unit,integration}`
- Done when: `find backend -type d | wc -l` returns 25+ directories

### Step 2: Replace `.env.example` with CV Optimizer vars
- Run: overwrite `.env.example` with correct vars for FastAPI + ARQ + PostgreSQL + Redis + LLM providers
- Done when: `.env.example` contains `llm_provider`, `database_url`, `redis_url`, `context_providers` etc.

### Step 3: Create `requirements.txt`
- Run: write `requirements.txt` with all deps: fastapi, uvicorn, langgraph, langchain-openai, langchain-anthropic, langchain-groq, faiss-cpu, asyncpg, sqlalchemy[asyncio], arq, pydantic-settings, structlog, PyMuPDF, python-docx, pytest, pytest-asyncio, ruff
- Done when: `pip install -r requirements.txt` succeeds

### Step 4: Create `pyproject.toml` or `setup.py`
- Done when: project is installable via `pip install -e .`

---

## Phase 1 — Core Infrastructure (~2 days)

### Step 5: Implement `app/core/config.py`
- Run: write `app/core/config.py` with `pydantic_settings.BaseSettings` — all env vars from `.env.example`
- Done when: `python -c "from app.core.config import settings; print(settings.llm_provider)"` works

### Step 6: Implement `app/core/exceptions.py`
- Run: write all custom exceptions (`CVOptimizerError`, `ParseError`, `ValidationError`, etc.)
- Done when: `pytest tests/unit/test_exceptions.py` passes

### Step 7: Implement `app/core/llm_factory.py`
- Run: write `LLMFactory` with OpenAI/Groq/Claude factory
- Done when: `python -c "from app.core.llm_factory import LLMFactory; m = LLMFactory.create('openai'); print(type(m))"` returns `ChatOpenAI`

### Step 8: Implement `app/models/schemas.py`
- Run: write all Pydantic v2 schemas: `InputPayload`, `CVData`, `JDData`, `Experience`, `Education`, `MatchResult`, `GenerateResult`, `JobRecord`, `JobCreateResponse`, `JobStatusResponse`
- Done when: `python -c "from app.models.schemas import CVData, JDData, MatchResult; print('OK')"` works

### Step 9: Implement `app/repositories/job_repository.py`
- Run: write `AbstractJobRepository`, `InMemoryJobRepository`, `PostgresJobRepository`
- Done when: `pytest tests/unit/test_repository.py` passes with `InMemoryJobRepository`

---

## Phase 2 — Services Layer (~2 days)

### Step 10: Implement `app/services/parser/`
- Run: write `base.py` (ParserStrategy Protocol), `pdf_parser.py`, `docx_parser.py`, `text_parser.py`, `__init__.py` (ParserService with auto-registry)
- Done when: `python -c "from app.services.parser import ParserService; p = ParserService(); print('OK')"` works

### Step 11: Implement `app/services/context/base.py`
- Run: write `ContextChunk`, `KnowledgeDoc`, `ContextProvider` Protocol
- Done when: imports work without error

### Step 12: Implement `app/services/context/providers/`
- Run: write `faiss_provider.py`, `markdown_provider.py`, `db_provider.py`, `http_provider.py`
- Done when: `python -c "from app.services.context import context_registry; print('OK')"` works

### Step 13: Implement `app/services/context/__init__.py`
- Run: write `ContextRegistry` with lazy provider instantiation, `gather_docs`, `gather_chunks`
- Done when: `pytest tests/unit/test_context.py` passes

### Step 14: Implement `app/services/matcher.py`
- Run: write `MatcherService` with synonym expansion, skill scoring, `_suggestions`
- Done when: `pytest tests/unit/test_matcher.py` passes with mock LLM

---

## Phase 3 — LangGraph Agents (~2 days)

### Step 15: Implement `app/agents/state.py`
- Run: write `WorkflowState` TypedDict
- Done when: `python -c "from app.agents.state import WorkflowState; print(WorkflowState.__annotations__)"` works

### Step 16: Implement `app/agents/nodes/parse_node.py`
- Run: write `parse_node.run()` — format detection, text extraction, LLM structured extraction
- Done when: `pytest tests/unit/test_parse_node.py` passes

### Step 17: Implement `app/agents/nodes/validate_node.py`
- Run: write `validate_node.run()` — Pydantic validation
- Done when: `pytest tests/unit/test_validate_node.py` passes

### Step 18: Implement `app/agents/nodes/context_node.py`
- Run: write `context_node.run()` — calls `context_registry.gather_docs` + `gather_chunks`
- Done when: `pytest tests/unit/test_context_node.py` passes

### Step 19: Implement `app/agents/nodes/match_node.py`
- Run: write `match_node.run()` — calls `MatcherService.match()`
- Done when: `pytest tests/unit/test_match_node.py` passes

### Step 20: Implement `app/agents/nodes/rewrite_node.py`
- Run: write `rewrite_node.run()` — Anthropic document blocks for Claude, inline text for OpenAI/Groq
- Done when: `pytest tests/unit/test_rewrite_node.py` passes

### Step 21: Implement `app/agents/nodes/format_node.py`
- Run: write `format_node.run()` — assembles `GenerateResult`
- Done when: `pytest tests/unit/test_format_node.py` passes

### Step 22: Implement `app/agents/workflow.py`
- Run: write `build_workflow()` — LangGraph graph with all 6 nodes + conditional error edge
- Done when: `python -c "from app.agents.workflow import workflow; print('OK')"` works

---

## Phase 4 — API & Worker (~2 days)

### Step 23: Implement `app/api/v1/middleware/exception_handler.py`
- Run: write exception handler mapping domain errors to HTTP codes
- Done when: FastAPI returns correct codes for each exception type

### Step 24: Implement `app/api/v1/routes/jobs.py`
- Run: write `POST /jobs` (202, enqueue) and `GET /jobs/{job_id}` routes
- Done when: routes register without error and accept multipart/form-data

### Step 25: Implement `app/api/v1/routes/admin.py`
- Run: write `POST /admin/faiss/build` background trigger
- Done when: endpoint returns 202 and background task logs confirm

### Step 26: Implement `app/api/v1/routes/health.py`
- Run: write `GET /health`
- Done when: `curl http://localhost:8000/api/v1/health` returns 200

### Step 27: Implement `app/api/v1/router.py`
- Run: wire up all route modules with `/api/v1` prefix
- Done when: all routes accessible under `/api/v1/`

### Step 28: Implement `app/workers/cv_worker.py` + `arq_settings.py`
- Run: write `process_cv_job`, `enqueue_cv_job`, `WorkerSettings`
- Done when: worker starts without error: `arq app.workers.cv_worker.WorkerSettings`

### Step 29: Implement `app/main.py`
- Run: write FastAPI lifespan (Redis pool creation, FAISS index load), include router
- Done when: `uvicorn app.main:app --reload` starts without error

---

## Phase 5 — Docker + Knowledge Base (~1 day)

### Step 30: Write `docker-compose.yml`
- Run: write services: api, worker, postgres, redis
- Done when: `docker compose up` starts all 4 services and health checks pass

### Step 31: Write `Dockerfile`
- Run: write multi-stage Dockerfile for FastAPI + ARQ worker
- Done when: `docker build .` succeeds

### Step 32: Create `app/knowledge/` .md files
- Run: write `skills/backend.md`, `skills/frontend.md`, `skills/devops.md`, `skills/data_science.md`, `ats_keywords.md`, `cv_style_guide.md`
- Done when: `MarkdownDocProvider` loads all files on startup

---

## Phase 6 — Testing (~1 day)

### Step 33: Write `tests/conftest.py`
- Run: fixtures: `repo()`, `mock_llm()`, `sample_cv_data()`, `sample_jd_data()`
- Done when: `pytest --collect-only` finds all fixtures

### Step 34: Write unit tests for parsers
- Done when: `pytest tests/unit/test_parser.py -v` 100% pass

### Step 35: Write unit tests for matcher
- Done when: `pytest tests/unit/test_matcher.py -v` 100% pass

### Step 36: Write unit tests for all nodes
- Done when: `pytest tests/unit/test_nodes/ -v` 100% pass

### Step 37: Write integration test for full workflow
- Run: end-to-end test using `InMemoryJobRepository` + mock LLM
- Done when: `pytest tests/integration/ -v` pass

---

## Dependency Graph

```
Step 5  (config)
   ↓
Step 6  (exceptions)
   ↓
Step 7  (llm_factory)
   ↓
Step 8  (schemas)          Step 9 (repo)
   ↓                        ↓
Step 10 (parser)           Step 11 (context/base)
   ↓                        ↓
Step 12 (context providers) Step 13 (context registry)
   ↓                        ↓
Step 14 (matcher)          Step 15 (state)
   ↓                        ↓
Steps 16-21 (nodes)        ↓
   ↓                        ↓
Step 22 (workflow)          ↓
   ↓                        ↓
Steps 23-29 (API + worker) ↓
   ↓                        ↓
Steps 30-31 (Docker)        ↓
   ↓                        ↓
Steps 33-37 (tests)
```

---

## Checklist Format

```
[ ] Phase 0: Project Scaffolding
  [ ] Step 1: Create backend directory structure
  [ ] Step 2: Replace .env.example with CV Optimizer vars
  [ ] Step 3: Create requirements.txt
  [ ] Step 4: Create pyproject.toml
[ ] Phase 1: Core Infrastructure (~2 days)
  [ ] Step 5: Implement app/core/config.py
  [ ] Step 6: Implement app/core/exceptions.py
  [ ] Step 7: Implement app/core/llm_factory.py
  [ ] Step 8: Implement app/models/schemas.py
  [ ] Step 9: Implement app/repositories/job_repository.py
[ ] Phase 2: Services Layer (~2 days)
  [ ] Step 10: Implement app/services/parser/
  [ ] Step 11: Implement app/services/context/base.py
  [ ] Step 12: Implement app/services/context/providers/
  [ ] Step 13: Implement app/services/context/__init__.py
  [ ] Step 14: Implement app/services/matcher.py
[ ] Phase 3: LangGraph Agents (~2 days)
  [ ] Step 15: Implement app/agents/state.py
  [ ] Step 16: Implement parse_node.py
  [ ] Step 17: Implement validate_node.py
  [ ] Step 18: Implement context_node.py
  [ ] Step 19: Implement match_node.py
  [ ] Step 20: Implement rewrite_node.py
  [ ] Step 21: Implement format_node.py
  [ ] Step 22: Implement workflow.py
[ ] Phase 4: API & Worker (~2 days)
  [ ] Step 23: Implement exception_handler.py
  [ ] Step 24: Implement jobs.py routes
  [ ] Step 25: Implement admin.py routes
  [ ] Step 26: Implement health.py
  [ ] Step 27: Implement router.py
  [ ] Step 28: Implement cv_worker.py + arq_settings.py
  [ ] Step 29: Implement main.py
[ ] Phase 5: Docker + Knowledge Base (~1 day)
  [ ] Step 30: Write docker-compose.yml
  [ ] Step 31: Write Dockerfile
  [ ] Step 32: Create app/knowledge/ .md files
[ ] Phase 6: Testing (~1 day)
  [ ] Step 33: Write tests/conftest.py
  [ ] Step 34: Write unit tests for parsers
  [ ] Step 35: Write unit tests for matcher
  [ ] Step 36: Write unit tests for all nodes
  [ ] Step 37: Write integration test for full workflow
```
