from typing import Optional, Dict, Any
from aws_lambda_powertools import Tracer
from contextlib import contextmanager
from .base import BaseTracer

class CloudTracer(BaseTracer):
    def __init__(self, service_name: str):
        self.tracer = Tracer(service=service_name)

    def capture_lambda_handler(self, handler):
        return self.tracer.capture_lambda_handler(handler)

    def capture_method(self, method):
        return self.tracer.capture_method(method)

    @contextmanager
    def create_segment(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        with self.tracer.provider.in_subsegment(name=name) as subsegment:
            if metadata:
                subsegment.put_metadata("metadata", metadata)
            try:
                yield subsegment
            except Exception as e:
                subsegment.put_annotation("error", str(e))
                raise
