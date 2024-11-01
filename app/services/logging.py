import json
from logging import FileHandler

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter

from config.app import get_settings

settings = get_settings()

APP_NAME = settings.APP_NAME.lower()
LOG_LEVEL = settings.LOG_LEVEL
LOG_FILE = settings.LOG_FILE
APP_ENVIRONMENT = settings.APP_ENVIRONMENT.lower()


class StandardLogFormatter(LambdaPowertoolsFormatter):
    def format(self, record):
        return super().format(record)


class FileLogFormatter(LambdaPowertoolsFormatter):
    def format(self, record):
        log_entry = super().format(record)
        # return json.dumps(json.loads(log_entry), indent=4)
        return log_entry


class StandardLoggerService:
    def __init__(self):
        if APP_ENVIRONMENT in ["local"]:
            self.logger = Logger(
                service=APP_NAME,
                level=LOG_LEVEL,
                formatter=FileLogFormatter(),
                logger_handler=FileHandler(LOG_FILE),
                json_deserializer=json.loads,
            )
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
