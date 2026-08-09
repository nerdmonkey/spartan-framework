from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, Optional


class BaseTracer(ABC):
    @abstractmethod
    def capture_lambda_handler(self, handler):
        pass

    def capture_handler(self, handler):
        """Runtime-agnostic alias for capture_lambda_handler.

        Serverless callers can keep using capture_lambda_handler; container/
        microservice callers should use this name instead.
        """
        return self.capture_lambda_handler(handler)

    @abstractmethod
    def capture_method(self, method):
        pass

    @abstractmethod
    @contextmanager
    def create_segment(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        pass
