import logging
from .config import settings

def setup_logging():
    """Configure default logging format and level."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format=f"%(asctime)s | {settings.SERVICE_NAME} | %(levelname)s | %(name)s | %(message)s"
    )
    return logging.getLogger(settings.SERVICE_NAME)
