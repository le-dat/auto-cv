# CV Optimizer — Specification

**Goal**: `text/PDF/DOCX(CV) + text/PDF/DOCX(JD)` → rewritten CV optimized for JD + match report.
**Flow**: `POST /api/v1/jobs` (202) → poll `GET /api/v1/jobs/{id}` → done.

> ⚠️ Never fabricate experience, skills, or achievements not in original CV.
> ⚠️ All routes prefixed `/api/v1/` from day one — no versioning = breaking changes.
> ⚠️ Never commit `.env` — use `.env.example` only.

---

## Stack

| Layer | Library | Notes |
|---|---|---|
| API | FastAPI | async, OpenAPI auto-docs |
| Workflow | LangGraph | multi-agent state machine |
| LLM abstraction | LangChain `BaseChatModel` | never use concrete class directly |
| LLM providers | OpenAI / Groq / Anthropic | switched via factory |
| Embeddings | `text-embedding-3-small` | cost-effective |
| Vector store | faiss-cpu | local first |
| PDF | PyMuPDF (fitz) | fast + accurate |
| DOCX | python-docx | via parser strategy |
| Plain text | built-in | via parser strategy |
| Schema | Pydantic v2 | runtime + static |
| Settings | pydantic-settings | `.env` loader |
| Job queue | ARQ | async-native, Redis-backed — **required** |
| DB | PostgreSQL + asyncpg | job + result persistence — **required** |
| ORM | SQLAlchemy 2.0 async | repository pattern |
| Cache | Redis | job status, embedding cache — **required** |
| Logging | structlog | structured JSON, keyed by `job_id` |
| Testing | pytest + pytest-asyncio | unit + integration |

> ⚠️ PostgreSQL + Redis are **not optional** — without them you lose job persistence across restarts, can't scale workers, and can't implement past-CV memory.

---

## API Endpoints

### `POST /api/v1/jobs`

Submit a CV + Job Description for rewriting. Returns immediately with `202 Accepted`.

**Request**: `multipart/form-data`
- `cv_file`: PDF/DOCX/TXT file (optional)
- `cv_text`: raw CV text (optional, mutually exclusive with cv_file)
- `jd_file`: PDF/DOCX/TXT file (optional)
- `jd_text`: raw JD text (optional, mutually exclusive with jd_file)

**Response**: `{ "job_id": "...", "status": "pending", "message": "Poll GET /api/v1/jobs/{id}" }`

### `GET /api/v1/jobs/{job_id}`

Poll job status and retrieve result.

**Response**:
```json
{
  "job_id": "...",
  "status": "done",
  "result": {
    "cv_markdown": "...",
    "match_result": { "score": 78.5, "matching_skills": [...], "missing_skills": [...] },
    "processing_time_ms": 14200,
    "llm_model_used": "openai",
    "context_sources": ["knowledge:ats_keywords.md", "knowledge:cv_style_guide.md"]
  }
}
```

### `POST /api/v1/admin/faiss/build`

Trigger FAISS index rebuild from all completed jobs. Background task.

### `GET /api/v1/health`

Health check endpoint.

---

## Data Schemas

### `InputPayload`
```python
raw: bytes | None = None   # file upload
text: str | None = None    # direct text input
filename: str = "input.txt"
content_type: str | None = None
```

### `CVData`
```python
name: str
email: EmailStr | None
phone: str | None
linkedin_url: str | None
summary: str | None
skills: list[str]
experience: list[Experience]  # company, title, start_date, end_date, bullets
education: list[Education]     # institution, degree, field, graduation_year
projects: list[str]
certifications: list[str]
languages: list[str]
```

### `JDData`
```python
title: str
company_name: str | None
location: str | None
job_type: "full-time" | "part-time" | "contract" | "internship" | None
required_skills: list[str]
preferred_skills: list[str]
responsibilities: list[str]
experience_required: str | None
salary_range: str | None
```

### `MatchResult`
```python
score: float  # 0-100
matching_skills: list[str]
missing_skills: list[str]
strong_skills: list[str]
suggestions: list[str]
ats_keywords: list[str]
```

### `GenerateResult`
```python
cv_markdown: str
match_result: MatchResult
processing_time_ms: int
llm_model_used: str
context_sources: list[str]
```

### `JobRecord`
```python
id: str
status: "pending" | "processing" | "done" | "failed"
created_at: datetime
updated_at: datetime
result: GenerateResult | None
error: str | None
```

---

## LangGraph Workflow

```
parse → validate → context → match → rewrite → format → END
              ↓ (error)
             END
```

### Nodes

1. **parse_node**: Detects format, extracts plain text, LLM extracts structured CVData/JDData
2. **validate_node**: Pydantic validation, guards against corrupted LLM JSON
3. **context_node**: Loads `.md` knowledge docs + dynamic context chunks (FAISS, DB)
4. **match_node**: Scores skill match, identifies gaps, generates suggestions
5. **rewrite_node**: Rewrites CV using context + match analysis (never fabricates)
6. **format_node**: Assembles final `GenerateResult`

---

## Context Providers

| Provider | Source | When Active |
|----------|--------|-------------|
| FAISSContextProvider | Vector similarity on past CVs/JDs | Always (if index built) |
| MarkdownDocProvider | `.md` files in `app/knowledge/` | Always |
| DBContextProvider | Past successful rewrites from PostgreSQL | `db_context_enabled=true` |
| HTTPContextProvider | External enrichment API | `http_context_url` set |

Enable/disable via `context_providers` in `.env` — zero code change.

---

## Environment Variables

See [`.env.example`](../.env.example) for full list.

Key variables:
- `llm_provider`: `openai` | `groq` | `claude`
- `database_url`: PostgreSQL connection string
- `redis_url`: Redis connection string
- `context_providers`: list of active context providers
- `max_file_size_mb`: upload size limit (default: 10)
- `allowed_input_types`: `["pdf", "docx", "txt", "text", "md"]`

---

## CLI

```bash
# File upload
curl -X POST http://localhost:8000/api/v1/jobs \
  -F "cv_file=@my_cv.pdf" -F "jd_file=@jd.docx"

# Plain text
curl -X POST http://localhost:8000/api/v1/jobs \
  -F "cv_text=John Doe, Python engineer..." \
  -F "jd_text=We are looking for a senior backend..."

# Poll
curl http://localhost:8000/api/v1/jobs/abc-123

# Trigger FAISS rebuild
curl -X POST http://localhost:8000/api/v1/admin/faiss/build
```

---

## Docker

```bash
docker compose up --build
```

Without Docker:
```bash
uvicorn app.main:app --reload &
arq app.workers.cv_worker.WorkerSettings
```
