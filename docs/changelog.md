# Changelog

## 2026-04-03 — Session 7 (Review Fixes)

### Fixed
- **`job_repository.py`** — InMemoryJobRepository singleton so status persists across API/worker
- **`arq_settings.py`** — WorkerSettings uses `settings.redis_url`, added `max_retries=3`
- **`jobs.py`** — Actually enqueues to Redis, reads UploadFile content, uses singleton repository
- **`workflow.py`** — Removed redundant `add_edge` calls conflicting with conditional edges
- **`context_node.py`** — Path resolution using `Path` instead of nested `dirname`
- **`arq_settings.py`** — Fixed `ArqRedis` import, `RedisSettings.from_dsn()` for Redis URL

### Added
- **`.gitignore`** — Python, venv, .env, IDE, test cache, FAISS index files
- **`backend/app/api/v1/routes/jobs.py`** — POST /jobs (202), GET /jobs/{id} with multipart/form support
- **`backend/app/api/v1/routes/admin.py`** — POST /admin/faiss/build trigger
- **`backend/app/api/v1/routes/health.py`** — GET /health endpoint
- **`backend/app/api/v1/router.py`** — Aggregates all route modules under /api/v1
- **`backend/app/api/v1/middleware/auth.py`** — Auth middleware placeholder (TODO: implement)
- **`backend/app/api/v1/middleware/rate_limit.py`** — Rate limiting middleware placeholder (TODO: implement)
- **`backend/app/api/v1/middleware/exception_handler.py`** — Catches CVOptimizerError → JSON responses
- **`backend/app/agents/state.py`** — WorkflowState TypedDict for LangGraph
- **`backend/app/agents/workflow.py`** — build_workflow() with parse→validate→context→match→rewrite→format
- **`backend/app/agents/nodes/parse_node.py`** — LLM-based CV/JD text extraction
- **`backend/app/agents/nodes/validate_node.py`** — Pydantic validation of extracted data
- **`backend/app/agents/nodes/context_node.py`** — Markdown/FAISS/DB/HTTP context loading
- **`backend/app/agents/nodes/match_node.py`** — LLM-based skill matching analysis
- **`backend/app/agents/nodes/rewrite_node.py`** — CV rewriting with context + match analysis
- **`backend/app/agents/nodes/format_node.py`** — Final GenerateResult assembly
- **`backend/app/services/parser/__init__.py`** — ParserService with PDF/DOCX/Text Strategy pattern
- **`backend/app/services/context/__init__.py`** — ContextProvider base + MarkdownDocProvider, FAISSContextProvider, DBContextProvider, HTTPContextProvider stubs
- **`backend/app/services/matcher.py`** — MatcherService for ATS skill matching
- **`backend/app/services/rewriter.py`** — RewriterService for CV rewriting
- **`backend/app/workers/arq_settings.py`** — process_cv_job ARQ function + WorkerSettings
- **`backend/app/workers/cv_worker.py`** — ARQ worker entry point
- **`backend/app/main.py`** — FastAPI app with Redis lifespan, CORS, middleware stack
- **`backend/app/knowledge/ats_keywords.md`** — ATS keyword guide
- **`backend/app/knowledge/cv_style_guide.md`** — CV writing style guide

### Changed
- **`backend/app/core/config.py`** — Fixed mutable defaults: `allowed_input_types` and `context_providers` use `default_factory`
- **`backend/app/core/llm_factory.py`** — Now wires `settings.openai_api_key`, `settings.openai_model`, etc. as defaults
- **`backend/app/models/schemas.py`** — `JobStatus` now uses `StrEnum` instead of `str, Enum`
- **`backend/app/services/parser/__init__.py`** — Removed unused `abc` imports
- **`requirements.txt`** — Added `python-multipart>=0.0.9` for FastAPI file uploads

### Fixed
- **`backend/app/agents/nodes/format_node.py`** — Syntax error in list comprehension (unpacking with `or`)

---

## 2026-04-01 — Session 6

### Added
- **`.claude/commands/new-feature.md`** — Scaffolds parser strategies, context providers, nodes, and services following project patterns
- **`.claude/commands/dev-setup.md`** — Validates env, starts PostgreSQL + Redis via Docker, checks connectivity
- **`.claude/agents/cv-worker-agent.md`** — Implements LangGraph workflow nodes with canonical examples, test templates, and quality rules

---

## 2026-03-31 — Session 4

### Added
- **docs/project-plan.md** — Generated full 37-step implementation plan across 6 phases

### Changed
- **docs/project-status.md** — Updated with session 3 history entry

---

## 2026-03-31 — Session 3

### Added
- **CLAUDE.md** — Fully populated from `roadmap.md`: project name, repo structure, core logic, env vars, coding patterns, constraints, architectural decisions
- **docs/spec-doc.md** — API endpoints, data schemas, LangGraph workflow overview, context providers, CLI reference
- **docs/architecture.md** — Tech stack, project structure, core patterns (Parser Strategy, Context Providers, Repository, LLM Abstraction), security, Docker/extension guide

### Changed
- **docs/project-plan.md** — Converted to milestone format with goals checklist
- **docs/project-status.md** — Updated with current phase and next steps
- **docs/changelog.md** — Added session entries

---

## 2026-03-31 — Session 1

- Initial project specification created
- Project structure defined in `roadmap.md`
