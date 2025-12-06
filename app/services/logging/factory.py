import os
from typing import Dict, List, Optional, Type

from app.helpers.environment import env
from app.services.logging.both import BothLogger
from app.services.logging.file import FileLogger
from app.services.logging.stream import StreamLogger

from .base import BaseLogger


class LoggerFactory:
    """
    Factory class for creating different types of loggers with lazy
    loading support.
    """

    # Cache for lazy-loaded logger classes
    _lazy_logger_cache: Dict[str, Type[BaseLogger]] = {}

    # Registry of available logger types
    _logger_registry = {
        "stream": StreamLogger,
        "file": FileLogger,
        "both": BothLogger,
        # gcloud is handled separately due to lazy loading
    }

    @classmethod
    def _get_gcloud_logger(cls) -> Type[BaseLogger]:
        """Lazy loader for Google Cloud Logger to avoid dependency conflicts."""
        if "gcloud" not in cls._lazy_logger_cache:
            from app.services.logging.gcloud import GCloudLogger

            cls._lazy_logger_cache["gcloud"] = GCloudLogger
        return cls._lazy_logger_cache["gcloud"]

    @classmethod
    def _is_gcp_environment(cls) -> bool:
        """Detect if running in Google Cloud Platform environment."""
        # Check for Google Cloud environment indicators
        return any(
            [
                env("GOOGLE_CLOUD_PROJECT"),
                env("GCLOUD_PROJECT"),
                env("GCP_PROJECT"),
                env("GOOGLE_APPLICATION_CREDENTIALS"),
                # Check for Cloud Run metadata server
                os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount")
                and env("K_SERVICE"),  # Cloud Run indicator
                # Check for App Engine
                env("GAE_APPLICATION"),
                # Check for Compute Engine
                (
                    os.path.exists("/sys/class/dmi/id/product_name")
                    and "Google"
                    in open("/sys/class/dmi/id/product_name", "r").read().strip()
                    if os.path.exists("/sys/class/dmi/id/product_name")
                    else False
                ),
            ]
        )

    @classmethod
    def _resolve_logger_type(cls, logger_type: Optional[str]) -> str:
        """
        Resolve the logger type from parameters or environment variables
        with smart fallback.
        """
        resolved_type = (
            logger_type or env("LOGGER_TYPE", env("LOG_CHANNEL", "file"))
        ).lower()

        # Smart fallback: if gcloud is requested but we're not in GCP environment,
        # and no explicit override, fall back to 'both' for local development
        if resolved_type == "gcloud" and not cls._is_gcp_environment():
            app_env = env("APP_ENVIRONMENT", "").lower()
            if app_env in ["local", "development", "dev"]:
                print(
                    f"⚠️  Warning: gcloud logger requested in {app_env} "
                    f"environment. Falling back to 'both' logger."
                )
                return "both"

        return resolved_type

    @classmethod
    def _get_logger_params(
        cls, service_name: str, level: str, logger_type: str
    ) -> Dict:
        """Get common parameters for logger initialization."""
        base_params = {"service_name": service_name, "level": level}

        # Add sample_rate for loggers that support it
        if logger_type in ["file", "gcloud", "both"]:
            base_params["sample_rate"] = float(env("LOG_SAMPLE_RATE", "1.0"))

        return base_params

    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of all supported logger types."""
        return list(cls._logger_registry.keys()) + ["gcloud"]

    @classmethod
    def create_logger(
        cls,
        service_name: str,
        level: str = "INFO",
        logger_type: Optional[str] = None,
    ) -> BaseLogger:
        """
        Create a logger instance based on the specified type.

        Args:
            service_name: Name of the service for logging identification
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            logger_type: Type of logger to create (stream, file, gcloud, both)

        Returns:
            BaseLogger: Configured logger instance

        Raises:
            ValueError: If logger_type is not supported
            ImportError: If required dependencies for the logger type are not available
        """
        resolved_type = cls._resolve_logger_type(logger_type)
        params = cls._get_logger_params(service_name, level, resolved_type)

        # Handle regular logger types
        if resolved_type in cls._logger_registry:
            logger_class = cls._logger_registry[resolved_type]
            return logger_class(**params)

        # Handle lazy-loaded logger types
        elif resolved_type == "gcloud":
            logger_class = cls._get_gcloud_logger()
            return logger_class(**params)

        # Unknown logger type
        else:
            supported_types = ", ".join([f"'{t}'" for t in cls.get_supported_types()])
            raise ValueError(
                f"Unknown logger_type: '{resolved_type}'. "
                f"Must be one of: {supported_types}."
            )
