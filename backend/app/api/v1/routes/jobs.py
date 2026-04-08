"""Job submission and status polling endpoints."""

import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.core.config import settings
from app.models.schemas import JobCreateResponse, JobStatusResponse
from app.repositories.job_repository import AbstractJobRepository, InMemoryJobRepository

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_repository() -> AbstractJobRepository:
    """Dependency that provides the job repository singleton."""
    return InMemoryJobRepository.get_instance()


async def _read_upload_file(file: UploadFile | None) -> tuple[str | None, str | None]:
    """Read upload file content and filename.

    Returns:
        Tuple of (text_content, filename)
    """
    if not file:
        return None, None
    content = await file.read()
    # Try to decode as text (for PDF/DOCX this won't be perfect but LLM can handle it)
    try:
        text = content.decode("utf-8", errors="replace")
    except Exception:
        try:
            text = content.decode("latin-1", errors="replace")
        except Exception:
            text = ""
            logging.warning(f"Failed to decode file {file.filename}, returning empty string")
    return text, file.filename


@router.post(
    "",
    response_model=JobCreateResponse,
    status_code=202,
    summary="Submit a CV + Job Description for rewriting",
)
async def create_job(
    request: Request,
    cv_file: UploadFile | None = File(None),
    cv_text: str | None = Form(None),
    jd_file: UploadFile | None = File(None),
    jd_text: str | None = Form(None),
    repository: AbstractJobRepository = Depends(get_repository),
) -> JobCreateResponse:
    """Submit a CV + JD for async processing.

    Returns immediately with 202 Accepted and a job_id for polling.
    """
    # Read file content if provided
    if cv_file:
        _validate_file_type(cv_file.filename)
        cv_file_text, cv_file_name = await _read_upload_file(cv_file)
        cv_text = cv_text or cv_file_text
    else:
        cv_file_name = None

    if jd_file:
        _validate_file_type(jd_file.filename)
        jd_file_text, jd_file_name = await _read_upload_file(jd_file)
        jd_text = jd_text or jd_file_text
    else:
        jd_file_name = None

    # Require at least text input
    if not cv_text and not cv_file:
        raise HTTPException(status_code=400, detail="Either cv_text or cv_file required")
    if not jd_text and not jd_file:
        raise HTTPException(status_code=400, detail="Either jd_text or jd_file required")

    # Create job record
    job_id = str(uuid.uuid4())
    record = await repository.create(job_id)

    # Enqueue to ARQ/Redis
    redis_client = getattr(request.app.state, "redis", None)
    if redis_client:
        from app.workers.arq_settings import enqueue_job
        await enqueue_job(
            redis_client,
            job_id,
            cv_text=cv_text,
            cv_file_name=cv_file_name,
            jd_text=jd_text,
            jd_file_name=jd_file_name,
        )
    else:
        # No Redis available - log warning but don't fail
        logging.warning(f"No Redis connection - job {job_id} not enqueued")

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
