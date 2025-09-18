from app.services.logger import LoggerService


def get_logger(service_name: str = None):
    """Simple helper to get logger instance."""
    return LoggerService.get_logger(service_name)
