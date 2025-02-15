import os

from app.helpers.logger.factory import LoggerFactory


def get_logger(service_name: str):
    environment = os.getenv("APP_ENVIRONMENT", "local").lower()
    log_level = os.getenv("LOG_LEVEL", "INFO")
    return LoggerFactory.create_logger(service_name, environment, log_level)
