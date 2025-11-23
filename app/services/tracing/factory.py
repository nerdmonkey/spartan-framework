from functools import lru_cache
from typing import Optional

from app.helpers.environment import env

from .base import BaseTracer
from .cloud import CloudTracer
from .local import LocalTracer
from .gcloud import GCloudTracer


class TracerFactory:
    @staticmethod
    def create_tracer(service_name: Optional[str] = None) -> BaseTracer:
        environment = str(env("APP_ENVIRONMENT", "local")).lower()
        service = service_name or env("APP_NAME", "default-service")

        service = validate_service_name(service)

        if environment == "local":
            return LocalTracer(service)

        # Detect GCP environment similar to logger factory heuristics
        def _is_gcp_environment() -> bool:
            return any([
                env('GOOGLE_CLOUD_PROJECT'),
                env('GCLOUD_PROJECT'),
                env('GCP_PROJECT'),
                env('GOOGLE_APPLICATION_CREDENTIALS'),
                env('GAE_APPLICATION'),
                env('K_SERVICE'),
            ])

        if _is_gcp_environment():
            return GCloudTracer(service)

        return CloudTracer(service)


def validate_service_name(service_name):
    """Validate service name"""
    if not service_name or not service_name.strip():
        raise ValueError("Invalid service name")
    return service_name.strip()


@lru_cache
def get_tracer(service_name: Optional[str] = None) -> BaseTracer:
    return TracerFactory.create_tracer(service_name)
