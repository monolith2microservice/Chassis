from datetime import datetime

def utc_now():
    """Returns current UTC time in ISO format."""
    return datetime.utcnow().isoformat()
