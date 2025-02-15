import os
from functools import lru_cache
from typing import Optional

from .base import BaseTracer
from .cloud import CloudTracer
from .local import LocalTracer


class TracerFactory:
    @staticmethod
    def create_tracer(service_name: Optional[str] = None) -> BaseTracer:
        environment = os.getenv("APP_ENVIRONMENT", "local").lower()
        service = service_name or os.getenv("APP_NAME", "default-service")

        if environment == "local":
            return LocalTracer(service)
        return CloudTracer(service)


@lru_cache
def get_tracer(service_name: Optional[str] = None) -> BaseTracer:
    return TracerFactory.create_tracer(service_name)
