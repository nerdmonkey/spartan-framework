from contextlib import contextmanager
from time import time
from typing import Any, Dict, Optional
from functools import wraps

from aws_lambda_powertools import Tracer

from .base import BaseTracer


class CloudTracer(BaseTracer):
    def __init__(self, service_name: str):
        self.tracer = Tracer(service=service_name)

    def capture_lambda_handler(self, handler):
        @wraps(handler)
        def wrapper(event, context):
            start_time = time()
            try:
                result = handler(event, context)
                end_time = time()
                processing_time = end_time - start_time
                self.tracer.put_annotation("processing_time", processing_time)
                return result
            except Exception as e:
                end_time = time()
                processing_time = end_time - start_time
                self.tracer.put_annotation("processing_time", processing_time)
                raise e

        return wrapper

    def capture_method(self, method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            start_time = time()
            try:
                result = method(*args, **kwargs)
                end_time = time()
                processing_time = end_time - start_time
                self.tracer.put_annotation("processing_time", processing_time)
                return result
            except Exception as e:
                end_time = time()
                processing_time = end_time - start_time
                self.tracer.put_annotation("processing_time", processing_time)
                raise e

        return wrapper

    @contextmanager
    def create_segment(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ):
        start_time = time()
        with self.tracer.provider.in_subsegment(name=name) as subsegment:
            if metadata:
                subsegment.put_metadata("metadata", metadata)
            try:
                yield subsegment
            except Exception as e:
                end_time = time()
                processing_time = end_time - start_time
                subsegment.put_annotation("error", str(e))
                subsegment.put_annotation("processing_time", processing_time)
                raise
            else:
                end_time = time()
                processing_time = end_time - start_time
                subsegment.put_annotation("processing_time", processing_time)
