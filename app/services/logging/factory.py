import os
from typing import Optional

from app.helpers.environment import env
from app.services.logging.both import BothLogger
from app.services.logging.cloud import CloudWatchLogger
from app.services.logging.file import FileLogger
from app.services.logging.stream import StreamLogger

from .base import BaseLogger


class LoggerFactory:
    @staticmethod
    def create_logger(
        service_name: str,
        level: str = "INFO",
        logger_type: Optional[str] = None,
    ) -> BaseLogger:
        logger_type = (
            logger_type
            or env("LOGGER_TYPE", env("LOG_CHANNEL", "file"))
        ).lower()

        # Get sample rate from environment using env helper
        sample_rate = float(env("LOG_SAMPLE_RATE", "1.0"))

        if logger_type == "stream":
            return StreamLogger(service_name=service_name, level=level)
        elif logger_type == "file":
            return FileLogger(service_name=service_name, level=level, sample_rate=sample_rate)
        elif logger_type == "cloud":
            return CloudWatchLogger(service_name=service_name, level=level, sample_rate=sample_rate)
        elif logger_type == "both":
            return BothLogger(service_name=service_name, level=level, sample_rate=sample_rate)
        else:
            raise ValueError(
                f"Unknown logger_type: {logger_type}. Must be 'file', 'stream', 'cloud', or 'both'."
            )
