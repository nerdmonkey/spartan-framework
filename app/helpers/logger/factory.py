import os
from typing import Optional

from app.helpers.logger.cloud import CloudWatchLogger
from app.helpers.logger.file import FileLogger
from app.helpers.logger.stream import StreamLogger
from app.helpers.logger.both import BothLogger

from .base import BaseLogger


class LoggerFactory:
    @staticmethod
    def create_logger(
        service_name: str,
        level: str = "INFO",
        logger_type: Optional[str] = None,
    ) -> BaseLogger:
        logger_type = logger_type or os.getenv("LOGGER_TYPE", os.getenv("LOG_CHANNEL", "file")).lower()

        if logger_type == "stream":
            return StreamLogger(service_name=service_name, level=level)
        elif logger_type == "file":
            return FileLogger(service_name=service_name, level=level)
        elif logger_type == "cloud":
            return CloudWatchLogger(service_name=service_name, level=level)
        elif logger_type == "both":
            return BothLogger(service_name=service_name, level=level)
        else:
            raise ValueError(f"Unknown logger_type: {logger_type}. Must be 'file', 'stream', 'cloud', or 'both'.")
