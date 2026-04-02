"""Repository pattern for job storage — abstract + in-memory + postgres."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from app.models.schemas import GenerateResult, JobRecord, JobStatus


class AbstractJobRepository(ABC):
    """Abstract base for job repositories."""

    @abstractmethod
    async def create(self, job_id: str) -> JobRecord:
        """Create a new pending job record."""
        ...

    @abstractmethod
    async def get(self, job_id: str) -> JobRecord | None:
        """Retrieve a job record by ID."""
        ...

    @abstractmethod
    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        error: str | None = None,
    ) -> JobRecord | None:
        """Update the status of a job."""
        ...

    @abstractmethod
    async def save_result(
        self, job_id: str, result: GenerateResult
    ) -> JobRecord | None:
        """Save the result of a completed job."""
        ...


class InMemoryJobRepository(AbstractJobRepository):
    """In-memory job repository for tests and dev without a database."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}

    async def create(self, job_id: str) -> JobRecord:
        record = JobRecord(job_id=job_id, status=JobStatus.PENDING)
        self._jobs[job_id] = record
        return record

    async def get(self, job_id: str) -> JobRecord | None:
        return self._jobs.get(job_id)

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        error: str | None = None,
    ) -> JobRecord | None:
        record = self._jobs.get(job_id)
        if record is None:
            return None
        record.status = status
        record.error = error
        record.updated_at = datetime.utcnow()
        return record

    async def save_result(
        self, job_id: str, result: GenerateResult
    ) -> JobRecord | None:
        record = self._jobs.get(job_id)
        if record is None:
            return None
        record.result = result
        record.status = JobStatus.COMPLETED
        record.updated_at = datetime.utcnow()
        return record


# ── Postgres repository (prod) ──────────────────────────────────


class PostgresJobRepository(AbstractJobRepository):
    """PostgreSQL-backed job repository using SQLAlchemy async.

    Requires sqlalchemy[asyncio] and asyncpg.
    Wire via `database_url` in settings.
    """

    def __init__(self, session_factory: Any) -> None:
        self._session_factory = session_factory

    async def create(self, job_id: str) -> JobRecord:
        # Implementation deferred to when SQLAlchemy models are defined
        raise NotImplementedError("Use InMemoryJobRepository until models exist")

    async def get(self, job_id: str) -> JobRecord | None:
        raise NotImplementedError("Use InMemoryJobRepository until models exist")

    async def update_status(
        self,
        job_id: str,
        status: JobStatus,
        error: str | None = None,
    ) -> JobRecord | None:
        raise NotImplementedError("Use InMemoryJobRepository until models exist")

    async def save_result(
        self, job_id: str, result: GenerateResult
    ) -> JobRecord | None:
        raise NotImplementedError("Use InMemoryJobRepository until models exist")
