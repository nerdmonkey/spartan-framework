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

        service = validate_service_name(service)

        if environment == "local":
            return LocalTracer(service)
        return CloudTracer(service)


def validate_service_name(service_name):
    """Validate service name"""
    if not service_name or not service_name.strip():
        raise ValueError("Invalid service name")
    return service_name.strip()


@lru_cache
def get_tracer(service_name: Optional[str] = None) -> BaseTracer:
    return TracerFactory.create_tracer(service_name)
