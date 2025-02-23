from contextlib import contextmanager
from functools import wraps
from time import time
from typing import Any, Dict, Optional

from aws_lambda_powertools import Tracer
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.context import Context
from aws_xray_sdk.core.models.segment import Segment
from aws_xray_sdk.core.models.subsegment import Subsegment

from .base import BaseTracer


class CloudTracer(BaseTracer):
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.tracer = xray_recorder
        self.tracer.configure(service=service_name, context=Context())

    def capture_lambda_handler(self, handler):
        @wraps(handler)
        def wrapper(event, context):
            start_time = time()
            with self.tracer.in_subsegment(handler.__name__):
                self.tracer.put_annotation("service", self.service_name)
                try:
                    result = handler(event, context)
                    end_time = time()
                    processing_time = end_time - start_time
                    self.tracer.put_annotation(
                        "processing_time", processing_time
                    )
                    return result
                except Exception as e:
                    end_time = time()
                    processing_time = end_time - start_time
                    self.tracer.put_annotation(
                        "processing_time", processing_time
                    )
                    raise e

        return wrapper

    def capture_method(self, method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            start_time = time()
            with self.tracer.in_subsegment(method.__name__):
                self.tracer.put_annotation("service", self.service_name)
                try:
                    result = method(*args, **kwargs)
                    end_time = time()
                    processing_time = end_time - start_time
                    self.tracer.put_annotation(
                        "processing_time", processing_time
                    )
                    return result
                except Exception as e:
                    end_time = time()
                    processing_time = end_time - start_time
                    self.tracer.put_annotation(
                        "processing_time", processing_time
                    )
                    raise e

        return wrapper

    @contextmanager
    def create_segment(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ):
        start_time = time()
        segment = self.tracer.begin_segment(name)
        if metadata:
            segment.put_metadata("metadata", metadata)
        try:
            yield segment
        except Exception as e:
            end_time = time()
            processing_time = end_time - start_time
            segment.put_annotation("error", str(e))
            segment.put_annotation("processing_time", processing_time)
            raise
        else:
            end_time = time()
            processing_time = end_time - start_time
            segment.put_annotation("processing_time", processing_time)
        finally:
            self.tracer.end_segment()

    @contextmanager
    def create_subsegment(self, name: str):
        start_time = time()
        subsegment = self.tracer.begin_subsegment(name)
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
        finally:
            self.tracer.end_subsegment()
