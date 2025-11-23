import inspect
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any

from app.helpers.environment import env
from .base import BaseTracer

try:
    from google.cloud import trace_v1
    GCP_TRACING_AVAILABLE = True
except Exception as e:  # pragma: no cover - availability depends on env
    GCP_TRACING_AVAILABLE = False
    _IMPORT_ERROR = e


class GCloudTracer(BaseTracer):
    """Google Cloud tracer (lightweight wrapper)."""

    def __init__(self, service_name: str):
        if not GCP_TRACING_AVAILABLE:
            error_msg = "Google Cloud Tracing dependencies not available."
            if hasattr(globals(), "_IMPORT_ERROR"):
                error_msg += f" Error: {_IMPORT_ERROR}"
            else:
                error_msg += " Install with: pip install google-cloud-trace"
            raise ImportError(error_msg)

        self.service_name = service_name
        # create a client; tests can monkeypatch trace_v1
        self.client = trace_v1.TraceServiceClient()

    def capture_lambda_handler(self, func):
        def wrapper(event, context):
            # lightweight: annotate via client if available
            try:
                if hasattr(self.client, "patch_traces"):
                    # noop payload; real implementation would push spans
                    pass
            except Exception:
                pass
            return func(event, context)

        return wrapper

    def capture_method(self, func):
        def wrapper(instance, *args, **kwargs):
            try:
                if hasattr(self.client, "patch_traces"):
                    pass
            except Exception:
                pass
            return func(instance, *args, **kwargs)

        return wrapper

    @contextmanager
    def create_segment(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        # Real implementation would start and end spans; here we provide a context manager
        try:
            yield
        finally:
            pass

    @contextmanager
    def create_subsegment(self, name: str):
        try:
            yield
        finally:
            pass
