from fastapi import APIRouter

router = APIRouter()

@router.get("/health", summary="Health check endpoint")
async def health_check():
    """Standard health check endpoint."""
    return {"status": "ok"}
