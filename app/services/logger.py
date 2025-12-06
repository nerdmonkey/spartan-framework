from functools import lru_cache

from app.helpers.environment import env
from app.services.logging.factory import LoggerFactory


class LoggerService:
    """Centralized logger service for the application."""

    @staticmethod
    @lru_cache(maxsize=128)
    def get_logger(service_name: str = None):
        """Get cached logger instance for the given service name."""
        if not service_name:
            service_name = "spartan-framework-lazaro"

        log_level = env("LOG_LEVEL") or "INFO"
        return LoggerFactory.create_logger(service_name, log_level)


def get_logger(service_name: str = None):
    """Simple helper to get logger instance."""
    return LoggerService.get_logger(service_name)
