"""Unit tests for job repository (InMemory implementation)."""

import pytest

from app.models.schemas import GenerateResult, JobStatus, MatchResult
from app.repositories.job_repository import (
    AbstractJobRepository,
    InMemoryJobRepository,
)


class TestInMemoryJobRepository:
    """Tests for InMemoryJobRepository."""

    @pytest.fixture
    def repo(self) -> InMemoryJobRepository:
        return InMemoryJobRepository()

    @pytest.mark.asyncio
    async def test_create_returns_pending_job(self, repo: InMemoryJobRepository):
        record = await repo.create("job-1")
        assert record.job_id == "job-1"
        assert record.status == JobStatus.PENDING
        assert record.created_at is not None

    @pytest.mark.asyncio
    async def test_get_returns_existing_job(self, repo: InMemoryJobRepository):
        await repo.create("job-1")
        record = await repo.get("job-1")
        assert record is not None
        assert record.job_id == "job-1"

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing_job(self, repo: InMemoryJobRepository):
        record = await repo.get("nonexistent")
        assert record is None

    @pytest.mark.asyncio
    async def test_update_status_changes_status(
        self, repo: InMemoryJobRepository
    ):
        await repo.create("job-1")
        record = await repo.update_status("job-1", JobStatus.PROCESSING)
        assert record is not None
        assert record.status == JobStatus.PROCESSING

    @pytest.mark.asyncio
    async def test_update_status_sets_error(
        self, repo: InMemoryJobRepository
    ):
        await repo.create("job-1")
        record = await repo.update_status(
            "job-1", JobStatus.FAILED, error="Something went wrong"
        )
        assert record is not None
        assert record.status == JobStatus.FAILED
        assert record.error == "Something went wrong"

    @pytest.mark.asyncio
    async def test_save_result_sets_completed(
        self, repo: InMemoryJobRepository
    ):
        await repo.create("job-1")
        result = GenerateResult(
            rewritten_cv="# Alice Smith\n\n## Skills\nPython",
            match_report="Match score: 80%",
            match_result=MatchResult(
                matched_skills=["Python"],
                missing_skills=["AWS"],
                weak_skills=[],
                skill_match_score=0.8,
                suggestions=[],
            ),
        )
        record = await repo.save_result("job-1", result)
        assert record is not None
        assert record.status == JobStatus.COMPLETED
        assert record.result is not None
        assert record.result.rewritten_cv.startswith("# Alice Smith")

    @pytest.mark.asyncio
    async def test_save_result_returns_none_for_missing_job(
        self, repo: InMemoryJobRepository
    ):
        result = GenerateResult(rewritten_cv="test", match_report="test")
        record = await repo.save_result("nonexistent", result)
        assert record is None

    @pytest.mark.asyncio
    async def test_singleton_instance_persists(
        self, repo: InMemoryJobRepository
    ):
        """Singleton instance should be the same object across calls."""
        instance1 = InMemoryJobRepository.get_instance()
        instance2 = InMemoryJobRepository.get_instance()
        assert instance1 is instance2


class TestAbstractJobRepository:
    """Verify InMemoryJobRepository implements AbstractJobRepository."""

    def test_inmemory_implements_abstract(self):
        repo = InMemoryJobRepository()
        assert isinstance(repo, AbstractJobRepository)
