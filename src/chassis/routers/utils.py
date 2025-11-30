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
            "total": f"{mem.total / 1000000} MB",
            "available": f"{mem.available / 1000000} MB",
            "used": f"{mem.used / 1000000} MB",
            "percent": mem.percent,
        },
        "disk": {
            "total": f"{disk.total / 1000000} MB",
            "used": f"{disk.used / 1000000} MB",
            "free": f"{disk.free / 1000000} MB",
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