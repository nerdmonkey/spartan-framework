from contextlib import contextmanager

from aws_xray_sdk.core import xray_recorder


class CloudTracer:
    def __init__(self, service_name):
        self.service_name = service_name
        self.tracer = xray_recorder

    def capture_lambda_handler(self, func):
        def wrapper(event, context):
            self.tracer.put_annotation("service", self.service_name)
            self.tracer.put_annotation("handler", func.__name__)
            return func(event, context)

        return wrapper

    def capture_method(self, func):
        def wrapper(instance, *args, **kwargs):
            self.tracer.put_annotation("service", self.service_name)
            self.tracer.put_annotation("method", func.__name__)
            return func(instance, *args, **kwargs)

        return wrapper

    @contextmanager
    def create_segment(self, name):
        try:
            self.tracer.begin_segment(name)
            yield
        finally:
            self.tracer.end_segment()

    @contextmanager
    def create_subsegment(self, name):
        try:
            self.tracer.begin_subsegment(name)
            yield
        finally:
            self.tracer.end_subsegment()
