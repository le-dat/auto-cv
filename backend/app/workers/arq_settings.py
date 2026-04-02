"""ARQ worker settings and job functions."""

from typing import Any

import arq
from arq.connections import RedisConnection

from app.core.llm_factory import LLMFactory
from app.models.schemas import JobStatus
from app.repositories.job_repository import AbstractJobRepository, InMemoryJobRepository


async def process_cv_job(
    ctx: dict,
    job_id: str,
    cv_text: str | None,
    cv_file_name: str | None,
    jd_text: str | None,
    jd_file_name: str | None,
) -> dict[str, Any]:
    """ARQ job function to process a CV optimization job.

    Args:
        ctx: ARQ context dict (contains redis, etc.).
        job_id: Unique job identifier.
        cv_text: Raw CV text input.
        cv_file_name: Original CV filename.
        jd_text: Raw JD text input.
        jd_file_name: Original JD filename.

    Returns:
        Dict with job_id, status, and result/error.
    """
    # Create repository for this job
    # TODO: Use PostgresJobRepository in production with proper session
    repository: AbstractJobRepository = InMemoryJobRepository()

    # Update status to processing
    await repository.update_status(job_id, JobStatus.PROCESSING)

    try:
        # Import here to avoid circular imports
        from app.agents.workflow import compile_workflow

        # Create LLM from settings
        llm = LLMFactory.create()

        # Compile workflow with LLM
        workflow = compile_workflow(llm)

        # Run the workflow
        initial_state = {
            "cv_text": cv_text,
            "jd_text": jd_text,
            "cv_file_name": cv_file_name,
            "jd_file_name": jd_file_name,
        }

        result = await workflow.ainvoke(initial_state)

        # Check for errors in result
        if result.get("error"):
            await repository.update_status(job_id, JobStatus.FAILED, error=result["error"])
            return {
                "job_id": job_id,
                "status": "failed",
                "error": result["error"],
            }

        # Save successful result
        if result.get("result"):
            await repository.save_result(job_id, result["result"])
            return {
                "job_id": job_id,
                "status": "completed",
                "result": result["result"].model_dump(),
            }
        else:
            await repository.update_status(job_id, JobStatus.FAILED, error="No result produced")
            return {
                "job_id": job_id,
                "status": "failed",
                "error": "No result produced by workflow",
            }

    except Exception as e:
        error_msg = f"Job processing failed: {str(e)}"
        await repository.update_status(job_id, JobStatus.FAILED, error=error_msg)
        return {
            "job_id": job_id,
            "status": "failed",
            "error": error_msg,
        }


class WorkerSettings:
    """ARQ worker settings."""

    redis_settings = arq.RedisSettings()
    functions = [process_cv_job]
    max_jobs = 10
    job_timeout = 120  # seconds


# Convenience function to enqueue a job
async def enqueue_job(
    redis: RedisConnection,
    job_id: str,
    cv_text: str | None = None,
    cv_file_name: str | None = None,
    jd_text: str | None = None,
    jd_file_name: str | None = None,
) -> str:
    """Enqueue a CV processing job.

    Args:
        redis: Redis connection.
        job_id: Unique job identifier.
        cv_text: Raw CV text input.
        cv_file_name: Original CV filename.
        jd_text: Raw JD text input.
        jd_file_name: Original JD filename.

    Returns:
        ARQ job ID.
    """
    job = await redis.enqueue_job(
        "process_cv_job",
        job_id,
        cv_text,
        cv_file_name,
        jd_text,
        jd_file_name,
        _job_id=job_id,
    )
    return job.job_id
