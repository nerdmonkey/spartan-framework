import os
import logging
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter
from config.app import get_settings


settings = get_settings()

APP_NAME = settings.APP_NAME
LOG_LEVEL = settings.LOG_LEVEL
LOG_FILE_PATH = settings.LOG_FILE
APP_ENVIRONMENT = settings.APP_ENVIRONMENT

class StandardLogFormatter(LambdaPowertoolsFormatter):
    def format(self, record):
        return super().format(record)

class StandardLoggerService:
    def __init__(self):
        environment = os.getenv("ENV", "dev")

        if environment in ["local", "test"]:
            log_file_path = LOG_FILE_PATH
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

            logging.basicConfig(
                filename=log_file_path,
                level=LOG_LEVEL,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            self.logger = logging.getLogger(APP_NAME)
        else:
            self.logger = Logger(
                service=APP_NAME, level=LOG_LEVEL, formatter=StandardLogFormatter()
            )

    def debug(self, message, **kwargs):
        self.logger.debug(message, **kwargs)

    def info(self, message, **kwargs):
        self.logger.info(message, **kwargs)

    def warning(self, message, **kwargs):
        self.logger.warning(message, **kwargs)

    def error(self, message, **kwargs):
        self.logger.error(message, **kwargs)

    def critical(self, message, **kwargs):
        self.logger.critical(message, **kwargs)

    def exception(self, message, **kwargs):
        self.logger.exception(message, **kwargs)
