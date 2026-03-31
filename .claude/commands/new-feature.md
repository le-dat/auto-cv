# Command: new-feature

## Description

Scaffold a new feature module for the CV Optimizer backend following the project's established patterns. Supports: parser strategies, context providers, and LangGraph nodes.

## Usage

```
/new-feature parser pdf
/new-feature context-provider faiss
/new-feature node match_node
/new-feature service matcher
```

## What Claude must do

### Step 1 — Identify feature type

Read `docs/architecture.md` and `docs/spec-doc.md` to understand the pattern for the requested type:

| Type | Template location | What to create |
|------|-----------------|----------------|
| `parser` | `docs/spec-doc.md` → Parser Strategy section | `app/services/parser/{name}_parser.py` + register in `__init__.py` |
| `context-provider` | `docs/spec-doc.md` → Context Providers section | `app/services/context/{name}_provider.py` + add to `_PROVIDER_FACTORIES` |
| `node` | `docs/spec-doc.md` → LangGraph Workflow section | `app/agents/nodes/{name}.py` with `run(state: WorkflowState) -> WorkflowState` |
| `service` | `docs/spec-doc.md` → Services section | `app/services/{name}.py` following service pattern |

### Step 2 — Read existing patterns

Before writing any code, read the canonical example for that type:

| Type | Read first |
|------|-----------|
| parser | `app/services/parser/pdf_parser.py` |
| context-provider | `app/services/context/faiss_provider.py` |
| node | `app/agents/nodes/parse_node.py` |
| service | `app/services/matcher.py` |

### Step 3 — Create the file

Follow the exact pattern from the canonical example. Key rules:

- **Parser**: must have `media_types`, `extensions`, `async extract_text(raw: bytes) -> str`
- **ContextProvider**: must implement Protocol, have `name`, `async is_ready() -> bool`, `async gather(query, top_k) -> list[ContextChunk]`
- **Node**: must have `async def run(state: WorkflowState) -> WorkflowState`, include `job_id` in all log calls
- **Service**: must accept `BaseChatModel` (not concrete class), accept `AbstractJobRepository` (not SQLAlchemy), use `structlog`

### Step 4 — Register/integrate

| Type | Integration step |
|------|-----------------|
| parser | Add `from app.services.parser.{name}_parser import {Name}Parser` + append `{Name}Parser()` to `_registry` in `__init__.py` |
| context-provider | Add `"name": lambda: {Name}Provider(...)` to `_PROVIDER_FACTORIES` in `__init__.py` + add `"name"` to `context_providers` in `.env` |
| node | Add `from app.agents.nodes.{name} import {name}_node` + add `("{name}", {name}_node.run)` to `build_workflow()` |
| service | No registration needed — services are imported by routes/nodes |

### Step 5 — Verify

After creating the file:

1. Run `ruff check app/services/parser/` or the appropriate path
2. If new parser: verify MIME type detection logic is correct
3. If new context provider: verify `is_ready()` returns `False` when data unavailable (graceful degradation)
4. Log a `job_id` in all async functions that touch the workflow

### Step 6 — Update docs

- Mark the relevant step as `✅` in `docs/project-plan.md`
- If this is a new type of feature, update `docs/architecture.md` to document the extension point
- Run `/checkpoint` after completing the feature
