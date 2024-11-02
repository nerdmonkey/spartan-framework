from logging import FileHandler

from aws_lambda_powertools.logging import Logger

from app.helpers.logs.base import BaseLogger
from app.helpers.logs.formatter.file import FileLogFormatter
from config.logging import handler


class FileLogger(BaseLogger):
    def __init__(self):
        self.logger = Logger(
            service=handler.file.name,
            level=handler.file.level,
            formatter=FileLogFormatter(),
            logger_handler=FileHandler(handler.file.path),
            json_deserializer=handler.file.json_deserializer,
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
