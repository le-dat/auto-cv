"""CV worker module — ARQ worker entry point."""

# This module serves as the entry point for the ARQ worker.
# Run with: arq app.workers.cv_worker.WorkerSettings

from app.workers.arq_settings import WorkerSettings, process_cv_job

__all__ = ["WorkerSettings", "process_cv_job"]
