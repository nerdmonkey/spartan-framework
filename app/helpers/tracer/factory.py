import os
from typing import Optional
from functools import lru_cache
from .local import LocalTracer
from .cloud import CloudTracer
from .base import BaseTracer

class TracerFactory:
    @staticmethod
    def create_tracer(service_name: Optional[str] = None) -> BaseTracer:
        environment = os.getenv('ENVIRONMENT', 'local').lower()
        service = service_name or os.getenv('APP_NAME', 'default-service')

        if environment == 'local':
            return LocalTracer(service)
        return CloudTracer(service)

@lru_cache
def get_tracer(service_name: Optional[str] = None) -> BaseTracer:
    return TracerFactory.create_tracer(service_name)
