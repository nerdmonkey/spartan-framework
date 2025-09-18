# Simple re-export from factory
from app.helpers.environment import env

from .factory import LoggerFactory


def get_logger(service_name: str = None):
    """Simple helper to get logger instance."""
    if not service_name:
        service_name = "spartan-framework"

    log_level = env("LOG_LEVEL") or "INFO"
    return LoggerFactory.create_logger(service_name, log_level)
