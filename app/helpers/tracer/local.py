from typing import Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path
from functools import wraps
from contextlib import contextmanager
from .base import BaseTracer

class LocalTracer(BaseTracer):
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.trace_file = self._get_trace_file_path()
        self._ensure_trace_directory_exists()

    def _get_trace_file_path(self) -> Path:
        base_path = Path(__file__).parent.parent.parent.parent
        return base_path / "storage" / "traces" / "spartan.trace"

    def _ensure_trace_directory_exists(self):
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)

    def _write_trace(self, segment_name: str, metadata: Optional[Dict] = None):
        trace_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": self.service_name,
            "segment": segment_name,
            "metadata": metadata or {}
        }

        with open(self.trace_file, "a") as f:
            f.write(json.dumps(trace_entry) + "\n")

    def capture_lambda_handler(self, handler):
        @wraps(handler)
        def wrapper(event, context):
            self._write_trace("lambda_handler", {"event": event})
            try:
                result = handler(event, context)
                self._write_trace("lambda_handler_response", {"result": result})
                return result
            except Exception as e:
                self._write_trace("lambda_handler_error", {"error": str(e)})
                raise
        return wrapper

    def capture_method(self, method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            self._write_trace(method.__name__)
            try:
                result = method(*args, **kwargs)
                return result
            except Exception as e:
                self._write_trace(f"{method.__name__}_error", {"error": str(e)})
                raise
        return wrapper

    @contextmanager
    def create_segment(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        self._write_trace(name, metadata)
        try:
            yield
        except Exception as e:
            self._write_trace(f"{name}_error", {"error": str(e)})
            raise
