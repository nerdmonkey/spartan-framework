import inspect
import json
import logging
import os
import random
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from app.helpers.environment import env

from .base import BaseLogger


class FileLogger(BaseLogger):
    def __init__(
        self,
        service_name: str,
        level: str = "INFO",
        log_dir: str = env("LOG_DIR", "storage/logs"),
        max_bytes: int = 10485760,  # 10MB
        backup_count: int = 5,
        sample_rate: float = None,
    ):
        self.service_name = service_name
        self.sample_rate = sample_rate or float(env("LOG_SAMPLE_RATE", "1.0"))
        self.logger = self._setup_logger(
            service_name, level, log_dir, max_bytes, backup_count
        )

    def _setup_logger(
        self,
        service_name: str,
        level: str,
        log_dir: str,
        max_bytes: int,
        backup_count: int,
    ) -> logging.Logger:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger(f"{service_name}_file")
        logger.setLevel(level)

        logger.handlers = []

        file_handler = RotatingFileHandler(
            f"{log_dir}/{service_name}.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
        )

        class JsonFormatter(logging.Formatter):
            # Cache project root as class variable for performance
            _project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../..")
            )

            # Define sensitive field names for PII sanitization
            _sensitive_fields = {'password', 'token', 'secret', 'key', 'auth', 'credentials', 'api_key'}

            def format(self, record):
                # Use inspect to find the first frame inside the project, outside the logger package
                stack = inspect.stack()
                rel_path = None
                lineno = None
                for frame_info in stack:
                    filename = frame_info.filename
                    # Only consider frames inside the project root and outside the logging-related directories
                    normalized_path = filename.replace("\\", "/")
                    rel_normalized = normalized_path.replace(self._project_root.replace("\\", "/"), "")

                    # Skip frames from logging-related files
                    is_logging_frame = (
                        "/services/logging/" in rel_normalized or
                        "/helpers/logger.py" in rel_normalized or
                        "/logging/" in rel_normalized
                    )

                    if filename.startswith(self._project_root) and not is_logging_frame:
                        rel_path = os.path.relpath(filename, self._project_root)
                        lineno = frame_info.lineno
                        break
                # Fallback with error resilience
                if not rel_path:
                    try:
                        rel_path = os.path.relpath(record.pathname, self._project_root)
                        lineno = record.lineno
                    except (ValueError, OSError):
                        rel_path = os.path.basename(record.pathname)
                        lineno = record.lineno
                log_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": record.levelname,
                    "service": service_name,
                    "message": record.getMessage(),
                    "location": f"{rel_path}:{lineno}",
                    "environment": env("APP_ENVIRONMENT", "unknown"),
                    "version": env("APP_VERSION", "unknown"),
                }

                if record.exc_info:
                    log_entry["exception"] = self.formatException(
                        record.exc_info
                    )

                # Handle extra data with PII sanitization
                # Python logging adds extra fields as attributes to the record
                record_dict = record.__dict__
                standard_fields = {
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                    'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                    'relativeCreated', 'thread', 'threadName', 'processName',
                    'process', 'message', 'exc_info', 'exc_text', 'stack_info', 'extra'
                }
                for key, value in record_dict.items():
                    if key not in standard_fields:
                        # Sanitize potentially sensitive fields for security
                        if key.lower() in self._sensitive_fields:
                            log_entry[key] = '[REDACTED]'
                        else:
                            log_entry[key] = value

                return json.dumps(log_entry)

        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
        return logger

    def _should_sample_log(self) -> bool:
        """Determine if this log should be sampled based on sample rate."""
        return random.random() <= self.sample_rate

    def _log(self, level: str, message: str, **kwargs):
        # Apply sampling for high-volume scenarios
        if not self._should_sample_log():
            return

        log_method = getattr(self.logger, level.lower())
        extra = kwargs.pop("extra", {})
        stacklevel = kwargs.pop("stacklevel", 1)

        # Python logging expects extra fields as part of the extra dict
        # Pass extra data properly to the logging method
        log_method(message, extra=extra, stacklevel=stacklevel)

    def log(self, message: str, level: str = "INFO", **kwargs):
        """Generic logging entry point.

        This mirrors the behaviour of ``StreamLogger`` allowing ``BothLogger``
        to delegate calls to a common ``log`` method on the underlying loggers.
        ``_log`` handles the actual dispatch to the appropriate logging level
        method.
        """
        self._log(level, message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)

    def exception(self, message: str, **kwargs):
        stacklevel = kwargs.pop("stacklevel", 1)
        self.logger.exception(message, extra=kwargs, stacklevel=stacklevel)

    def critical(self, message: str, **kwargs):
        self._log("critical", message, **kwargs)

    def inject_lambda_context(self, func):
        def wrapper(event, context):
            return func(event, context)

        return wrapper
