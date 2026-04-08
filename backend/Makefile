.PHONY: help install lint lint-fix test test-unit test-integration test-watch
.PHONY: infra-up infra-down infra-logs infra-ps infra-check
.PHONY: run worker run-all clean

PYTHON=python3
BACKEND_DIR=.
TEST_DIR=tests

## ─────────────────────────────────────────────
## Project Management
## ─────────────────────────────────────────────

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	@uv pip install -r requirements.txt

clean: ## Remove cache directories
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(BACKEND_DIR)/**/__pycache__ 2>/dev/null || true
	@rm -rf $(TEST_DIR)/__pycache__ 2>/dev/null || true

## ─────────────────────────────────────────────
## Infrastructure (Docker Compose)
## ─────────────────────────────────────────────

infra-up: ## Start PostgreSQL and Redis
	docker compose up -d postgres redis

infra-down: ## Stop infrastructure
	docker compose down

infra-logs: ## Tail infrastructure logs
	docker compose logs -f postgres redis

infra-ps: ## Show infrastructure status
	docker compose ps

infra-check: ## Verify PostgreSQL and Redis are healthy
	@echo "Checking PostgreSQL..." && docker compose exec postgres pg_isready -U user -d cvoptimizer
	@echo "Checking Redis..." && docker compose exec redis redis-cli ping
	@echo "All services healthy."

## ─────────────────────────────────────────────
## Code Quality
## ─────────────────────────────────────────────

lint: ## Lint Python code
	uv run ruff check $(BACKEND_DIR)/

lint-fix: ## Lint and fix Python code
	uv run ruff check $(BACKEND_DIR)/ --fix

test: ## Run all tests
	uv run pytest $(TEST_DIR)/

test-unit: ## Run unit tests only
	uv run pytest $(TEST_DIR)/unit/

test-integration: ## Run integration tests only
	uv run pytest $(TEST_DIR)/integration/

test-watch: ## Run tests with short traceback, stop on first failure
	uv run pytest $(TEST_DIR)/ -x --tb=short

## ─────────────────────────────────────────────
## Development
## ─────────────────────────────────────────────

run: ## Start FastAPI dev server
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

worker: ## Start ARQ worker
	cd $(BACKEND_DIR) && uv run arq app.workers.cv_worker.WorkerSettings

run-all: ## Start both API server and worker
	@echo "Starting FastAPI server and ARQ worker..."
	@trap 'kill 0' EXIT; \
	cd $(BACKEND_DIR) && (uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &) && \
	uv run arq app.workers.cv_worker.WorkerSettings & \
	wait
