from app.helpers.environment import env
from app.helpers.logger.factory import LoggerFactory


def get_logger(service_name: str):
    environment = env("APP_ENVIRONMENT").lower()
    log_level = env("LOG_LEVEL") or "INFO"
    return LoggerFactory.create_logger(service_name, environment, log_level)
