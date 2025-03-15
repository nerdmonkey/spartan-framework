from typing import Optional

from app.helpers.environment import env
from app.helpers.logger.cloud import CloudWatchLogger
from app.helpers.logger.file import FileLogger

from .base import BaseLogger


class LoggerFactory:
    @staticmethod
    def create_logger(
        service_name: str,
        environment: Optional[str] = None,
        level: str = "INFO",
    ) -> BaseLogger:

        if env("APP_ENVIRONMENT") == "local":
            return FileLogger(service_name=service_name, level=level)
        else:
            return CloudWatchLogger(service_name=service_name, level=level)
