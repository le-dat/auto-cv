# Command: dev-setup

## Description

Validate environment variables, start local infrastructure (PostgreSQL + Redis via Docker), and verify the CV Optimizer backend is ready for development.

## Usage

```
/dev-setup
/dev-setup --check-only
/dev-setup --verbose
```

## What Claude must do

### Step 1 — Check environment

1. Read `.env.example` to get the expected variable list
2. Check if `.env` or `.env.local` exists:
   - If neither exists: create `.env.local` from `.env.example` template with empty values
   - If exists: verify all required keys are present
3. Report missing required variables:
   - `llm_provider` (openai/groq/claude)
   - `database_url` (postgresql+asyncpg://...)
   - `redis_url` (redis://...)
   - At least one LLM API key (`openai_api_key` OR `groq_api_key` OR `anthropic_api_key`)

### Step 2 — Check Docker availability

```bash
docker --version
docker compose version
```

- If Docker not installed: print manual setup instructions for PostgreSQL + Redis
- If Docker not running: prompt to start Docker Desktop

### Step 3 — Start infrastructure

```bash
docker compose up -d postgres redis
```

Wait for healthy checks:
```bash
docker compose ps
```

Expected output should show `healthy` for both postgres and redis.

### Step 4 — Verify connectivity

Test PostgreSQL:
```bash
docker compose exec postgres pg_isready -U user -d cvoptimizer
```

Test Redis:
```bash
docker compose exec redis redis-cli ping
```

Expected: `PONG`

### Step 5 — Verify Python dependencies

```bash
pip install -r requirements.txt 2>&1 | tail -5
python -c "from app.core.config import settings; print(f'llm={settings.llm_provider}, db={settings.database_url[:20]}...')"
```

### Step 6 — Report status

Print a table:

```
┌─────────────────┬────────────────────────────────┐
│ Component       │ Status                          │
├─────────────────┼────────────────────────────────┤
│ Docker          │ ✅ Running                      │
│ PostgreSQL      │ ✅ Healthy (cvoptimizer)        │
│ Redis           │ ✅ Healthy                      │
│ Python deps     │ ✅ Installed                    │
│ config.py       │ ✅ Loads from .env.local        │
│ LLM provider    │ ⚠️  Not configured (set key)   │
└─────────────────┴────────────────────────────────┘
```

### Step 7 — Next action

If `--check-only`: stop here.

Otherwise: if all green, print:
```
✅ Dev environment ready. Next: /new-feature parser pdf
```

If any red: list exact steps to fix.
