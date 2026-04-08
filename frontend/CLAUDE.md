# CLAUDE.md — CV Optimizer Frontend

> FE reads this alongside root `CLAUDE.md` for frontend-specific rules.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 18 + Vite |
| Language | TypeScript (strict) |
| State | Zustand |
| HTTP | Axios |
| Styling | TailwindCSS (dark theme) |
| Routing | React Router DOM |
| Forms | React Hook Form + Zod |
| File upload | react-dropzone |
| Markdown | react-markdown |
| Icons | Lucide React |

## Key Conventions

- **API base URL**: configured via `VITE_API_BASE_URL` env var (defaults to `http://localhost:8000`)
- **API types**: defined in `src/types/api.ts` — must match BE Pydantic schemas exactly
- **Dark theme**: all colors via CSS variables defined in `src/index.css` — never use hardcoded hex
- **No fabrications**: UI never shows data that doesn't come from the BE API

## Environment Variables

```bash
VITE_API_BASE_URL=http://localhost:8000   # BE API base URL
```

## Available Scripts

```bash
npm run dev    # Start Vite dev server (port 5173)
npm run build  # Build for production
npm run lint   # ESLint
```

## API Contract

FE communicates with BE via REST:

```
POST /api/v1/jobs
  multipart/form-data: cv_file|cv_text, jd_file|jd_text
  → { job_id, status, message }

GET /api/v1/jobs/{job_id}
  → { job_id, status, result: { cv_markdown, match_result, ... } | null, error }

GET /api/v1/health
  → { status: "ok" }
```

## File Structure

```
src/
├── main.tsx              # BrowserRouter setup
├── App.tsx               # Routes: / and /jobs/:jobId
├── index.css             # Tailwind + CSS variables (dark theme)
├── lib/api.ts            # Axios client + API functions
├── store/jobStore.ts     # Zustand store (job state + polling)
├── hooks/usePolling.ts   # Polling hook (2s interval)
├── pages/
│   ├── UploadPage.tsx    # File/text upload → POST /api/v1/jobs
│   └── ResultsPage.tsx   # Poll GET /api/v1/jobs/:id → display
├── components/
│   ├── layout/Header.tsx
│   ├── upload/FileDropzone.tsx
│   └── results/ScoreDisplay.tsx
└── types/api.ts          # TypeScript types matching BE schemas
```

## Color Variables (Dark Theme)

```css
--text: #9ca3af           /* Secondary text */
--text-h: #f3f4f6         /* Headings */
--bg: #0f1117             /* Background */
--border: #1e1f27         /* Borders */
--code-bg: #1a1c24        /* Card/code backgrounds */
--accent: #8b5cf6         /* Primary accent (purple) */
--accent-bg: rgba(139, 92, 246, 0.1)
--accent-border: rgba(139, 92, 246, 0.4)
```

## Rules

1. Never hardcode colors — always use CSS variables
2. Never call BE APIs directly — use `src/lib/api.ts` functions
3. Never store job results in FE state longer than needed — clear on unmount
4. All API response types must be defined in `src/types/api.ts`
5. Polling interval: 2 seconds (defined in `usePolling.ts`)
