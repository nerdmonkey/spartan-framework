import inspect
import json
import os
import random
from datetime import datetime, timezone
from typing import Dict, Any

from app.helpers.environment import env
from .base import BaseLogger

try:
    from google.cloud import logging as gcp_logging
    from google.cloud.logging_v2.handlers import CloudLoggingHandler
    import logging
    GCP_LOGGING_AVAILABLE = True
except (ImportError, TypeError, AttributeError) as e:
    GCP_LOGGING_AVAILABLE = False
    _IMPORT_ERROR = e


class GCloudLogger(BaseLogger):
    """Google Cloud Logging implementation with structured JSON logging."""

    def __init__(self, service_name: str, level: str = "INFO", sample_rate: float = None):
        if not GCP_LOGGING_AVAILABLE:
            error_msg = "Google Cloud Logging dependencies not available."
            if hasattr(globals(), '_IMPORT_ERROR'):
                error_msg += f" Error: {_IMPORT_ERROR}"
            else:
                error_msg += " Install with: pip install google-cloud-logging"
            raise ImportError(error_msg)

        self.service_name = service_name
        self.sample_rate = sample_rate or float(env("LOG_SAMPLE_RATE", "1.0"))
        self.level = level

        # Define sensitive field names for PII sanitization
        self._sensitive_fields = {
            'password', 'token', 'secret', 'key', 'auth', 'credentials',
            'api_key', 'access_token', 'refresh_token', 'private_key'
        }

        # Get project root for location tracking
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../..")
        )

        # Initialize Google Cloud Logging
        self._setup_gcp_logger(service_name, level)

    def _setup_gcp_logger(self, service_name: str, level: str):
        """Setup Google Cloud Logging client and handler."""
        try:
            # Initialize the client
            client = gcp_logging.Client()

            # Create a Cloud Logging handler
            handler = CloudLoggingHandler(client, name=service_name)

            # Setup standard Python logger with Cloud Logging handler
            self.logger = logging.getLogger(f"{service_name}_gcloud")
            self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

            # Clear any existing handlers
            self.logger.handlers = []
            self.logger.addHandler(handler)
            self.logger.propagate = False

        except Exception as e:
            # Fallback to standard logging if GCP setup fails
            print(f"Warning: Failed to setup Google Cloud Logging: {e}")
            print("Falling back to standard logging...")

            self.logger = logging.getLogger(f"{service_name}_gcloud_fallback")
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.handlers = []
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
            self.logger.propagate = False

    def _get_caller_location(self) -> str:
        """Get the actual caller location, excluding logging-related files."""
        stack = inspect.stack()
        for frame_info in stack:
            filename = frame_info.filename
            # Only consider frames inside the project root and outside the logging-related directories
            normalized_path = filename.replace("\\", "/")
            rel_normalized = normalized_path.replace(self.project_root.replace("\\", "/"), "")

            # Skip frames from logging-related files
            is_logging_frame = (
                "/services/logging/" in rel_normalized or
                "/helpers/logger.py" in rel_normalized or
                "/logging/" in rel_normalized
            )

            if filename.startswith(self.project_root) and not is_logging_frame:
                try:
                    rel_path = os.path.relpath(filename, self.project_root)
                    return f"{rel_path}:{frame_info.lineno}"
                except (ValueError, OSError):
                    return f"{os.path.basename(filename)}:{frame_info.lineno}"

        # Fallback
        return "unknown:0"

    def _sanitize_extra_data(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize potentially sensitive data from extra fields."""
        if not extra:
            return {}

        sanitized = {}
        for key, value in extra.items():
            if key.lower() in self._sensitive_fields:
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value

        return sanitized

    def _should_sample_log(self) -> bool:
        """Determine if this log should be sampled based on sample rate."""
        return random.random() <= self.sample_rate

    def _create_structured_log(self, level: str, message: str, **kwargs) -> Dict[str, Any]:
        """Create structured log entry for Google Cloud Logging."""
        extra = kwargs.get("extra", {})
        sanitized_extra = self._sanitize_extra_data(extra)

        structured_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": level.upper(),
            "service": self.service_name,
            "message": message,
            "location": self._get_caller_location(),
            "environment": env("APP_ENVIRONMENT", "unknown"),
            "version": env("APP_VERSION", "unknown"),
        }

        # Add sanitized extra data to the structured log
        if sanitized_extra:
            structured_log.update(sanitized_extra)

        return structured_log

    def _log(self, level: str, message: str, **kwargs):
        """Internal logging method with sampling and structured logging."""
        # Apply sampling for high-volume scenarios
        if not self._should_sample_log():
            return

        # Create structured log data
        structured_data = self._create_structured_log(level, message, **kwargs)

        # Log using the appropriate level method
        log_method = getattr(self.logger, level.lower(), self.logger.info)

        # Google Cloud Logging expects structured data as extra parameter
        log_method(message, extra=structured_data)

    def info(self, message: str, **kwargs):
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log("error", message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log("debug", message, **kwargs)

    def exception(self, message: str, **kwargs):
        # Apply sampling for high-volume scenarios
        if not self._should_sample_log():
            return

        # Create structured log data
        structured_data = self._create_structured_log("ERROR", message, **kwargs)

        # Use exception method which includes traceback
        self.logger.exception(message, extra=structured_data)

    def critical(self, message: str, **kwargs):
        self._log("critical", message, **kwargs)
