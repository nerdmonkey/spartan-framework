from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, Optional


class BaseTracer(ABC):
    """Base class for tracer implementations."""

    @abstractmethod
    def capture_lambda_handler(self, handler):
        """
        Decorator for tracing Lambda/Cloud Function handlers.

        Args:
            handler: The handler function to trace

        Returns:
            Wrapped handler function with tracing
        """

    @abstractmethod
    def capture_method(self, method):
        """
        Decorator for tracing class methods.

        Args:
            method: The method to trace

        Returns:
            Wrapped method with tracing
        """

    @abstractmethod
    @contextmanager
    def create_segment(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for creating trace segments/spans.

        Args:
            name: Name of the segment
            metadata: Optional metadata to attach to the segment

        Yields:
            The created segment/span object (implementation-specific)
        """

    @contextmanager
    def create_subsegment(self, name: str):
        """
        Context manager for creating trace subsegments/child spans.

        Default implementation creates a regular segment. Subclasses can override
        for specific subsegment behavior.

        Args:
            name: Name of the subsegment

        Yields:
            The created subsegment/span object (implementation-specific)
        """
        with self.create_segment(name) as segment:
            yield segment
