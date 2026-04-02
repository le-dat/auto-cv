"""Job submission and status polling endpoints."""

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.models.schemas import JobCreateResponse, JobStatusResponse
from app.repositories.job_repository import AbstractJobRepository, InMemoryJobRepository

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_repository() -> AbstractJobRepository:
    """Dependency that provides the job repository."""
    # TODO: Wire up PostgresJobRepository in production
    return InMemoryJobRepository()


@router.post(
    "",
    response_model=JobCreateResponse,
    status_code=202,
    summary="Submit a CV + Job Description for rewriting",
)
async def create_job(
    cv_file: UploadFile | None = File(None),
    cv_text: str | None = Form(None),
    jd_file: UploadFile | None = File(None),
    jd_text: str | None = Form(None),
    repository: AbstractJobRepository = Depends(get_repository),
) -> JobCreateResponse:
    """Submit a CV + JD for async processing.

    Returns immediately with 202 Accepted and a job_id for polling.
    """
    # Validate file types if provided
    if cv_file:
        _validate_file_type(cv_file.filename)
    if jd_file:
        _validate_file_type(jd_file.filename)

    # Create job record
    job_id = str(uuid.uuid4())
    record = await repository.create(job_id)

    # TODO: Enqueue to ARQ/Redis for async processing
    # from app.workers.arq_settings import enqueue_job
    # await enqueue_job(job_id, cv_text, jd_text, cv_file, jd_file)

    return JobCreateResponse(
        job_id=record.job_id,
        status=record.status,
        message=f"Job queued. Poll GET /api/v1/jobs/{job_id}",
    )


@router.get(
    "/{job_id}",
    response_model=JobStatusResponse,
    summary="Poll job status and retrieve result",
)
async def get_job_status(
    job_id: str,
    repository: AbstractJobRepository = Depends(get_repository),
) -> JobStatusResponse:
    """Poll for job status. Returns result when complete."""
    record = await repository.get(job_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobStatusResponse(
        job_id=record.job_id,
        status=record.status,
        created_at=record.created_at,
        updated_at=record.updated_at,
        result=record.result,
        error=record.error,
    )


def _validate_file_type(filename: str | None) -> None:
    """Validate that file extension is allowed."""
    if not filename:
        return
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.allowed_input_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{ext} not allowed. Allowed: {settings.allowed_input_types}",
        )
