from aws_lambda_powertools.logging import Logger

from app.helpers.logs.base import BaseLogger
from app.helpers.logs.formatter.standard import StandardLogFormatter
from app.helpers.environment import env


class ConsoleLogger(BaseLogger):
    def __init__(self):
        self.logger = Logger(
            service=env().APP_NAME,
            level=env().LOG_LEVEL,
            formatter=StandardLogFormatter(),
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
