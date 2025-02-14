from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths

from .base import BaseLogger


class CloudWatchLogger(BaseLogger):
    def __init__(self, service_name: str, level: str = "INFO"):
        self.logger = Logger(
            service=service_name,
            level=level,
            correlation_id_path=correlation_paths.API_GATEWAY_REST,
            use_rfc3339=True,
        )

    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)

    def exception(self, message: str, **kwargs):
        self.logger.exception(message, extra=kwargs)

    def inject_lambda_context(self, *args, **kwargs):
        """Decorator to inject lambda context"""
        return self.logger.inject_lambda_context(*args, **kwargs)
