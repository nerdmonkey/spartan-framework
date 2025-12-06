"""
Google Cloud Logging implementation following GCP best practices.

Key improvements:
1. Direct logging client instead of Python logging handler
2. Proper structured logging with jsonPayload
3. Cloud Trace context integration
4. Resource labels for Cloud Run/Functions
5. Error Reporting integration
6. Efficient resource usage with shared client
"""

import inspect
import os
from functools import lru_cache
from typing import Any, Dict, Optional

from app.helpers.environment import env

from .base import BaseLogger


try:
    from google.cloud import logging as gcp_logging
    from google.cloud.logging_v2 import Resource

    GCP_LOGGING_AVAILABLE = True
except (ImportError, TypeError, AttributeError) as e:
    GCP_LOGGING_AVAILABLE = False
    _IMPORT_ERROR = e

    # Create dummy Resource class for type hints when GCP is not available
    class Resource:
        def __init__(self, *args, **kwargs):
            pass


# Shared client for all loggers (best practice for performance)
@lru_cache(maxsize=1)
def get_gcp_logging_client():
    """Get or create shared GCP logging client."""
    if not GCP_LOGGING_AVAILABLE:
        return None
    try:
        return gcp_logging.Client()
    except Exception:
        return None


class GCloudLogger(BaseLogger):
    """
    Google Cloud Logging implementation following GCP best practices.

    Features:
    - Structured logging with jsonPayload
    - Automatic trace context from Cloud Run/Functions
    - Proper severity levels (DEFAULT, DEBUG, INFO, NOTICE, WARNING, ERROR,
      CRITICAL, ALERT, EMERGENCY)
    - Resource labels for service identification
    - Source location for debugging
    - PII sanitization
    - Efficient batching
    """

    # GCP standard severity levels
    SEVERITY_MAPPING = {
        "debug": "DEBUG",
        "info": "INFO",
        "warning": "WARNING",
        "error": "ERROR",
        "critical": "CRITICAL",
        "exception": "ERROR",
    }

    def __init__(
        self,
        service_name: str,
        level: str = "INFO",
        sample_rate: float = None,
    ):
        self.service_name = service_name
        self.sample_rate = (
            sample_rate
            if sample_rate is not None
            else float(env("LOG_SAMPLE_RATE", "1.0"))
        )
        self.level = level.upper()

        # Sensitive fields for PII sanitization
        self._sensitive_fields = {
            "password",
            "token",
            "secret",
            "key",
            "auth",
            "credentials",
            "api_key",
            "access_token",
            "refresh_token",
            "private_key",
            "authorization",
            "cookie",
            "session",
        }

        # Get project root for source location
        self.project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../..")
        )

        # Initialize GCP logging
        self.client = get_gcp_logging_client()
        if self.client:
            # Use structured logger (not Python logging handler)
            self.logger = self.client.logger(service_name)
            self.use_gcp = True
        else:
            # Fallback to print for local development
            self.logger = None
            self.use_gcp = False
            print(
                f"Warning: GCP Logging not available, using fallback for {service_name}"
            )

        # Get resource information for Cloud Run/Functions
        self.resource = self._get_resource()

    def _get_resource(self) -> Optional[Resource]:
        """
        Get GCP resource information for proper log attribution.

        Cloud Run/Functions automatically set environment variables that
        identify the resource. This ensures logs are properly grouped in
        Cloud Logging.
        """
        if not self.use_gcp:
            return None

        # Cloud Run environment variables
        service = env("K_SERVICE")  # Cloud Run service name
        revision = env("K_REVISION")  # Cloud Run revision
        configuration = env("K_CONFIGURATION")

        # Cloud Functions environment variables
        function_name = env("FUNCTION_NAME")
        function_region = env("FUNCTION_REGION")

        if service:
            # Cloud Run resource
            return Resource(
                type="cloud_run_revision",
                labels={
                    "service_name": service,
                    "revision_name": revision or "unknown",
                    "configuration_name": configuration or service,
                    "location": env("FUNCTION_REGION", "us-central1"),
                },
            )
        elif function_name:
            # Cloud Functions resource
            return Resource(
                type="cloud_function",
                labels={
                    "function_name": function_name,
                    "region": function_region or "us-central1",
                },
            )
        else:
            # Generic compute resource
            return Resource(
                type="global",
                labels={},
            )

    def _get_trace_context(self) -> Optional[str]:
        """
        Extract trace context from Cloud Run/Functions headers.

        Format: projects/PROJECT_ID/traces/TRACE_ID
        This enables automatic correlation with Cloud Trace.
        """
        # In Cloud Run/Functions, trace context is in X-Cloud-Trace-Context header
        # Format: TRACE_ID/SPAN_ID;o=TRACE_TRUE
        trace_header = env("HTTP_X_CLOUD_TRACE_CONTEXT")
        if not trace_header:
            return None

        try:
            trace_id = trace_header.split("/")[0]
            project_id = env("GCP_PROJECT") or env("GOOGLE_CLOUD_PROJECT")
            if project_id and trace_id:
                return f"projects/{project_id}/traces/{trace_id}"
        except Exception:
            pass

        return None

    def _get_source_location(self) -> Dict[str, Any]:
        """
        Get source location following GCP's sourceLocation format.

        Returns:
            Dict with file, line, and function for Cloud Logging
        """
        stack = inspect.stack()
        for frame_info in stack:
            filename = frame_info.filename
            normalized_path = filename.replace("\\", "/")

            # Skip logging framework files
            if any(
                skip in normalized_path
                for skip in [
                    "/services/logging/",
                    "/helpers/logger.py",
                    "/logging/",
                    "site-packages/",
                ]
            ):
                continue

            if filename.startswith(self.project_root):
                try:
                    rel_path = os.path.relpath(filename, self.project_root)
                    return {
                        "file": rel_path,
                        "line": str(frame_info.lineno),
                        "function": frame_info.function or "unknown",
                    }
                except (ValueError, OSError):
                    pass

        return {
            "file": "unknown",
            "line": "0",
            "function": "unknown",
        }

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitize sensitive data.

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary with sensitive values redacted
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            if key.lower() in self._sensitive_fields:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    def _should_sample(self) -> bool:
        """Determine if log should be written based on sample rate."""
        import random

        return random.random() <= self.sample_rate

    def _create_log_entry(
        self,
        severity: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> Dict[str, Any]:
        """
        Create structured log entry following GCP format.

        Uses jsonPayload structure that GCP understands natively.
        """
        # Sanitize extra data
        sanitized_extra = self._sanitize_data(extra or {})

        # Build json_payload following GCP conventions
        json_payload = {
            "message": message,
            "service": self.service_name,
            "environment": env("APP_ENVIRONMENT", "unknown"),
            "version": env("APP_VERSION", "unknown"),
            **sanitized_extra,  # Merge user-provided fields
        }

        # Build structured log entry
        log_entry = {
            "severity": severity,
            "json_payload": json_payload,
        }

        # Add source location (helps with debugging)
        source_location = self._get_source_location()
        if source_location["file"] != "unknown":
            log_entry["source_location"] = source_location

        # Add trace context (enables distributed tracing)
        trace = self._get_trace_context()
        if trace:
            log_entry["trace"] = trace

        # Add resource (Cloud Run/Functions metadata)
        if self.resource:
            log_entry["resource"] = self.resource

        # Add labels for filtering/grouping
        log_entry["labels"] = {
            "service": self.service_name,
            "environment": env("APP_ENVIRONMENT", "production"),
        }

        return log_entry

    def _write_log(
        self,
        severity: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        """Write log entry to GCP or fallback."""
        # Apply sampling
        if not self._should_sample():
            return

        if self.use_gcp and self.logger:
            # Use GCP structured logging
            log_entry = self._create_log_entry(severity, message, extra, exc_info)

            try:
                # Write structured log directly
                self.logger.log_struct(
                    log_entry["json_payload"],
                    severity=log_entry["severity"],
                    resource=log_entry.get("resource"),
                    labels=log_entry.get("labels"),
                    trace=log_entry.get("trace"),
                    source_location=log_entry.get("source_location"),
                )
            except Exception as e:
                # Fallback if GCP logging fails
                print(f"[{severity}] {message} | extra: {extra} | error: {e}")
        else:
            # Fallback - print direct JSON payload (GCP best practice)
            sanitized_extra = self._sanitize_data(extra or {})
            json_payload = {
                "message": message,
                "service": self.service_name,
                "environment": env("APP_ENVIRONMENT", "unknown"),
                "version": env("APP_VERSION", "unknown"),
                **sanitized_extra,
            }
            import json

            print(json.dumps(json_payload, default=str))

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        extra = kwargs.get("extra")
        self._write_log("DEBUG", message, extra)

    def info(self, message: str, **kwargs):
        """Log info message."""
        extra = kwargs.get("extra")
        self._write_log("INFO", message, extra)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        extra = kwargs.get("extra")
        self._write_log("WARNING", message, extra)

    def error(self, message: str, **kwargs):
        """Log error message."""
        extra = kwargs.get("extra")
        self._write_log("ERROR", message, extra)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        extra = kwargs.get("extra")
        self._write_log("CRITICAL", message, extra)

    def exception(self, message: str, **kwargs):
        """
        Log exception with traceback.

        This integrates with Error Reporting when exc_info is available.
        """
        extra = kwargs.get("extra")

        # Get exception info
        import sys

        exc_info = sys.exc_info()

        # Add exception details to extra
        if exc_info[0] is not None:
            if extra is None:
                extra = {}
            extra["exception"] = {
                "type": exc_info[0].__name__,
                "message": str(exc_info[1]),
            }

        self._write_log("ERROR", message, extra, exc_info=True)
