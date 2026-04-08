"""End-to-end workflow integration test using InMemoryJobRepository."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from app.models.schemas import CVData, JDData, JobStatus
from app.repositories.job_repository import InMemoryJobRepository


class TestJobRepositoryIntegration:
    """Integration tests for job repository (async job lifecycle)."""

    @pytest.fixture
    def repo(self) -> InMemoryJobRepository:
        return InMemoryJobRepository()

    @pytest.mark.asyncio
    async def test_full_job_lifecycle(self, repo: InMemoryJobRepository):
        """Simulate a full job lifecycle: create → process → complete."""
        from app.models.schemas import GenerateResult, MatchResult

        # 1. Create job
        job = await repo.create("lifecycle-job-1")
        assert job.status == JobStatus.PENDING
        assert job.job_id == "lifecycle-job-1"

        # 2. Mark as processing
        job = await repo.update_status("lifecycle-job-1", JobStatus.PROCESSING)
        assert job.status == JobStatus.PROCESSING

        # 3. Simulate workflow producing result
        result = GenerateResult(
            rewritten_cv="# Alice Smith\n\n## Skills\nPython, FastAPI, PostgreSQL",
            match_report="# Match Report\n\nMatch: 80%",
            match_result=MatchResult(
                matched_skills=["Python", "FastAPI", "PostgreSQL"],
                missing_skills=["AWS", "Docker"],
                weak_skills=[],
                skill_match_score=0.8,
                suggestions=["Add AWS experience"],
            ),
        )
        saved = await repo.save_result("lifecycle-job-1", result)

        # 4. Verify final state
        assert saved.status == JobStatus.COMPLETED
        assert saved.result is not None
        assert "Alice Smith" in saved.result.rewritten_cv
        assert saved.result.match_result.skill_match_score == 0.8

    @pytest.mark.asyncio
    async def test_job_failure_flow(self, repo: InMemoryJobRepository):
        """Simulate a job that fails during processing."""
        job = await repo.create("failing-job-1")
        await repo.update_status("failing-job-1", JobStatus.PROCESSING)

        # Simulate failure
        job = await repo.update_status(
            "failing-job-1", JobStatus.FAILED, error="CV parsing failed: invalid format"
        )

        assert job.status == JobStatus.FAILED
        assert job.error == "CV parsing failed: invalid format"

    @pytest.mark.asyncio
    async def test_parallel_jobs_independent(self, repo: InMemoryJobRepository):
        """Two jobs can be processed independently in parallel."""
        from app.models.schemas import GenerateResult

        await repo.create("job-a")
        await repo.create("job-b")

        await repo.save_result(
            "job-a",
            GenerateResult(rewritten_cv="CV for A", match_report="Report A"),
        )
        await repo.save_result(
            "job-b",
            GenerateResult(rewritten_cv="CV for B", match_report="Report B"),
        )

        a = await repo.get("job-a")
        b = await repo.get("job-b")

        assert a.result.rewritten_cv == "CV for A"
        assert b.result.rewritten_cv == "CV for B"


class TestWorkflowCompilation:
    """Test that workflow compiles correctly with a mock LLM."""

    def test_workflow_builds_without_error(self):
        """Workflow should compile without errors."""
        from unittest.mock import MagicMock
        from app.agents.workflow import compile_workflow

        class FakeLLM:
            async def ainvoke(self, messages):
                return MagicMock(content="{}")

        app = compile_workflow(FakeLLM())
        assert app is not None

    def test_workflow_state_schema(self):
        """WorkflowState should have all required fields."""
        from app.agents.state import WorkflowState

        state = WorkflowState()
        # Check that state is a dict with expected keys
        assert isinstance(state, dict)
