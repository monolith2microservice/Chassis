import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def raise_and_log_error(status_code: int, message: str):
    """Raise HTTPException and log the error message."""
    logger.error(message)
    raise HTTPException(status_code=status_code, detail=message)
