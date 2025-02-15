from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from contextlib import contextmanager

class BaseTracer(ABC):
    @abstractmethod
    def capture_lambda_handler(self, handler):
        pass

    @abstractmethod
    def capture_method(self, method):
        pass

    @abstractmethod
    @contextmanager
    def create_segment(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        pass
