from app.helpers.environment import env
from app.helpers.logger.factory import LoggerFactory


def get_logger(service_name: str = None):
    if not service_name:
        service_name = "spartan-framework"

    log_level = env("LOG_LEVEL") or "INFO"

    return LoggerFactory.create_logger(service_name, log_level)
