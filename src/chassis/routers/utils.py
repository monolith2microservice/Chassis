from fastapi import HTTPException
import logging

def raise_and_log_error(
    logger: logging.Logger,
    status_code: int,
    message: str
) -> None:
    """Raises HTTPException and logs an error."""
    logger.error(message)
    raise HTTPException(status_code, message)