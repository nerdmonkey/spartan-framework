import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from .base import BaseLogger


class FileLogger(BaseLogger):
    def __init__(
        self,
        service_name: str,
        level: str = "INFO",
        log_dir: str = "storage/logs",
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
    ):
        self.service_name = service_name
        self.logger = self._setup_logger(service_name, level, log_dir, max_bytes, backup_count)

    def _setup_logger(
        self, service_name: str, level: str, log_dir: str, max_bytes: int, backup_count: int
    ) -> logging.Logger:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger(f"{service_name}_file")
        logger.setLevel(level)

        logger.handlers = []

        file_handler = RotatingFileHandler(
            f"{log_dir}/spartan.log", maxBytes=max_bytes, backupCount=backup_count
        )

        class JsonFormatter(logging.Formatter):
            def format(self, record):

                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "service": service_name,
                    "message": record.getMessage(),
                    "location": f"{record.filename}:{record.lineno}",
                }

                if record.exc_info:
                    log_entry["exception"] = self.formatException(record.exc_info)

                if hasattr(record, "extra"):
                    log_entry.update(record.extra)

                return json.dumps(log_entry)

        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        return logger

    def _log(self, level: str, message: str, **kwargs):
        log_method = getattr(self.logger, level.lower())
        log_method(message, extra=kwargs)

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)

    def exception(self, message: str, **kwargs):
        self.logger.exception(message, extra=kwargs)

    def inject_lambda_context(self, func):
        def wrapper(event, context):
            return func(event, context)
        return wrapper
