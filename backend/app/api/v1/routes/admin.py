"""Admin endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/faiss/build",
    summary="Trigger FAISS index rebuild",
)
async def rebuild_faiss_index() -> dict:
    """Trigger a background rebuild of the FAISS index from completed jobs.

    TODO: Implement actual FAISS index building logic.
    """
    # TODO: Implement FAISS rebuild
    # - Query completed jobs from repository
    # - Generate embeddings for CV text
    # - Build FAISS index
    # - Persist to disk
    return {
        "status": "triggered",
        "message": "FAISS rebuild started in background",
    }
