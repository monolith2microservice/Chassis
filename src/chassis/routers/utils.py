from fastapi import HTTPException
import psutil
import logging

def get_system_metrics() -> dict:
    cpu_percent = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    metrics = {
        "cpu_percent": cpu_percent,
        "memory": {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }
    }

    return metrics

def raise_and_log_error(
    logger: logging.Logger,
    status_code: int,
    message: str
) -> None:
    """Raises HTTPException and logs an error."""
    logger.error(message)
    raise HTTPException(status_code, message)