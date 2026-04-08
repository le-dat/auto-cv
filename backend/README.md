# CV Optimizer

AI-powered CV rewriting service that optimizes resumes for job descriptions.

## Quick Start

### Backend

```bash
cd backend
cp .env.example .env   # edit with your API keys
docker compose up --build
```

Backend runs at `http://localhost:8000`. Health check:
```bash
curl http://localhost:8000/api/v1/health
```

### Frontend

```bash
cd fe
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Submit a Job

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
```

## Tech Stack

| Layer | Backend | Frontend |
|-------|---------|----------|
| API | FastAPI | React 18 + Vite |
| Workflow | LangGraph | TypeScript |
| State | ARQ/Redis | Zustand |
| DB | PostgreSQL | — |
| Styling | — | TailwindCSS |

See [docs/architecture.md](docs/architecture.md) for full architecture.
